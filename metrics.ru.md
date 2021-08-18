# Описания плагинов

## pg_probackup.py
Предназначен для контроля за состоянием каталогов бэкапов создаваемых утилитой [pg_probackup](https://postgrespro.ru/docs/postgrespro/current/app-pgprobackup).
Плагин адаптирован для контроля нескольких инстансов в одном каталоге. Имя инстанса указывается в ключе метрики как подкаталог.

### Настройки в секции [pgprobackup]

| Наименование                      | Ключ                      | Описание                                                           |
| --------------------------------- | ------------------------- | ------------------------------------------------------------------ |
| enabled                           | False                     | По умолчанию плагин отключен. Укажите True для включения           |
| interval                          | 900                       | Как часто опрашивать состояние каталогов. Указано в секундах       |
| backup_dirs                       | /backup_dir1,/backup_dir2 | Список каталогов бэкапов утилиты pg_probackup                      |
| pg_probackup_path                 | /usr/bin/pg_probackup-13  | Полный путь к утилите создания бэкапов  pg_probackup               |
| max_time_run_backup2alert_in_sec  | 21600                     | Время срабатывания алерта "Backup runs too long on..." в секундах. |
| max_time_lack_backup2alert_in_sec | 100800                    | Время срабатывания алерта "Long time no backups on..." в секундах. |


### Текущие метрики в Discovery правиле:

| Наименование                                               | Ключ                                             | Хранить | Описание                                                 |
| ---------------------------------------------------------- | ------------------------------------------------ | ------- | -------------------------------------------------------- |
| Pg_probackup dir {#BACKUPDIR}: size                        | pg_probackup.dir.size[{#BACKUPDIR}]              | 31d     | Общий размер каталога: /backups + /wal                   |
| Pg_probackup dir {#BACKUPDIR}/backups: size                | pg_probackup.dir.size[{#BACKUPDIR}/backups]      | 31d     | Размер подкаталога /backups                              |
| Pg_probackup dir {#BACKUPDIR}/wal: size                    | pg_probackup.dir.size[{#BACKUPDIR}/wal]          | 31d     | Размер подкаталога /wal                                  |
| Pg_probackup dir {#BACKUPDIR}: duration full backup        | pg_probackup.dir.duration_full[{#BACKUPDIR}]     | 31d     | Длительность в секундах создания полного бэкапа          |
| Pg_probackup dir {#BACKUPDIR}: duration incremental backup | pg_probackup.dir.duration_inc[{#BACKUPDIR}]      | 31d     | Длительность в секундах создания инкрементального бэкапа |
| Pg_probackup dir {#BACKUPDIR}: start time backup           | pg_probackup.dir.start_time_backup[{#BACKUPDIR}] |         | Время (UNIXTIME) старта создания бэкапа                  |
| Pg_probackup dir {#BACKUPDIR}: end time backup             | pg_probackup.dir.end_time_backup[{#BACKUPDIR}]   |         | Время (UNIXTIME) завершения создания бэкапа              |
| Pg_probackup dir {#BACKUPDIR}: mode                        | pg_probackup.dir.mode_backup[{#BACKUPDIR}]       |         | Текущий режим бэкапа                                     |
| Pg_probackup dir {#BACKUPDIR}: status                      | pg_probackup.dir.status_backup[{#BACKUPDIR}]     |         | Текущий статус бэкапа                                    |
| Pg_probackup dir {#BACKUPDIR}: error                       | pg_probackup.dir.error[{#BACKUPDIR}]             |         | Признак ошибочного состояния или "ok" если всё хорошо    |


### Текущие алерты в Discovery правиле:
Созданы следующие алерты, позволящие контролировать состояние архивных каталогов:

* Алерт срабатывает если создание бэкапа выполняется больше, чем указано в настроечном параметре `max_time_run_backup2alert_in_sec`. Время задаётся в секундах и значение по умолчанию = 21600 (6 часов). Контролируется текущее состояние в котором находится процесс создания бэкапной копии. 

| Категория     | Детали                                                                                                                                                                                                                                                                             |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Важность:     | Warning                                                                                                                                                                                                                                                                            |
| Наименование: | Backup runs too long on {HOSTNAME} in pg_probackup dir {#BACKUPDIR} (RUNNING)                                                                                                                                                                                                      |
| Выражение:    | {PostgresPro-Linux:pg_probackup.dir.status_backup[{#BACKUPDIR}].last()}="RUNNING" and ( {PostgresPro-Linux:pg_probackup.dir.start_time_backup[{#BACKUPDIR}].now()}-{PostgresPro-Linux:pg_probackup.dir.start_time_backup[{#BACKUPDIR}].last()}) > max_time_run_backup2alert_in_sec |

* Алерт срабатывает если не выполняется создание нового бэкапа дольше, чем указано в настроечном параметре `max_time_lack_backup2alert_in_sec`. Время задаётся в секундах и значение по умолчанию = 100800 (28 часов). Контролируется, что очередной бэкап (тип бэкапа любой) будет создан не позже, чем указано в параметре.

| Категория     | Детали                                                                                                                                                                                     |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Важность:     | Warning                                                                                                                                                                                    |
| Наименование: | Long time no backups on {HOSTNAME} in pg_probackup dir {#BACKUPDIR}                                                                                                                        |
| Выражение:    | ( {PostgresPro-Linux:pg_probackup.dir.end_time_backup[{#BACKUPDIR}].now()} -{PostgresPro-Linux:pg_probackup.dir.end_time_backup[{#BACKUPDIR}].last()}) > max_time_lack_backup2alert_in_sec |

* Алерт срабатывает если при создании бэкапа произошла ошибка - 'ERROR', 'CORRUPT', 'ORPHAN'. Контролирует состояние любой архивной копии, не только последней. Активен всё время пока есть любая архивная копия с ошибочным состоянием.

| Категория     | Детали                                                                              |
| ------------- | ----------------------------------------------------------------------------------- |
| Важность:     | Average                                                                             |
| Наименование: | Error in pg_probackup dir {#BACKUPDIR} (hostname={HOSTNAME} value={ITEM.LASTVALUE}) |
| Выражение:    | {PostgresPro-Linux:pg_probackup.dir.error[{#BACKUPDIR}].str(ok)}<>1                 |


### Текущие графики в Discovery правиле:

1. Pg_probackup: backup dir: {#BACKUPDIR} size

Показывает 3 метрики с информацией о размерах каталогов с архивными копиями:

| Метрика                                     | Сторона графика | Описание                               |
| ------------------------------------------- | --------------- | -------------------------------------- |
| pg_probackup.dir.size[{#BACKUPDIR}]         | (Left Side)     | Общий размер каталогов /backups + /wal |
| pg_probackup.dir.size[{#BACKUPDIR}/backups] | (Left Side)     | размер подкаталога /backups            |
| pg_probackup.dir.size[{#BACKUPDIR}/wal]     | (Right Side)    | размер подкаталога /wal                |

2. Pg_probackup: backup dir: {#BACKUPDIR} duration

Показывает 2 метрики с длительностью создания архивных копий:

| Метрика                                      | Сторона графика | Описание                                                 |
| -------------------------------------------- | --------------- | -------------------------------------------------------- |
| pg_probackup.dir.duration_full[{#BACKUPDIR}] | (Left Side)     | Длительность в секундах создания полного бэкапа          |
| pg_probackup.dir.duration_inc[{#BACKUPDIR}]  | (Right Side)    | Длительность в секундах создания инкрементального бэкапа |
