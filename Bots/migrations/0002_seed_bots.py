# -*- coding: utf-8 -*-
from django.db import migrations

BOTS = [
    {
        'slug': 'appeals-count',
        'name': 'Бот: количество обращений',
        'source_type': 'postgres',
        'source_config': {
            'host': 'CHANGE_ME',
            'port': 5432,
            'dbname': 'CHANGE_ME',
            'user': 'CHANGE_ME',
            'password': '${BOT_APPEALS_DB_PASSWORD}',
            'time_field': 'time',
            'query': (
                "SELECT date_trunc('hour', created_at) AS time, "
                "COUNT(*) AS requests "
                "FROM dialogs "
                "WHERE created_at > %(since)s "
                "GROUP BY 1 "
                "ORDER BY 1"
            ),
        },
        'metric_schema': [
            {'key': 'requests', 'label': 'Обращения', 'type': 'int'},
        ],
    },
    {
        'slug': 'support-handoff',
        'name': 'Бот: обращения / решено / на специалиста',
        'source_type': 'postgres',
        'source_config': {
            'host': 'CHANGE_ME',
            'port': 5432,
            'dbname': 'CHANGE_ME',
            'user': 'CHANGE_ME',
            'password': '${BOT_SUPPORT_DB_PASSWORD}',
            'time_field': 'time',
            'query': (
                "SELECT date_trunc('hour', created_at) AS time, "
                "COUNT(*) AS requests, "
                "COUNT(*) FILTER (WHERE status = 'resolved_by_bot') AS resolved_by_bot, "
                "COUNT(*) FILTER (WHERE status = 'transferred') AS transferred "
                "FROM dialogs "
                "WHERE created_at > %(since)s "
                "GROUP BY 1 "
                "ORDER BY 1"
            ),
        },
        'metric_schema': [
            {'key': 'requests', 'label': 'Обращения', 'type': 'int'},
            {'key': 'resolved_by_bot', 'label': 'Решено ботом', 'type': 'int'},
            {'key': 'transferred', 'label': 'Передано специалисту', 'type': 'int'},
        ],
    },
    {
        'slug': 'candidates-jsonl',
        'name': 'Бот: кандидаты из JSONL',
        'source_type': 'ssh_jsonl',
        'source_config': {
            'host': 'CHANGE_ME',
            'port': 22,
            'username': 'CHANGE_ME',
            'key_path': '${BOT_JSONL_SSH_KEY}',
            'remote_path': '/var/log/bot/stats.jsonl',
            'rotated_glob': '/var/log/bot/stats.jsonl*',
            'time_field': 'time',
        },
        'metric_schema': [
            {'key': 'candidates', 'label': 'Кандидаты', 'type': 'int'},
            {'key': 'sent', 'label': 'Отправлено', 'type': 'int'},
            {'key': 'confirmed', 'label': 'Подтверждено', 'type': 'int'},
            {'key': 'failed', 'label': 'Ошибки', 'type': 'int'},
            {'key': 'skipped', 'label': 'Пропущено', 'type': 'int'},
        ],
    },
]


def seed_bots(apps, schema_editor):
    Bot = apps.get_model('Bots', 'Bot')
    for item in BOTS:
        Bot.objects.update_or_create(slug=item['slug'], defaults=item)


def unseed_bots(apps, schema_editor):
    Bot = apps.get_model('Bots', 'Bot')
    Bot.objects.filter(slug__in=[item['slug'] for item in BOTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('Bots', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_bots, unseed_bots),
    ]
