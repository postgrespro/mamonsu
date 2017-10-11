; Mamonsu install Script
; Written by Postgres Professional, Postgrespro.ru
; dba@postgrespro.ru
;--------------------------------
!addincludedir Include
!addplugindir Plugins
!include mamonsu.def.nsh
!include Utf8Converter.nsh
!include MUI2.nsh
!include LogicLib.nsh
!include nsDialogs.nsh
!include NSISpcre.nsh
!include TextFunc.nsh
!include WordFunc.nsh
!insertmacro REMatches
;-------------------------------

Name "${NAME} ${VERSION}"
OutFile "mamonsu-${VERSION}.exe"
InstallDir "$PROGRAMFILES\PostgresPro\${NAME}\${VERSION}"
BrandingText "Postgres Professional"
;-------------------------------

Var Dialog
Var Label

Var pg_host
Var pg_host_input
Var pg_port
Var pg_port_input
Var pg_db
Var pg_db_input
Var pg_user
Var pg_user_input
Var pg_password
Var pg_password_input
Var pg_version
Var pg_datadir
Var pg_service

Var zb_client
Var zb_client_input
Var zb_address
Var zb_address_input
Var zb_port
Var zb_port_input
Var zb_conf
Var log_dir
Var img_path
Var hostname
Var action
Var brand
Var user_password
Var user_not_exist
Var ext_version
Var ext_inst_dir
Var ext_log_dir

;----------------------------------------
;General
RequestExecutionLevel admin

!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "pp_header.bmp" ; optional
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\classic-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\classic-uninstall.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "mamonsu.bmp" ; 164x314
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "mamonsu.bmp"
!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!define MUI_COMPONENTSPAGE_SMALLDESC
!insertmacro MUI_PAGE_COMPONENTS 
!define MUI_PAGE_CUSTOMFUNCTION_PRE CheckMamonsu ; Important!
!insertmacro MUI_PAGE_DIRECTORY

Page custom CheckPG ; collect postgresql data
Page custom CheckZB ; collect zabbix data
Page custom DefaultConf
Page custom PG_Page InputData
Page custom ZB_Page InputDataZB

;second directory selection
!define MUI_PAGE_HEADER_TEXT "Mamonsu Log Directory"
!define MUI_PAGE_HEADER_SUBTEXT "Choose Mamonsu log directory location"
!define MUI_DIRECTORYPAGE_TEXT_TOP "The installer will place Mamonsu log directory in the following folder. To install in a different folder, click Browse and select another folder. Click Install to continue."
!define MUI_DIRECTORYPAGE_VARIABLE $log_dir
SpaceTexts none
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_NOAUTOCLOSE
!define MUI_FINISHPAGE_SHOWREADME_TEXT "show config"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\${CONFIG_FILE}"
!insertmacro MUI_PAGE_FINISH

;Uninstall
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!define MUI_UNFINISHPAGE_NOAUTOCLOSE
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"
;-----------------------------------------------


;Sections 
Section "Microsoft Visual C++ 2010 Redistibutable" SectionMS
 GetTempFileName $1
 File /oname=$1 vcredist\vcredist_x86_2010.exe
 ExecWait "$1  /passive /norestart" $0
 DetailPrint "Visual C++ Redistributable Packages return $0"
 Delete $1
SectionEnd

Section "${NAME} ${VERSION}" SectionMamonsu
 #installation procedure
 ${if} $action != ''
   Call StopService
 ${endif}

 SetOutPath "$INSTDIR"
 File "..\..\dist\${SERVICE_FILE}"
 File "..\..\dist\${EXE_FILE}"
 File "..\..\packaging\conf\${TEMPLATE_FILE}"
 CreateDirectory "$log_dir"
 WriteUninstaller "$INSTDIR\Uninstall.exe"

 ;create user
 Call CreateUser
 ;create agent.conf
 Call CreateConfig
 ;create service
 Call CreateService
 ;create mamonsu registry entry 
 Call CreateReg
 ;start service
 Call StartService
 ;delete old directory if upgrade/downgrade
 Call DeleteDirectory
