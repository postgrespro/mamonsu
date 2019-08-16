#!/bin/bash
PATH=/usr/local/bin:${PATH}
IFS_DEFAULT="${IFS}"

contains() {
  [[ $1 =~ (^|${2})"${3}"($|${2}) ]] && echo "1" || echo "0"
}

#################################################################################

while getopts "s::a:sj:uphvt:" OPTION; do
    case ${OPTION} in
 
    j)
            JSON=1
            JSON_ATTR=(${OPTARG})
            IFS="${IFS_DEFAULT}"
            ;;
    
    esac
done

#################################################################################

  rval=$(cat /proc/self/mountinfo)
    exclude_list=("none" "unknown" "rootfs" "iso9660"
        "squashfs" "udf" "romfs" "ramfs"
        "debugfs" "cgroup" "cgroup_root"
        "pstore" "devtmpfs" "autofs"
        "cgroup" "configfs" "devpts"
        "efivarfs" "fusectl" "fuse.gvfsd-fuse"
        "hugetlbfs" "mqueue"
        "nfsd" "proc" "pstore"
        "rpc_pipefs" "securityfs" "sysfs"
        "nsfs" "tmpfs" "tracefs")
   list_str=$(IFS=","; echo "${exclude_list[*]}")
output=" "

if [[ ${JSON} -eq 1 ]]; then
    echo '{'
    echo '   "data":['
    count=1
    while read line; do
        values=(${line})
            if [ $(contains "${list_str}" "," "${values[8]}") -eq 0 ]; then    
            if [[ ${output} != " " ]]; then
                echo "      ${output}"
                fi        
                 output='{ '
                 output+='"'{#${JSON_ATTR[0]}}'"'
                 output+=':'
                 output+='"'${values[4]}'"'
                 output+=' }'
                 tmp="${output}"
                 output="${output},"
            fi        
        let "count=count+1"
    done <<< "${rval}"
    echo "      ${tmp}"
    echo '   ]'
    echo '}'
else
    echo "${rval:-0}"
fi

exit ${rcode}

         