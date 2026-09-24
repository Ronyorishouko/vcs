# -*- coding: utf-8 -*-
"""
Единая схема статистики ботов.

Новый бот = новая запись Bot (slug + source_type + source_config).
Новая метрика = новое поле внутри JSON metrics / пункт в metric_schema.
Миграции моделей для этого не нужны.
"""
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import models


class Bot(models.Model):
    SOURCE_POSTGRES = 'postgres'
    SOURCE_SSH_JSONL = 'ssh_jsonl'
    SOURCE_CHOICES = (
        (SOURCE_POSTGRES, 'PostgreSQL'),
        (SOURCE_SSH_JSONL, 'SSH JSONL-файл'),
    )

    slug = models.SlugField(
        max_length=64,
        unique=True,
        help_text='Стабильный код бота, например support-bot',
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    source_type = models.CharField(max_length=32, choices=SOURCE_CHOICES)
    source_config = JSONField(
        default=dict,
        blank=True,
        help_text=(
            'Параметры источника. Секреты задавайте как ${ENV_VAR}. '
            'postgres: host, port, dbname, user, password, query, time_field. '
            'ssh_jsonl: host, port, username, key_path, remote_path, rotated_glob, time_field.'
        ),
    )
    metric_schema = JSONField(
        default=list,
        blank=True,
        help_text='Описание витрины: [{"key": "requests", "label": "Обращения", "type": "int"}]',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Бот'
        verbose_name_plural = 'Боты'
        ordering = ['name']

    def __str__(self):
        return self.name

    def labeled_metrics(self, metrics):
        schema = self.metric_schema or []
        by_key = {item.get('key'): item for item in schema if item.get('key')}
        if by_key:
            result = []
            for item in schema:
                key = item.get('key')
                if not key:
                    continue
                result.append({
                    'key': key,
                    'label': item.get('label') or key,
                    'type': item.get('type') or 'number',
                    'value': metrics.get(key),
                })
            extra_keys = [k for k in metrics.keys() if k not in by_key]
            for key in extra_keys:
                result.append({
                    'key': key,
                    'label': key,
                    'type': 'number',
                    'value': metrics.get(key),
                })
            return result
        return [
            {'key': key, 'label': key, 'type': 'number', 'value': value}
            for key, value in metrics.items()
        ]


class BotStatSnapshot(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='snapshots')
    occurred_at = models.DateTimeField(db_index=True)
    collected_at = models.DateTimeField(auto_now_add=True)
    metrics = JSONField(default=dict)
    source_ref = models.CharField(
        max_length=512,
        blank=True,
        default='',
        help_text='Откуда взята строка: файл:смещение или id строки SQL',
    )

    class Meta:
        verbose_name = 'Снимок статистики'
        verbose_name_plural = 'Снимки статистики'
        unique_together = (('bot', 'occurred_at'),)
        indexes = [
            models.Index(fields=['bot', '-occurred_at']),
            GinIndex(fields=['metrics']),
        ]
        ordering = ['-occurred_at']

    def __str__(self):
        return '%s @ %s' % (self.bot.slug, self.occurred_at)


class BotCollectCursor(models.Model):
    bot = models.OneToOneField(Bot, on_delete=models.CASCADE, related_name='cursor')
    data = JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Курсор сбора'
        verbose_name_plural = 'Курсоры сбора'

    def __str__(self):
        return 'cursor:%s' % self.bot.slug


class BotCollectRun(models.Model):
    STATUS_OK = 'ok'
    STATUS_ERROR = 'error'
    STATUS_CHOICES = (
        (STATUS_OK, 'OK'),
        (STATUS_ERROR, 'Ошибка'),
    )

    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='collect_runs')
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    inserted = models.IntegerField(default=0)
    updated = models.IntegerField(default=0)
    skipped = models.IntegerField(default=0)
    error = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Запуск сбора'
        verbose_name_plural = 'Запуски сбора'
        ordering = ['-started_at']

    def __str__(self):
        return '%s %s %s' % (self.bot.slug, self.started_at, self.status)
