# -*- coding: utf-8 -*-
from celery import shared_task


@shared_task(name='Bots.tasks.collect_bot_stats')
def collect_bot_stats(slug=None):
    from .services import collect_all
    return collect_all(slug=slug)
