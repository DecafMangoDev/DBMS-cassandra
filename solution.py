# -*- coding: utf-8 -*-
# Заготовка решения ДЗ_3 (Cassandra). Заполняйте тела функций с TODO -
# остальное (стенд, контрольные данные, проверки) уже готово в lab.py.
# Служебный lab.py менять не нужно; контракты и порядок опытов - в Задание.md.

import json
from datetime import datetime, timedelta

from cassandra.query import ConsistencyLevel

# База отсчёта времени событий: 2026-01-01T00:00:00Z. Важно: без таймзоны
# (наивный UTC) - драйвер возвращает timestamp без tzinfo, и сценарий data
# сравнивает прочитанные значения именно с наивной базой.
BASE_EVENT_TIME = datetime(2026, 1, 1)

# Типы событий: циклично по индексу i - login, purchase, view.
EVENT_TYPES = ['login', 'purchase', 'view']


def create_tables(session):
    # Раздел 2, сценарий data. Создайте две таблицы в keyspace hw3 -
    # сессия уже подключена к нему.
    #
    # user_actions: user_id int (partition key), event_time timestamp
    #   (clustering key, порядок по убыванию - ORDER BY event_time DESC),
    #   event_type text, payload text; включите сжатие LZ4 через
    #   параметр COMPRESSION в CREATE TABLE.
    # user_actions_none: та же структура, но сжатие отключено (параметр
    #   COMPRESSION; как отключить - найдите в документации). Таблица
    #   нужна только для сравнения размеров SSTable в разделе 5.
    #
    # Сценарий data проверяет по system_schema: partition key, DESC
    # у event_time, наличие event_type и payload, настройки сжатия
    # обеих таблиц.
    #
    # Верните список имён созданных таблиц
    # (например, ['user_actions', 'user_actions_none']).
    session.execute(
        "CREATE TABLE IF NOT EXISTS user_actions ("
        "user_id int, event_time timestamp, event_type text, payload text, "
        "PRIMARY KEY (user_id, event_time)) "
        "WITH CLUSTERING ORDER BY (event_time DESC) "
        "AND compression = {'class': 'LZ4Compressor'}"
    )
    session.execute(
        "CREATE TABLE IF NOT EXISTS user_actions_none ("
        "user_id int, event_time timestamp, event_type text, payload text, "
        "PRIMARY KEY (user_id, event_time)) "
        "WITH CLUSTERING ORDER BY (event_time DESC) "
        "AND compression = {'enabled': 'false'}"
    )
    return ['user_actions', 'user_actions_none']


def insert_events(session, table, user_id, n, consistency):
    # Разделы 3-4, сценарии bulk и consistency. Вставьте n событий
    # пользователя user_id в таблицу table (сценарий передаёт и
    # 'user_actions', и 'user_actions_none' - обе должны получить данные).
    #
    # Событие с номером i (i = 0..n-1):
    #   event_time = BASE_EVENT_TIME + timedelta(minutes=i)
    #   event_type - по циклу из EVENT_TYPES (события чередуются:
    #   login, purchase, view)
    #   payload - словарь с полем seq, равным i, сериализованный в JSON
    #
    # Вставка - через PreparedStatement: session.prepare(...) один раз,
    # затем bind и execute для каждого события. Требование задания.
    # Уровень консистентности задавайте на отдельном утверждении
    # (bound.consistency_level = consistency), а не на сессии: сессия
    # у сценария consistency одна на все четыре замера.
    #
    # Верните n - число вставленных событий.
    prepared = session.prepare(
        'INSERT INTO %s (user_id, event_time, event_type, payload) '
        'VALUES (?, ?, ?, ?)' % table
    )
    for i in range(n):
        bound = prepared.bind([
            user_id,
            BASE_EVENT_TIME + timedelta(minutes=i),
            EVENT_TYPES[i % len(EVENT_TYPES)],
            json.dumps({'seq': i}),
        ])
        bound.consistency_level = consistency
        session.execute(bound)
    return n


def read_last(session, table, user_id, limit, consistency):
    # Разделы 3-4, сценарии bulk и consistency. Прочитайте limit последних
    # событий пользователя user_id из таблицы table.
    #
    # Запрос: SELECT ... WHERE user_id = ? ORDER BY event_time DESC LIMIT ?.
    # Порядок по убыванию уже даёт кластеризация таблицы - сортировать
    # на клиенте не нужно. Уровень консистентности - на утверждении,
    # как в insert_events.
    #
    # Верните список строк результата - list(session.execute(...)):
    # сценарий берёт из строк поля event_time и event_type.
    prepared = session.prepare(
        'SELECT event_time, event_type, payload FROM %s '
        'WHERE user_id = ? ORDER BY event_time DESC LIMIT ?' % table
    )
    bound = prepared.bind([user_id, limit])
    bound.consistency_level = consistency
    return list(session.execute(bound))
