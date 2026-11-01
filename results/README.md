# Результаты сценариев

Артефакты: `results.json` - статусы и числа сценариев; `tablestats.txt` /
`tablestats_plain.txt` - `bash ops.sh tablestats`; `repair.txt` - `bash ops.sh repair`.

Блоки ниже копируются в README и заполняются числами своего прогона.

## `bulk` - вставка 10 000

| Что вставлено | Сколько | Время |
|---|---|---|
| События пользователя 1001 (`login`, `purchase`, `view`) | 10 000 | |

Время - из вывода `bulk` или `artifacts.bulk.seconds` (секунды); среднее за
запись = время / 10 000.

## `consistency` - ONE vs QUORUM

| Уровень | Запись, мс | Чтение, мс |
|---|---|---|
| ONE | | |
| QUORUM | | |

Числа - `artifacts.consistency` (секунды); для таблицы перевести в миллисекунды.

## Сжатие - `tablestats`

| Таблица | Space used (total) | SSTable count | SSTable Compression Ratio |
|---|---|---|---|
| `user_actions` (LZ4) | | | |
| `user_actions_none` (без сжатия) | | | |

Источник - `tablestats.txt` и `tablestats_plain.txt`.

## Bloom-фильтр

| Показатель | Значение |
|---|---|
| Bloom filter false positives | |
| Bloom filter false ratio | |

Источник - `tablestats.txt`, секция `hw3.user_actions`.

## `data` и `repair`

`data` - в README статус и краткий перечень проверенного (`scenarios.data`
в `results.json`); `repair` - финальные строки `repair.txt` и объяснения
раздела 7.
