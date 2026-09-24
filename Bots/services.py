# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from .collectors import get_collector
from .models import Bot, BotCollectCursor, BotCollectRun, BotStatSnapshot


def collect_all(slug=None):
    qs = Bot.objects.filter(is_active=True).order_by('id')
    if slug:
        qs = qs.filter(slug=slug)
    results = []
    for bot in qs:
        results.append(collect_bot(bot))
    return results


def collect_bot(bot):
    started = _now()
    run = BotCollectRun.objects.create(
        bot=bot,
        started_at=started,
        status=BotCollectRun.STATUS_OK,
    )
    try:
        cursor, _created = BotCollectCursor.objects.get_or_create(bot=bot, defaults={'data': {}})
        collector_cls = get_collector(bot.source_type)
        records, new_cursor = collector_cls().collect(bot, cursor.data or {})
        inserted = 0
        updated = 0
        skipped = 0
        with transaction.atomic():
            for record in records:
                obj, created = BotStatSnapshot.objects.update_or_create(
                    bot=bot,
                    occurred_at=record['occurred_at'],
                    defaults={
                        'metrics': record.get('metrics') or {},
                        'source_ref': record.get('source_ref') or '',
                    },
                )
                if created:
                    inserted += 1
                else:
                    updated += 1
            cursor.data = new_cursor or {}
            cursor.save(update_fields=['data', 'updated_at'])
        run.inserted = inserted
        run.updated = updated
        run.skipped = skipped
        run.status = BotCollectRun.STATUS_OK
    except Exception as exc:
        run.status = BotCollectRun.STATUS_ERROR
        run.error = str(exc)
    finally:
        run.finished_at = _now()
        run.save()
    return {
        'slug': bot.slug,
        'status': run.status,
        'inserted': run.inserted,
        'updated': run.updated,
        'error': run.error,
    }


def _now():
    if timezone.is_aware(timezone.now()):
        return timezone.now()
    return datetime.now()