SectionEnd

Section "Uninstall"
 Call un.CheckExist
 Call un.DeleteService
 Call un.DeleteUser
 Call un.DeleteReg
 Call un.DeleteDirectory
SectionEnd

;------------------------------------------
;Functions

Function CheckMamonsu
 ; if we abort from this function, next Page will be skipped
 ; if registry key InstallDir exist AND directory InstallDir itself exist we compare versions
 ; and determine our install policy
 SetRegView 32
 ReadRegStr $ext_version HKLM "${MAMONSU_REG_PATH}" "Version"
 ReadRegStr $ext_inst_dir HKLM "${MAMONSU_REG_PATH}\$ext_version" "InstallDir"
 ReadRegStr $hostname HKLM "System\CurrentControlSet\Control\ComputerName\ActiveComputerName" "ComputerName"
  ${if} $ext_inst_dir != ''
    ReadRegStr $ext_log_dir HKLM "${MAMONSU_REG_PATH}\$ext_version" "LogDir"  
    ${if} ${FileExists} $ext_inst_dir
      ${VersionCompare} $ext_version ${VERSION} $0
      ${if} $0 == 0
       StrCpy $action 'reinstall'
       MessageBox MB_YESNO  "Mamonsu version $ext_version is already installed. Do you want to reinstall?" IDYES continue IDNO quit
      ${elseif} $0 == 1
       StrCpy $action 'downgrade'
       MessageBox MB_YESNO  "Mamonsu version $ext_version is already installed. Do you want to downgrade to version ${VERSION}?" IDYES continue IDNO quit
      ${elseif} $0 == 2
       StrCpy $action 'upgrade'
       MessageBox MB_YESNO  "Mamonsu version $ext_version is already installed. Do you want to upgrade to version ${VERSION}?" IDYES continue IDNO quit
      ${endif}
       continue:
       Abort
       quit:
       Quit
    ${endif}
  ${endif} 
FunctionEnd

Function CheckPG
 ; check EDB installation
 ${if} $action != ''
   Abort
 ${endif}
 SetRegView 64
 EnumRegKey $1 HKLM "${EDB_REG}\Installations" 0
 ${If} $1 != ''
   ReadRegStr $pg_version HKLM "${EDB_REG}\Installations\$1" "Version"
   ReadRegStr $pg_datadir HKLM "${EDB_REG}\Installations\$1" "Data Directory"
   ReadRegStr $pg_service HKLM "${EDB_REG}\Installations\$1" "Service ID"
   ReadRegStr $pg_user HKLM "${EDB_REG}\Installations\$1" "Super User"
   ${If} $pg_version != ''
    StrCpy $brand "EDB"
    ReadRegDWORD $pg_port HKLM "${EDB_REG}\Services\$1" "Port"
    Abort
    ${EndIf}
 ${EndIf}

;check PostgresPro 1C
 SetRegView 32
 EnumRegKey $1 HKLM "${PGPRO_REG_1C}\Installations" 0
 ${If} $1 != ''
   ReadRegStr $pg_version HKLM "${PGPRO_REG_1C}\Installations\$1" "Version"
   ReadRegStr $pg_datadir HKLM "${PGPRO_REG_1C}\Installations\$1" "Data Directory"
   ReadRegStr $pg_service HKLM "${PGPRO_REG_1C}\Installations\$1" "Service ID"
   ReadRegStr $pg_user HKLM "${PGPRO_REG_1C}\Installations\$1" "Super User"
    ${If} $pg_version != ''
     StrCpy $brand "PRO-1C"
     ReadRegDWORD $pg_port HKLM "${PGPRO_REG_1C}\Services\$1" "Port"
     Abort
    ${EndIf}
 ${EndIf}

