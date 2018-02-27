!define NAME Mamonsu
!define VERSION 2.3.4
!define MAMONSU_REG_PATH "Software\PostgresPro\Mamonsu"
!define MAMONSU_REG_UNINSTALLER_PATH "Software\Microsoft\Windows\CurrentVersion\Uninstall"
!define EDB_REG "SOFTWARE\Postgresql"
!define PGPRO_REG_1C "SOFTWARE\Postgres Professional\PostgresPro 1C"
!define PGPRO_REG_32 "SOFTWARE\PostgresPro\X86"
!define PGPRO_REG_64 "SOFTWARE\PostgresPro\X64"
!define USER "mamonsu"
!define CONFIG_FILE "agent.conf"
!define EXE_FILE "mamonsu.exe"
!define OLD_EXE_FILE "agent.exe"
!define LOG_FILE "mamonsu.log"
!define SERVICE_FILE "service_win32.exe"
!define TEMPLATE_FILE "template_win32.xml"

!define SERVICE_NAME "mamonsu"
!define SERVICE_DISPLAY_NAME "Monitoring agent: mamonsu"
!define SERVICE_TYPE "16"      ; service that runs in its own process
!define SERVICE_START_TYPE "2" ; automatic start
!define SERVICE_DEPENDENCIES "EventLog"
!define SERVICE_DESCRIPTION "mamonsu service"

LangString PG_TITLE ${LANG_ENGLISH} "PostgreSQL"
LangString PG_SUBTITLE ${LANG_ENGLISH} "Server options of PostgreSQL instance you want to monitor"
LangString ZB_TITLE ${LANG_ENGLISH} "Zabbix"
LangString ZB_SUBTITLE ${LANG_ENGLISH} "Server options of Zabbix"
LangString DESC_SectionMS ${LANG_ENGLISH} "Install run-time components that are required to run C++ applications"
LangString DESC_SectionMamonsu ${LANG_ENGLISH} "Install Mamonsu Zabbix agent on this computer"
