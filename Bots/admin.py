# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Bot, BotCollectCursor, BotCollectRun, BotStatSnapshot


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'source_type', 'is_active', 'updated_at')
    list_filter = ('source_type', 'is_active')
    search_fields = ('name', 'slug')


@admin.register(BotStatSnapshot)
class BotStatSnapshotAdmin(admin.ModelAdmin):
    list_display = ('bot', 'occurred_at', 'collected_at', 'source_ref')
    list_filter = ('bot',)
    search_fields = ('bot__slug', 'source_ref')
    readonly_fields = ('collected_at',)
    date_hierarchy = 'occurred_at'


@admin.register(BotCollectCursor)
class BotCollectCursorAdmin(admin.ModelAdmin):
    list_display = ('bot', 'updated_at')
    readonly_fields = ('updated_at',)


@admin.register(BotCollectRun)
class BotCollectRunAdmin(admin.ModelAdmin):
    list_display = ('bot', 'started_at', 'status', 'inserted', 'updated', 'skipped')
    list_filter = ('status', 'bot')
    readonly_fields = ('bot', 'started_at', 'finished_at', 'status', 'inserted', 'updated', 'skipped', 'error')
