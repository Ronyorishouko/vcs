# -*- coding: utf-8 -*-
import gzip
import io
import json
import stat
from datetime import datetime

from .base import resolve_config, split_time_and_metrics


class SshJsonlCollector(object):
    def collect(self, bot, cursor_data):
        config = resolve_config(bot.source_config)
        time_field = config.get('time_field') or 'time'
        remote_path = config.get('remote_path')
        if not remote_path:
            raise ValueError('У бота %s не задан source_config.remote_path' % bot.slug)
        rotated_glob = config.get('rotated_glob') or (remote_path + '*')

        paramiko = _import_paramiko()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = _load_key(paramiko, config.get('key_path'))
        client.connect(
            hostname=config.get('host'),
            port=int(config.get('port') or 22),
            username=config.get('username'),
            pkey=pkey,
            timeout=int(config.get('connect_timeout') or 20),
            allow_agent=False,
            look_for_keys=False,
        )
        try:
            sftp = client.open_sftp()
            try:
                files = _list_rotated_files(sftp, remote_path, rotated_glob)
                records, new_cursor = _read_files(sftp, files, cursor_data or {}, time_field, remote_path)
            finally:
                sftp.close()
        finally:
            client.close()
        return records, new_cursor


def _import_paramiko():
    try:
        import paramiko
    except ImportError:
        raise RuntimeError('Для сбора по SSH нужен пакет paramiko')
    return paramiko


def _load_key(paramiko, key_path):
    if not key_path:
        raise ValueError('Не задан key_path для SSH')
    errors = []
    for key_cls in (paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey):
        try:
            return key_cls.from_private_key_file(key_path)
        except Exception as exc:
            errors.append('%s: %s' % (key_cls.__name__, exc))
    raise ValueError('Не удалось прочитать SSH-ключ %s (%s)' % (key_path, '; '.join(errors)))


def _list_rotated_files(sftp, remote_path, rotated_glob):
    directory = remote_path.rsplit('/', 1)[0] or '.'
    prefix = remote_path.rsplit('/', 1)[-1]
    glob_name = rotated_glob.rsplit('/', 1)[-1]
    names = sftp.listdir(directory)
    matched = []
    for name in names:
        if name == prefix or _glob_match(glob_name, name) or name.startswith(prefix):
            path = '%s/%s' % (directory.rstrip('/'), name)
            try:
                info = sftp.stat(path)
            except IOError:
                continue
            if stat.S_ISDIR(info.st_mode):
                continue
            matched.append({
                'path': path,
                'mtime': info.st_mtime,
                'size': info.st_size,
            })
    matched.sort(key=lambda item: (item['mtime'], item['path']))
    return matched


def _glob_match(pattern, name):
    if pattern == name:
        return True
    if pattern.endswith('*'):
        return name.startswith(pattern[:-1])
    return False


def _read_files(sftp, files, cursor_data, time_field, current_path):
    last_time = cursor_data.get('last_time')
    last_path = cursor_data.get('last_path')
    last_offset = int(cursor_data.get('last_offset') or 0)
    last_size = int(cursor_data.get('last_size') or 0)
    records = []
    new_offset = last_offset
    new_path = last_path or current_path
    new_size = last_size

    rotated = last_path and (
        last_path not in [item['path'] for item in files]
        or any(item['path'] == last_path and item['size'] < last_offset for item in files)
        or any(item['path'] == last_path and item['size'] < last_size for item in files)
    )

    start_index = 0
    if last_path and not rotated:
        for idx, item in enumerate(files):
            if item['path'] == last_path:
                start_index = idx
                break

    for item in files[start_index:]:
        path = item['path']
        offset = 0
        if path == last_path and not rotated:
            offset = last_offset
        elif last_time and path != last_path:
            offset = 0
        file_records, consumed_offset = _read_one_file(
            sftp, path, offset, time_field, last_time
        )
        records.extend(file_records)
        new_path = path
        new_offset = consumed_offset
        new_size = item['size']
        if file_records:
            last_time = file_records[-1]['occurred_at'].isoformat()

    new_cursor = {
        'last_time': last_time,
        'last_path': new_path,
        'last_offset': new_offset,
        'last_size': new_size,
        'updated_at': datetime.utcnow().isoformat(),
    }
    return records, new_cursor


def _read_one_file(sftp, path, offset, time_field, last_time):
    handle = sftp.open(path, 'rb')
    try:
        if path.endswith('.gz'):
            raw = handle.read()
            payload = gzip.decompress(raw)
            stream = io.BytesIO(payload)
            records, _ignored = _parse_stream(stream, 0, path, time_field, last_time)
            return records, len(raw)

        handle.seek(offset)
        records = []
        buffer = b''
        position = offset
        while True:
            chunk = handle.read(64 * 1024)
            if not chunk:
                break
            buffer += chunk
            while True:
                newline = buffer.find(b'\n')
                if newline < 0:
                    break
                line = buffer[:newline]
                buffer = buffer[newline + 1:]
                position += newline + 1
                record = _parse_line(line, path, position, time_field)
                if record is None:
                    continue
                if last_time and record['occurred_at'].isoformat() <= last_time:
                    continue
                records.append(record)
        return records, position
    finally:
        handle.close()


def _parse_stream(stream, start_offset, path, time_field, last_time):
    records = []
    position = start_offset
    for raw_line in stream:
        position += len(raw_line)
        line = raw_line[:-1] if raw_line.endswith(b'\n') else raw_line
        record = _parse_line(line, path, position, time_field)
        if record is None:
            continue
        if last_time and record['occurred_at'].isoformat() <= last_time:
            continue
        records.append(record)
    return records, position


def _parse_line(line, path, position, time_field):
    text = line.decode('utf-8').strip()
    if not text:
        return None
    try:
        payload = json.loads(text)
        occurred_at, metrics = split_time_and_metrics(payload, time_field)
    except (ValueError, TypeError):
        return None
    return {
        'occurred_at': occurred_at,
        'metrics': metrics,
        'source_ref': '%s:%s' % (path, position),
    }
