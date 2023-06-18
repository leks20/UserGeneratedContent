## Кластер MongoDB

1. Настройка серверов конфигурации: 
`docker exec -it mongocfg1 bash -c 'echo "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"mongocfg1\"}, {_id: 1, host: \"mongocfg2\"}, {_id: 2, host: \"mongocfg3\"}]})" | mongosh'`
- Проверка: `docker exec -it mongocfg1 bash -c 'echo "rs.status()" | mongosh'`

2. Инициализация реплик шарда: 
`docker exec -it mongors1n1 bash -c 'echo "rs.initiate({_id: \"mongors1\", members: [{_id: 0, host: \"mongors1n1\"}, {_id: 1, host: \"mongors1n2\"}, {_id: 2, host: \"mongors1n3\"}]})" | mongosh'`
- Проверка: `docker exec -it mongors1n1 bash -c 'echo "rs.status()" | mongosh'`

3. Добавление реплик в кластер: 
`docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors1/mongors1n1\")" | mongosh'`
- Проверка: `docker exec -it mongos1 bash -c 'echo "sh.status()" | mongosh'`

## Создать базу данных и включить шардирование
- `docker exec -it mongors1n1 bash -c 'echo "use testDB" | mongosh'`
- `docker exec -it mongos1 bash -c 'echo "sh.enableSharding(\"testDB\")" | mongosh'`