; check PostgresPro 32bit
 SetRegView 32
 EnumRegKey $1 HKLM "${PGPRO_REG_32}" 0
 ${If} $1 != ''
   EnumRegKey $2 HKLM "${PGPRO_REG_32}\$1\Installations" 0
   ReadRegStr $pg_version HKLM "${PGPRO_REG_32}\$1\Installations\$2" "Version"
   ReadRegStr $pg_datadir HKLM "${PGPRO_REG_32}\$1\Installations\$2" "Data Directory"
   ReadRegStr $pg_service HKLM "${PGPRO_REG_32}\$1\Installations\$2" "Service ID"
   ReadRegStr $pg_user HKLM "${PGPRO_REG_32}\$1\Installations\$2" "Super User"
   ${If} $pg_version != ''
     StrCpy $brand "PRO-32"
     ReadRegDWORD $pg_port HKLM "${PGPRO_REG_32}\$1\Services\$2" "Port"
     Abort
   ${EndIf}
 ${EndIf}

 ;check PostgresPro 64bit
 SetRegView 32
 EnumRegKey $1 HKLM "${PGPRO_REG_64}" 0
 ${If} $1 != ''
   EnumRegKey $2 HKLM "${PGPRO_REG_64}\$1\Installations" 0
   ReadRegStr $pg_version HKLM "${PGPRO_REG_64}\$1\Installations\$2" "Version"
   ReadRegStr $pg_datadir HKLM "${PGPRO_REG_64}\$1\Installations\$2" "Data Directory"
   ReadRegStr $pg_service HKLM "${PGPRO_REG_64}\$1\Installations\$2" "Service ID"
   ReadRegStr $pg_user HKLM "${PGPRO_REG_64}\$1\Installations\$2" "Super User"
    ${If} $pg_version != ''
     StrCpy $brand "PRO-64"
     ReadRegDWORD $pg_port HKLM "${PGPRO_REG_64}\$1\Services\$2" "Port"
     Abort
    ${EndIf}
 ${EndIf}
FunctionEnd

Function CheckZB
 ; check zabbix agent installation
 ${if} $action != ''
   Abort
 ${endif}

 ReadRegStr $img_path HKLM "System\CurrentControlSet\Services\Zabbix Agent" "ImagePath"
 
 ${If} $img_path == ''
  Goto quit
 ${EndIf}

 ${RECaptureMatches} $0 '^.* --config \"(.+.conf)\"' $img_path 1 ; 1 - partial string match
 Pop $1
 StrCpy $zb_conf $1
 
 ${ifnot} ${FileExists} $zb_conf
  Goto quit
 ${endif}

 ${ConfigRead} "$zb_conf" "ServerActive=" $zb_address
 ${RECaptureMatches} $0 "([A-Za-z0-9.]+):?(\d+)?" $zb_address 0 ; 0 - full string match
 ${if} $0 != 'false' ; $0 can contain false or number of matches
   Pop $1
   Pop $2
   StrCpy $zb_address $1
   StrCpy $zb_port $2
 ${endif}
 ${ConfigRead} "$zb_conf" "Hostname=" $zb_client
 ${RECaptureMatches} $0 "(.+)" $zb_client 0 ; 0 - full string match
  ${if} $0 != 'false'
   Pop $1
   StrCpy $zb_client $1
  ${else}
   quit:
   StrCpy $zb_client $hostname
  ${endIf}
FunctionEnd

Function DefaultConf
 StrCpy $log_dir '$INSTDIR\logs'
 ${if} $action != ''
   Abort
 ${endif}

 ${If} $pg_datadir != ''
   ;TODO check if file EXIST
   ${ConfigRead} "$pg_datadir\postgresql.conf" "listen_addresses = " $pg_host
   ${RECaptureMatches} $0 "^\'(.+)\'" $pg_host 1 ; match goes to $1
   Pop $1
   StrCpy $pg_host $1
 ${EndIf}

 ${If} $pg_host == 'localhost'
 ${OrIf} $pg_host == '*'
 ${OrIf} $pg_host == ''
   StrCpy $pg_host '127.0.0.1'
 ${EndIf}

 ${If} $pg_port == ''
   StrCpy $pg_port "5432"
 ${EndIf}
 ${If} $pg_user == ''
   StrCpy $pg_user "postgres"
 ${EndIf}
 StrCpy $pg_db $pg_user

 ;zabbix
 ${If} $zb_address == 'localhost'
 ${OrIf} $zb_address == '*'
 ${OrIf} $zb_address == ''
   StrCpy $zb_address '127.0.0.1'
 ${EndIf}
 
 ${If} $zb_port == ''
   StrCpy $zb_port '10051'
 ${EndIf}
