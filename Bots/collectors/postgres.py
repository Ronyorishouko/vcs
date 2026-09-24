# -*- coding: utf-8 -*-
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from .base import parse_occurred_at, resolve_config


class PostgresCollector(object):
    def collect(self, bot, cursor_data):
        config = resolve_config(bot.source_config)
        time_field = config.get('time_field') or 'time'
        query = config.get('query')
        if not query:
            raise ValueError('У бота %s не задан source_config.query' % bot.slug)

        since = cursor_data.get('last_time')
        params = {'since': since} if since else {'since': datetime(1970, 1, 1)}

        conn = psycopg2.connect(
            host=config.get('host'),
            port=config.get('port') or 5432,
            dbname=config.get('dbname'),
            user=config.get('user'),
            password=config.get('password') or '',
            connect_timeout=int(config.get('connect_timeout') or 15),
        )
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
        finally:
            conn.close()

        records = []
        last_time = since
        for row in rows:
            payload = dict(row)
            if time_field not in payload:
                raise ValueError('В результате SQL нет поля %s' % time_field)
            occurred_at = parse_occurred_at(payload.pop(time_field))
            source_id = payload.pop(config.get('id_field'), None) if config.get('id_field') else None
            metrics = payload
            records.append({
                'occurred_at': occurred_at,
                'metrics': metrics,
                'source_ref': str(source_id) if source_id is not None else '',
            })
            iso = occurred_at.isoformat()
            if last_time is None or iso > last_time:
                last_time = iso

        new_cursor = dict(cursor_data or {})
        if last_time:
            new_cursor['last_time'] = last_time
        return records, new_cursor
