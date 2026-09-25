# -*- coding: utf-8 -*-
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.dateparse import parse_datetime

from .models import Bot, BotCollectRun, BotStatSnapshot


@login_required
def dashboard(request):
    """
    Страница статистики ботов. Каркас страницы (шапка/меню/подвал) наследуется
    из общего base.html (как в Poly), меняется только содержимое {% block content %}.
    """
    bots = Bot.objects.filter(is_active=True).order_by('name')
    bots_payload = []
    for bot in bots:
        last_run = bot.collect_runs.order_by('-started_at').first()
        bots_payload.append({
            'slug': bot.slug,
            'name': bot.name,
            'source_type': bot.source_type,
            'metric_schema': bot.metric_schema or [],
            'last_run': _serialize_run(last_run),
        })

    context = {
        'bots_json': json.dumps(bots_payload, ensure_ascii=False),
        'bots': bots,
    }
    return render(request, 'Bots/dashboard.html', context)


@login_required
def bot_stats_api(request, slug):
    """
    JSON-API: точки статистики одного бота за период.
    GET /Bots/api/<slug>/stats/?since=YYYY-MM-DDTHH:MM:SS&until=...&limit=500
    """
    try:
        bot = Bot.objects.get(slug=slug, is_active=True)
    except Bot.DoesNotExist:
        return HttpResponseBadRequest('Бот не найден или неактивен')

    qs = BotStatSnapshot.objects.filter(bot=bot).order_by('occurred_at')

    since_raw = request.GET.get('since')
    until_raw = request.GET.get('until')
    if since_raw:
        since = parse_datetime(since_raw)
        if since is None:
            return HttpResponseBadRequest('Некорректный since')
        qs = qs.filter(occurred_at__gte=since)
    if until_raw:
        until = parse_datetime(until_raw)
        if until is None:
            return HttpResponseBadRequest('Некорректный until')
        qs = qs.filter(occurred_at__lte=until)

    try:
        limit = min(int(request.GET.get('limit', 500)), 5000)
    except ValueError:
        return HttpResponseBadRequest('Некорректный limit')

    # Берём последние N точек в возрастающем порядке времени.
    total = qs.count()
    if total > limit:
        qs = qs.order_by('-occurred_at')[:limit]
        rows = list(reversed(list(qs)))
    else:
        rows = list(qs)

    points = []
    for snap in rows:
        points.append({
            'occurred_at': snap.occurred_at.isoformat(),
            'metrics': snap.metrics or {},
        })

    return JsonResponse({
        'slug': bot.slug,
        'name': bot.name,
        'metric_schema': bot.metric_schema or [],
        'points': points,
        'truncated': total > limit,
        'total': total,
    })


@login_required
def bot_runs_api(request, slug):
    """
    JSON-API: последние запуски сбора для бота (для блока диагностики).
    GET /Bots/api/<slug>/runs/?limit=20
    """
    try:
        bot = Bot.objects.get(slug=slug)
    except Bot.DoesNotExist:
        return HttpResponseBadRequest('Бот не найден')

    try:
        limit = min(int(request.GET.get('limit', 20)), 200)
    except ValueError:
        return HttpResponseBadRequest('Некорректный limit')

    runs = bot.collect_runs.order_by('-started_at')[:limit]
    return JsonResponse({
        'slug': bot.slug,
        'runs': [_serialize_run(run) for run in runs],
    })


def _serialize_run(run):
    if run is None:
        return None
    return {
        'started_at': run.started_at.isoformat() if run.started_at else None,
        'finished_at': run.finished_at.isoformat() if run.finished_at else None,
        'status': run.status,
        'inserted': run.inserted,
        'updated': run.updated,
        'skipped': run.skipped,
        'error': run.error,
    }