FunctionEnd

Function PG_Page
 ${if} $action != ''
   Abort
 ${endif}

 !insertmacro MUI_HEADER_TEXT $(PG_TITLE) $(PG_SUBTITLE)
 nsDialogs::Create 1018
 Pop $Dialog

 ${If} $Dialog == error
   Abort
 ${EndIf}

 ${NSD_CreateLabel} 0 2u 60u 12u "PostgreSQL host"
 Pop $Label
 ${NSD_CreateText}  65u 0 100u 12u "$pg_host"
 Pop $pg_host_input

 ${NSD_CreateLabel} 0 22u 60u 12u "PostgreSQL port"
 Pop $Label
 ${NSD_CreateText}  65u 20u 100u 12u "$pg_port"
 Pop $pg_port_input

 ${NSD_CreateLabel} 0 42u 60u 12u "PostgreSQL user"
 Pop $Label
 ${NSD_CreateText}  65u 40u 100u 12u "$pg_user"
 Pop $pg_user_input

 ${NSD_CreateLabel} 0 62u 60u 12u "PostgreSQL db"
 Pop $Label
 ${NSD_CreateText}  65u 60u 100u 12u "$pg_db"
 Pop $pg_db_input

 ${NSD_CreateLabel} 0 82u 60u 12u "Password"
 Pop $Label
 ${NSD_CreatePassword} 65u 80u 100u 12u ""
 Pop $pg_password_input

 nsDialogs::Show
FunctionEnd

Function InputData
 ${if} $action != ''
   Abort
 ${endif}
 ${NSD_GetText} $pg_host_input $pg_host
 ${NSD_GetText} $pg_port_input $pg_port
 ${NSD_GetText} $pg_user_input $pg_user
 ${NSD_GetText} $pg_db_input $pg_db
 ${NSD_GetText} $pg_password_input $pg_password
 ${If} $pg_password == ''
   StrCpy $pg_password 'None' 
 ${EndIf}  
FunctionEnd

Function ZB_Page
 ${if} $action != ''
   Abort
 ${endif}

 !insertmacro MUI_HEADER_TEXT $(ZB_TITLE) $(ZB_SUBTITLE)
 nsDialogs::Create 1018
 Pop $Dialog

 ${If} $Dialog == error
   Abort
 ${EndIf}

 ${NSD_CreateLabel} 0 2u 60u 12u "Zabbix host"
 Pop $Label
 ${NSD_CreateText}  65u 0 100u 12u "$zb_address"
 Pop $zb_address_input

 ${NSD_CreateLabel} 0 22u 60u 12u "Zabbix port"
 Pop $Label
 ${NSD_CreateText}  65u 20u 100u 12u "$zb_port"
 Pop $zb_port_input

 ${NSD_CreateLabel} 0 42u 60u 12u "Client name"
 Pop $Label
 ${NSD_CreateText}  65u 40u 100u 12u "$zb_client"
 Pop $zb_client_input

 nsDialogs::Show
FunctionEnd

Function InputDataZB
 ${if} $action != ''
   Abort
 ${endif}
 ${NSD_GetText} $zb_address_input $zb_address
 ${NSD_GetText} $zb_port_input $zb_port
 ${NSD_GetText} $zb_client_input $zb_client
FunctionEnd

