# -*- coding: utf-8 -*-
from .postgres import PostgresCollector
from .ssh_jsonl import SshJsonlCollector

COLLECTORS = {
    'postgres': PostgresCollector,
    'ssh_jsonl': SshJsonlCollector,
}


def get_collector(source_type):
    try:
        return COLLECTORS[source_type]
    except KeyError:
        raise ValueError('Неизвестный source_type: %s' % source_type)
