class Scripts(object):
    Bash = {
        # name_of_script: 'script '
        "disk_sizes":
            """#!/bin/bash
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

         """,

        'disk_stats':
            """#!/bin/bash
 IFS_DEFAULT="${IFS}"
 #
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

 output=" "
 rval=`cat /proc/diskstats`
 if [[ ${JSON} -eq 1 ]]; then
     echo '{'
     echo '   "data":['
     count=1
     value=0
     while read line; do
        if [[ ${line} != '' ]]; then
             IFS="|" values=(${line})

             if [[ $count == 1 ]]; then    # for loop0 case
                 new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                 new_value3=`echo "$new_value2" | cut -d " " -f 3`
                 read_op=`echo "$new_value2" | cut -d " " -f 4`
                 read_sc=`echo "$new_value2" | cut -d " " -f 6`
                 write_op=`echo "$new_value2" | cut -d " " -f 8`
                 write_sc=`echo "$new_value2" | cut -d " " -f 10`
                 ticks=`echo "$new_value2" | cut -d " " -f 13`
             else
                 new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                 new_value3=`echo "$new_value2" | cut -d " " -f 4`
                 read_op=`echo "$new_value2" | cut -d " " -f 5`
                 read_sc=`echo "$new_value2" | cut -d " " -f 7`
                 write_op=`echo "$new_value2" | cut -d " " -f 9`
                 write_sc=`echo "$new_value2" | cut -d " " -f 11`
                 ticks=`echo "$new_value2" | cut -d " " -f 14`
             fi
             if [[ $new_value3 != *"loop"* ]]  &&  [[ $new_value3 != *"ram"* ]] && [[ $new_value3 != *[0-9]* ]]; then
                 if [[ ${output} != " " ]]; then
                 echo "      ${output}"
                 fi
                 value=$(($read_op+$value))
                  output='{ '
                  output+='"'{#${JSON_ATTR[0]}}'"'
                  output+=':'
                  output+='"'$new_value3'"'
                  output+=' }'
                  tmp="${output}"
                 output="${output},"
             fi
           fi
         let "count=count+1"
     done <<< ${rval}
     echo "      ${tmp}"
     echo '   ]'
     echo '}'
 else
     echo "${rval:-0}"
 fi

 exit ${rcode}
 """,

        'disk_stats_read_op':
            """#!/bin/bash
rval=`cat /proc/diskstats`

count=1
value=0
while read line; do
       if [[ ${line} != '' ]]; then
            IFS="|" values=(${line})

            if [[ $count == 1 ]]; then    # for loop0 case
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                # echo $new_value2
                new_value3=`echo "$new_value2" | cut -d " " -f 3`
                read_op=`echo "$new_value2" | cut -d " " -f 4`

            else
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                new_value3=`echo "$new_value2" | cut -d " " -f 4`
                read_op=`echo "$new_value2" | cut -d " " -f 5`

            fi
            re='^[0-9]+$'
            has_digits='no'
            if [[ "${new_value3: -1}" =~ $re ]]; then
                  has_digits='yes'
            fi
            if [[ $new_value3 != *"loop"* ]]  &&  [[ $new_value3 != *"ram"* ]] &&  [[ $has_digits == 'no' ]]; then
                value=$(($read_op+$value))


            fi
          fi
    let "count=count+1"
done <<< ${rval}
echo $(($value))

""",

        'disk_stats_read_b':
            """#!/bin/bash
rval=`cat /proc/diskstats`

count=1
value=0
while read line; do
       if [[ ${line} != '' ]]; then
            IFS="|" values=(${line})

            if [[ $count == 1 ]]; then    # for loop0 case
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                # echo $new_value2
                new_value3=`echo "$new_value2" | cut -d " " -f 3`
                read_sc=`echo "$new_value2" | cut -d " " -f 6`
            else
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                new_value3=`echo "$new_value2" | cut -d " " -f 4`
                read_sc=`echo "$new_value2" | cut -d " " -f 7`
            fi
            re='^[0-9]+$'
            has_digits='no'
            if [[ "${new_value3: -1}" =~ $re ]]; then
                  has_digits='yes'
            fi
            if [[ $new_value3 != *"loop"* ]]  &&  [[ $new_value3 != *"ram"* ]] &&  [[ $has_digits == 'no' ]]; then
                value=$(($read_sc+$value))
            fi
          fi
    let "count=count+1"
done <<< ${rval}
echo $(($value*512))

""",

        'disk_stats_write_op':
            """#!/bin/bash
rval=`cat /proc/diskstats`

count=1
value=0
while read line; do
       if [[ ${line} != '' ]]; then
            IFS="|" values=(${line})

            if [[ $count == 1 ]]; then    # for loop0 case
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                new_value3=`echo "$new_value2" | cut -d " " -f 3`
                write_op=`echo "$new_value2" | cut -d " " -f 8`

            else
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                new_value3=`echo "$new_value2" | cut -d " " -f 4`

                write_op=`echo "$new_value2" | cut -d " " -f 9`

            fi
            re='^[0-9]+$'
            has_digits='no'
            if [[ "${new_value3: -1}" =~ $re ]]; then
                  has_digits='yes'
            fi
            if [[ $new_value3 != *"loop"* ]]  &&  [[ $new_value3 != *"ram"* ]] &&  [[ $has_digits == 'no' ]];then
                #echo $write_op

                value=$(($write_op+$value))


            fi
          fi
    let "count=count+1"
done <<< ${rval}
echo $(($value))
""",

        'disk_stats_write_b':
            """#!/bin/bash
rval=`cat /proc/diskstats`

count=1
value=0
while read line; do
       if [[ ${line} != '' ]]; then
            IFS="|" values=(${line})

            if [[ $count == 1 ]]; then    # for loop0 case
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                new_value3=`echo "$new_value2" | cut -d " " -f 3`
                write_sc=`echo "$new_value2" | cut -d " " -f 10`
            else
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                new_value3=`echo "$new_value2" | cut -d " " -f 4`
                write_sc=`echo "$new_value2" | cut -d " " -f 11`
            fi
            re='^[0-9]+$'
            has_digits='no'
            if [[ "${new_value3: -1}" =~ $re ]]; then
                  has_digits='yes'
            fi
            #echo $values
            if [[ $new_value3 != *"loop"* ]]  &&  [[ $new_value3 != *"ram"* ]] &&  [[ $has_digits == 'no' ]]; then
                #echo $write_sc
                #echo $new_value3
                value=$(($write_sc+$value))
            fi
          fi
    let "count=count+1"
done <<< ${rval}
echo $(($value*512))
    """,
        'net':
            """#!/bin/bash


#################################################################################
while getopts "s::a:sj:uphvt:" OPTION; do
    case ${OPTION} in

        j)
            JSON=1
            JSON_ATTR=(${OPTARG})

            ;;
    esac
done
#################################################################################
  rval=$(cat /proc/net/dev)
  output=" "

if [[ ${JSON} -eq 1 ]]; then
    echo '{'
    echo '   "data":['
    count=1
    while read line; do
        values=(${line})
            if [[ "${values[0]}" != *"lo:"* ]] && [[ "${#values[@]}">1 ]]; then
            if [[ ${output} != " " ]] && [[ $count > 4 ]]; then
                echo "      ${output}"
                fi
                 output='{ '
                 output+='"'{#${JSON_ATTR[0]}}'"'
                 output+=':'
                 t="${values[0]}"
                 output+='"'${t%?}'"'
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

""",

        'disk_stats_ticks':
            """#!/bin/bash
rval=`cat /proc/diskstats`

count=1
value=0
while read line; do
       if [[ ${line} != '' ]]; then
            IFS="|" values=(${line})

            if [[ $count == 1 ]]; then    # for loop0 case
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                # echo $new_value2
                new_value3=`echo "$new_value2" | cut -d " " -f 3`
                ticks=`echo "$new_value2" | cut -d " " -f 13`
            else
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \\+/ /gp'`
                new_value3=`echo "$new_value2" | cut -d " " -f 4`
                ticks=`echo "$new_value2" | cut -d " " -f 14`
            fi
            if [[ $new_value3 != *"loop"* ]]  &&  [[ $new_value3 != *"ram"* ]]; then
                #echo $ticks
                value=$(($ticks+$value))
            fi
          fi
    let "count=count+1"
done <<< ${rval}
echo $(($value))
    """
    }