Function CreateUser
 DetailPrint "Checking user ..."
 UserMgr::GetUserInfo "${USER}" "EXISTS"
 Pop $0
 ${If} $0 == 'OK'
   DetailPrint "Result: exist"
   # if user exist, but service is not, we must recreate user and create service
   Goto cancel
 ${Else}
   DetailPrint "Result: do not exist"
   ${if} $action != ''
     StrCpy $user_not_exist 'true'
   ${endif}   
 ${EndIf}

 ; generate entropy
 pwgen::GeneratePassword 32
 Pop $0
 StrCpy $user_password $0
  
 DetailPrint "Create user ..."
 UserMgr::CreateAccountEx "${USER}" "$user_password" "${USER}" "${USER}" "${USER}" "UF_PASSWD_NOTREQD|UF_DONT_EXPIRE_PASSWD"
 Pop $0
 DetailPrint "CreateUser Result : $0"

 DetailPrint "Add privilege to user ..."
 UserMgr::AddPrivilege "${USER}" "SeServiceLogonRight"
 Pop $0
 DetailPrint "AddPrivilege Result: $0"

 DetailPrint "Add user ${USER} to Performance Logs User Group ..."
 UserMgr::AddToGroup "${USER}" "Performance Log Users" ; Performance Logs User Group to collect cpu/memory metrics
 Pop $0
 DetailPrint "AddToGroup Result: $0"
 cancel:
FunctionEnd

Function CreateConfig
 #rewrite all regfiles and installed files
 ;if up/downgrade/reinstall -> check config file existense
 ;if exist -> proceed with copying existing config
 ;if not exist -> rewrite config file with data from registry
 ;if not up/downgrade/install -> proceed to ;create config
 ${if} $action == 'downgrade'
 ${OrIf} $action == 'upgrade'

   ${if} ${FileExists} "$ext_inst_dir\${CONFIG_FILE}"
     ${ConfigRead} "$ext_inst_dir\${CONFIG_FILE}" "file =" $0 ; put log_file_name in $0
     DetailPrint "Copying config file to new install directory ..."
     CopyFiles "$ext_inst_dir\${CONFIG_FILE}" "$INSTDIR"
     ${ConfigWrite} "$INSTDIR\${CONFIG_FILE}" "file = " "$log_dir\${LOG_FILE}" $0
     StrCpy $5 "exist"
     Goto recreate_config
   ${else} ;do not exist
     Goto recreate_config
   ${endif}

 ${elseif} $action == 'reinstall'
   ${if} ${FileExists} "$ext_inst_dir\${CONFIG_FILE}"
     #if user decided to choose different log directory while reinstalling
     ${ConfigWrite} "$ext_inst_dir\${CONFIG_FILE}" "file = " "$log_dir\${LOG_FILE}" $0
     Goto cancel
   ${else}
     Goto recreate_config
   ${endif}
 ${else} ; fresh install
  Goto create_config
 ${endif}
 
 recreate_config:
 ReadRegStr $zb_address HKLM "${MAMONSU_REG_PATH}\$ext_version" "Zabbix host"
 ReadRegStr $zb_client HKLM "${MAMONSU_REG_PATH}\$ext_version" "Zabbix client name"
 ReadRegStr $zb_port HKLM "${MAMONSU_REG_PATH}\$ext_version" "Zabbix port"

 ReadRegStr $pg_host HKLM "${MAMONSU_REG_PATH}\$ext_version" "PostgreSQL host"
 ReadRegStr $pg_port HKLM "${MAMONSU_REG_PATH}\$ext_version" "PostgreSQL port"
 ReadRegStr $pg_user HKLM "${MAMONSU_REG_PATH}\$ext_version" "PostgreSQL user"
 ReadRegStr $pg_db HKLM "${MAMONSU_REG_PATH}\$ext_version" "PostgreSQL db"
 StrCpy $pg_password "None" ; user must rewrite password by himself

 create_config:
 ${if} $5 != 'exist' ; up/downgrade and file exist, so no need to create config
 ${AnsiToUtf8} $pg_password $2
 GetTempFileName $1
 FileOpen $0 $1 w
 FileWrite $0 '[zabbix]$\r$\nclient = $zb_client$\r$\naddress = $zb_address$\r$\nport = $zb_port$\r$\n$\r$\n\
[postgres]$\r$\nuser = $pg_user$\r$\ndatabase = $pg_db$\r$\npassword = $2$\r$\nhost = $pg_host$\r$\nport = $pg_port$\r$\n$\r$\n\
[log]$\r$\nfile = $log_dir\${LOG_FILE}$\r$\nlevel = INFO$\r$\n'
  FileClose $0
  Rename $1 "$INSTDIR\${CONFIG_FILE}"
 ${endif}

 AccessControl::DisableFileInheritance "$INSTDIR"
 AccessControl::DisableFileInheritance "$log_dir"

 ;set INSTALLDIR ownership to ${USER}
 AccessControl::SetFileOwner "$INSTDIR" "${USER}"
 Pop $0 ; "error" on errors
 DetailPrint "Change file owner to ${USER} : $0"
 AccessControl::GrantOnFile "$INSTDIR" "${USER}" "FullAccess" ; S-1-3-0 - owner

 ;revoke Users from INSTALLDIR and logs
 AccessControl::RevokeOnFile "$INSTDIR" "(S-1-5-32-545)" "FullAccess"
 AccessControl::RevokeOnFile "$log_dir" "(S-1-5-32-545)" "FullAccess"

 ;set logs directory owner
 AccessControl::SetFileOwner "$log_dir" "${USER}"
 Pop $0 ; "error" on errors
 DetailPrint "Change file owner to ${USER} : $0"
 AccessControl::GrantOnFile "$log_dir" "${USER}" "GenericRead + GenericWrite"
 AccessControl::GrantOnFile "$log_dir" "${USER}" "FullAccess"
 AccessControl::GrantOnFile "$log_dir" "${USER}" "AddFile"

 AccessControl::SetFileOwner "$INSTDIR\${SERVICE_FILE}" "${USER}"
 AccessControl::GrantOnFile "$INSTDIR\${SERVICE_FILE}" "(S-1-3-0)" "FullAccess"

 AccessControl::SetFileOwner "$INSTDIR\${CONFIG_FILE}" "${USER}"
 AccessControl::GrantOnFile "$INSTDIR\${CONFIG_FILE}" "(S-1-3-0)" "FullAccess"
 cancel:
