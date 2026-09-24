# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.contrib.postgres.fields.jsonb
import django.contrib.postgres.indexes
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(help_text='Стабильный код бота, например support-bot', max_length=64, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('source_type', models.CharField(choices=[('postgres', 'PostgreSQL'), ('ssh_jsonl', 'SSH JSONL-файл')], max_length=32)),
                ('source_config', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, help_text='Параметры источника. Секреты задавайте как ${ENV_VAR}. postgres: host, port, dbname, user, password, query, time_field. ssh_jsonl: host, port, username, key_path, remote_path, rotated_glob, time_field.')),
                ('metric_schema', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, help_text='Описание витрины: [{"key": "requests", "label": "Обращения", "type": "int"}]')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Бот',
                'verbose_name_plural': 'Боты',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='BotCollectCursor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('bot', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cursor', to='Bots.Bot')),
            ],
            options={
                'verbose_name': 'Курсор сбора',
                'verbose_name_plural': 'Курсоры сбора',
            },
        ),
        migrations.CreateModel(
            name='BotCollectRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField()),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('ok', 'OK'), ('error', 'Ошибка')], max_length=16)),
                ('inserted', models.IntegerField(default=0)),
                ('updated', models.IntegerField(default=0)),
                ('skipped', models.IntegerField(default=0)),
                ('error', models.TextField(blank=True, default='')),
                ('bot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collect_runs', to='Bots.Bot')),
            ],
            options={
                'verbose_name': 'Запуск сбора',
                'verbose_name_plural': 'Запуски сбора',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='BotStatSnapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('occurred_at', models.DateTimeField(db_index=True)),
                ('collected_at', models.DateTimeField(auto_now_add=True)),
                ('metrics', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('source_ref', models.CharField(blank=True, default='', help_text='Откуда взята строка: файл:смещение или id строки SQL', max_length=512)),
                ('bot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='Bots.Bot')),
            ],
            options={
                'verbose_name': 'Снимок статистики',
                'verbose_name_plural': 'Снимки статистики',
                'ordering': ['-occurred_at'],
                'unique_together': set([('bot', 'occurred_at')]),
            },
        ),
        migrations.AddIndex(
            model_name='botstatsnapshot',
            index=models.Index(fields=['bot', '-occurred_at'], name='Bots_botsta_bot_id_occur_idx'),
        ),
        migrations.AddIndex(
            model_name='botstatsnapshot',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metrics'], name='Bots_botsta_metrics_gin'),
        ),
    ]
