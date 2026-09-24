# -*- coding: utf-8 -*-
import copy
import os
import re
from datetime import datetime

from django.utils.dateparse import parse_datetime

ENV_RE = re.compile(r'\$\{([^}]+)\}')


def resolve_config(config):
    data = copy.deepcopy(config or {})

    def walk(value):
        if isinstance(value, dict):
            return {key: walk(item) for key, item in value.items()}
        if isinstance(value, list):
            return [walk(item) for item in value]
        if isinstance(value, str):
            def repl(match):
                name = match.group(1)
                env = os.environ.get(name)
                if env is None:
                    raise ValueError('Не задана переменная окружения %s' % name)
                return env
            return ENV_RE.sub(repl, value)
        return value

    resolved = walk(data)
    password_env = resolved.pop('password_env', None)
    if password_env and not resolved.get('password'):
        env_password = os.environ.get(password_env)
        if env_password is None:
            raise ValueError('Не задана переменная окружения %s' % password_env)
        resolved['password'] = env_password
    key_path_env = resolved.pop('key_path_env', None)
    if key_path_env and not resolved.get('key_path'):
        env_key = os.environ.get(key_path_env)
        if env_key is None:
            raise ValueError('Не задана переменная окружения %s' % key_path_env)
        resolved['key_path'] = env_key
    return resolved


def parse_occurred_at(value):
    if value is None:
        raise ValueError('Пустое время снимка')
    if isinstance(value, datetime):
        return value.replace(tzinfo=None) if value.tzinfo else value
    text = str(value).strip()
    parsed = parse_datetime(text)
    if parsed is None:
        parsed = parse_datetime(text.replace('Z', '+00:00'))
    if parsed is None:
        raise ValueError('Не разобрать время: %s' % value)
    if parsed.tzinfo:
        parsed = parsed.replace(tzinfo=None)
    return parsed


def split_time_and_metrics(payload, time_field='time'):
    if not isinstance(payload, dict):
        raise ValueError('Ожидался JSON-объект')
    if time_field not in payload:
        raise ValueError('Нет поля времени %s' % time_field)
    metrics = dict(payload)
    occurred_at = parse_occurred_at(metrics.pop(time_field))
    return occurred_at, metrics