FunctionEnd

Function CreateReg
 SetRegView 32
 WriteRegExpandStr HKLM "${MAMONSU_REG_PATH}" "Version" "${VERSION}"
 WriteRegExpandStr HKLM "${MAMONSU_REG_PATH}\${VERSION}" "User" "${USER}"
 WriteRegExpandStr HKLM "${MAMONSU_REG_PATH}\${VERSION}" "InstallDir" "$INSTDIR"
 WriteRegExpandStr HKLM "${MAMONSU_REG_PATH}\${VERSION}" "LogDir" "$log_dir"
 WriteRegExpandStr HKLM "${MAMONSU_REG_PATH}\${VERSION}" "Zabbix host" "$zb_address"
 WriteRegExpandStr HKLM "${MAMONSU_REG_PATH}\${VERSION}" "Zabbix port" "$zb_port"
 WriteRegExpandStr HKLM "${MAMONSU_REG_PATH}\${VERSION}" "Zabbix client name" "$zb_client"

 WriteRegExpandStr HKLM "${MAMONSU_REG_PATH}\${VERSION}" "PostgreSQL host" "$pg_host"
 WriteRegExpandStr HKLM "${MAMONSU_REG_PATH}\${VERSION}" "PostgreSQL port" "$pg_port"
 WriteRegExpandStr HKLM "${MAMONSU_REG_PATH}\${VERSION}" "PostgreSQL user" "$pg_user"
 WriteRegExpandStr HKLM "${MAMONSU_REG_PATH}\${VERSION}" "PostgreSQL db" "$pg_db"

 WriteRegExpandStr HKLM "${MAMONSU_REG_UNINSTALLER_PATH}\${NAME}" "InstallLocation" "$INSTDIR"
 WriteRegExpandStr HKLM "${MAMONSU_REG_UNINSTALLER_PATH}\${NAME}" "DisplayName" "${NAME} ${VERSION}"
 WriteRegExpandStr HKLM "${MAMONSU_REG_UNINSTALLER_PATH}\${NAME}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
 WriteRegExpandStr HKLM "${MAMONSU_REG_UNINSTALLER_PATH}\${NAME}" "DisplayVersion" "${VERSION}"
 WriteRegExpandStr HKLM "${MAMONSU_REG_UNINSTALLER_PATH}\${NAME}" "Publisher" "Postgres Professional"
 WriteRegExpandStr HKLM "${MAMONSU_REG_UNINSTALLER_PATH}\${NAME}" "HelpLink" "http://github.com/postgrespro/mamonsu"
 WriteRegExpandStr HKLM "${MAMONSU_REG_UNINSTALLER_PATH}\${NAME}" "Comments" "Packaged by PostgresPro.ru"
 WriteRegExpandStr HKLM "${MAMONSU_REG_UNINSTALLER_PATH}\${NAME}" "UrlInfoAbout" "http://github.com/postgrespro/mamonsu"

 ${if} $action == 'upgrade'
 ${orif} $action == 'downgrade'
   DetailPrint "Delete old registry entry ..."
   SetRegView 32
   DeleteRegKey HKLM "${MAMONSU_REG_PATH}\$ext_version"
 ${endif}
