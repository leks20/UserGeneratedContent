# UGC Service (Online Cinema)

## Адрес репозитория
https://github.com/do8rolyuboff/ugc_sprint_1

## Описание:
Сервис для сбора и последующей аналитики контента пользователей онлайн кинотеатра (лайки, просмотры, комментарии).

## Технологии:
Python3, FastAPI, Kafka, Redis, ClickHouse

## Установка:
1. Заполнить файлы окружений:
   1. WebAPP - `api_service/conf/.env`
   2. ETL - `etl_kafka_to_redis/.env`
   3. ClickHouse - `clickhouse/.env`
2. Запуск образов:
   1. Установить Docker [link](https://docs.docker.com/engine/install/)
   2. Создать сеть - `docker network create ugc_network`
   3. Запуск контейнера web app - `docker-compose -f docker-compose.yml up --build -d`
   4. Запуск контейнера clickhouse - `docker-compose -f clickhouse/docker-compose.yml up --build -d`
      1. Настройка шардов и реплик для clickhouse:
      2. ```
         docker exec clickhouse-node1 /bin/bash -c "/docker-entrypoint-initdb.d/init_db_1.sh"
         docker exec clickhouse-node2 /bin/bash -c "/docker-entrypoint-initdb.d/init_db_2.sh"
         docker exec clickhouse-node3 /bin/bash -c "/docker-entrypoint-initdb.d/init_db_3.sh"
         docker exec clickhouse-node4 /bin/bash -c "/docker-entrypoint-initdb.d/init_db_4.sh"
         ```

## Документация:
1. Swagger - `host/swagger`
2. UML - диаграммы(PlantUML):
   1. Общая С1 - `specs/uml/*-general_schema`
   2. UGC компонент C2 - `specs/uml/*-ugc_component`
3. Сравнение OLAP-хранилищ на чтение/запись - `Storage_discovery`

## Метрики:
1. Потребляемая память(Prometheus) - адрес по умолчанию `host:8001`

## Ответ на вопрос:
* Если запустить gunicorn или другую команду без exec, то она будет запущена в дочернем процессе. В результате, основной процесс скрипта (а не Gunicorn) станет процессом с PID 1 в контейнере.
