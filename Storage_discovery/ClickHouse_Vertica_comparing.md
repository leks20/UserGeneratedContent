## Сравнительный анализ ClickHouse и Vertica

### Вставка данных

- ClickHouse: 148.03 seconds (10 000 000 records)
- Vertica: 100 seconds (1000 000 records)
- Vertica: 16 minutes 46 seconds (10 000 000 records)

### Чтение данных

- ClickHouse: 0.11 seconds (1000 records)
- ClickHouse: 19.22 seconds (1 000 000 records)
- ClickHouse: 159.48 seconds (10 000 000 records)
- Vertica: 41.12 seconds (1000 000 records)
- Vertica: 7 minutes 18 seconds (10 000 000 records)

## Дополнительные преимущества
Таблицы в базах данных ClickHouse могут использовать движок ReplicatedMergeTree, обеспечивающий автоматическую репликацию данных, а также движок Distributed, который позволяет запрашивать данные во всех шардах, как если бы это была одна таблица.

Эта настройка обеспечивает высокий уровень избыточности и доступности данных. Если какой-либо отдельный узел выходит из строя,  данные по-прежнему доступны с других узлов.