FunctionEnd

Function CreateService
 ${if} $action != ''
   SimpleSC::ExistsService "${SERVICE_NAME}"
   Pop $0
   ${if} $0 == 0 ; service exist  
     DetailPrint "Service already exist"
      ${if} $user_not_exist == 'true' ; service exist and user was recreated, we forced to drop and recreate service
       DetailPrint "User was recreated so we forced to recreate service"
       DetailPrint "Removing service ..."
       SimpleSC::RemoveService "${SERVICE_NAME}"
       Pop $0 
        ${if} $0 == 0 ; service deleted
         DetailPrint "Result RemoveService: ok"
        ${else}
         DetailPrint "Result RemoveService: error"
        ${endIf}
      ${else} ; service exist but user was not recreated, so its ok to exit
        ${if} $action == 'upgrade'
        ${OrIf} $action == 'downgrade'
         DetailPrint "It`s upgrade/downgrade, service must be updated to reflect new path to binary"
         DetailPrint "Updating service ..."
         nsExec::ExecToStack /TIMEOUT=10000 '"$INSTDIR\${SERVICE_FILE}" update'
         Pop $0
         Pop $1
          ${if} $0 == 0
           DetailPrint "Result: ok"
          ${elseif} $0 == 'error'
           DetailPrint "Result: error"
           DetailPrint "$1"
          ${elseif} $0 == 'timeout'
           DetailPrint "Result: timeout"
          ${endif}
         Goto cancel
        ${elseif} $action == 'reinstall'
         DetailPrint "Service exist and user was not recreated, so its ok to use existing service"
         Goto cancel
        ${endif}
     ${endif}
    ${endif}
  ${endif} 
 DetailPrint "Creating service ${SERVICE_NAME} ... "
 nsExec::ExecToStack /TIMEOUT=10000 '"$INSTDIR\${SERVICE_FILE}" --username "$hostname\${USER}" --password "$user_password" --startup delayed install'
 Pop $0
 Pop $1
 ${if} $0 == 0
   DetailPrint "Result: ok"
 ${elseif} $0 == 'error'
   DetailPrint "Result: error"
   DetailPrint "$1"
 ${elseif} $0 == 'timeout'
  DetailPrint "Result: timeout"
 ${endif}
 cancel:
FunctionEnd

Function StopService
 DetailPrint "Stoping service ${SERVICE_NAME} ... "
 SimpleSC::StopService "${SERVICE_NAME}" 1 "30"
 Pop $0
 ${If} $0 == '0'
   DetailPrint "Result: ok"
 ${Else}
   DetailPrint "Result: error"
 ${EndIf}
FunctionEnd
 
Function StartService
 DetailPrint "Starting service ${SERVICE_NAME} ... "
 SimpleSC::StartService "${SERVICE_NAME}" "" "30"
 Pop $0
 ${If} $0 == '0'
   DetailPrint "Result: ok"
 ${Else}
   DetailPrint "Result: error"
   MessageBox MB_OK "Service ${SERVICE_NAME} failed to start"
 ${EndIf}
