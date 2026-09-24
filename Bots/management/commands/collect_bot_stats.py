# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

from Bots.models import Bot
from Bots.services import collect_all


class Command(BaseCommand):
    help = (
        'Собрать статистику ботов. Для cron: '
        'python manage.py collect_bot_stats'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--slug',
            dest='slug',
            default=None,
            help='Собрать только одного бота по slug',
        )

    def handle(self, *args, **options):
        slug = options.get('slug')
        if slug and not Bot.objects.filter(slug=slug).exists():
            raise CommandError('Бот %s не найден' % slug)
        results = collect_all(slug=slug)
        if not results:
            self.stdout.write('Нет активных ботов')
            return
        for item in results:
            self.stdout.write(
                '%s: %s inserted=%s updated=%s' % (
                    item['slug'],
                    item['status'],
                    item['inserted'],
                    item['updated'],
                )
            )
            if item.get('error'):
                self.stderr.write(item['error'])
        failed = [item for item in results if item['status'] != 'ok']
        if failed:
            raise CommandError('Сбор завершился с ошибками: %s' % ', '.join(item['slug'] for item in failed))