FunctionEnd

Function DeleteDirectory
 ${if} $action == 'reinstall'
 Goto compare_log_dirs
 ${endif}
 ${if} $action == 'downgrade'
 ${orif} $action == 'upgrade'
   DetailPrint "Deleting old install directory ..."
   Delete "$ext_inst_dir\${SERVICE_FILE}"
   Delete "$ext_inst_dir\${CONFIG_FILE}"
   Delete "$ext_inst_dir\${EXE_FILE}"
   ${if} ${FileExists} "$ext_inst_dir\${OLD_EXE_FILE}"
    Delete "$ext_inst_dir\${OLD_EXE_FILE}"
   ${endIf}
   Delete "$ext_inst_dir\${TEMPLATE_FILE}"
   Delete "$ext_inst_dir\Uninstall.exe"
   compare_log_dirs:
   ${if} $ext_log_dir != $log_dir
     Delete "$ext_log_dir\${LOG_FILE}"
     RMDir "$ext_log_dir"
   ${endif}
   RMDir "$ext_inst_dir"
 ${endif}  
FunctionEnd

;----------------------------------------------
; Uninstall functions
Function un.CheckExist
 ;добавить проверку директории
 ReadRegStr $ext_log_dir HKLM "${MAMONSU_REG_PATH}\${VERSION}" "LogDir"
FunctionEnd

Function un.DeleteService
 DetailPrint "Stoping service ${SERVICE_NAME} ... "
 SimpleSC::StopService "${SERVICE_NAME}" 1 "30"
 Pop $0
 ${If} $0 == '0'
   DetailPrint "Result: ok"
 ${Else}
   DetailPrint "Result: error"
 ${EndIf}

 #remove service
 DetailPrint "Removing service mamonsu ..."
 nsExec::ExecToStack '"$INSTDIR\${SERVICE_FILE}" remove'
 Pop $0
 Pop $1
 ${if} $0 == 0
   DetailPrint "Result: ok"
 ${elseif} $0 == 'timeout'
   DetailPrint "Result: $0"
 ${elseif} $0 == 'error'
   DetailPrint "Result: $0"
   DetailPrint "$1"
 ${endif}
FunctionEnd

Function un.DeleteUser
 DetailPrint "Delete user ${USER} ..."
 UserMgr::GetUserInfo "${USER}" "HOMEDIR"
 Pop $0
 
 UserMgr::GetSIDFromUserName "$hostname" "${USER}"
 Pop $0

 ReadRegStr $1 HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\$0" "ProfileImagePath"
 Pop $1
 StrCpy $9 $1

 UserMgr::DeleteAccount "${USER}"
 Pop $0
 DetailPrint "DeleteUser Result : $0"

 RMDir /r $9
FunctionEnd  

Function un.DeleteReg
 DetailPrint "Delete registry entry ..."
 SetRegView 32
 DeleteRegKey HKLM "${MAMONSU_REG_UNINSTALLER_PATH}\${NAME}"
 DeleteRegKey /ifempty HKLM "${MAMONSU_REG_UNINSTALLER_PATH}\${NAME}"
 DeleteRegKey HKLM "${MAMONSU_REG_PATH}"
FunctionEnd

Function un.DeleteDirectory
 Delete "$INSTDIR\${CONFIG_FILE}"
 Delete "$INSTDIR\${EXE_FILE}"
 Delete "$INSTDIR\${SERVICE_FILE}"
 Delete "$INSTDIR\${TEMPLATE_FILE}"
 Delete "$INSTDIR\Uninstall.exe"
 Delete "$ext_log_dir\${LOG_FILE}"
 RMDir "$ext_log_dir"
 RMDir "$INSTDIR"
FunctionEnd

;Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SectionMS} $(DESC_SectionMS)
!insertmacro MUI_DESCRIPTION_TEXT ${SectionMamonsu} $(DESC_SectionMamonsu)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
