#!/bin/bash
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
                 new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \+/ /gp'`
                 new_value3=`echo "$new_value2" | cut -d " " -f 3`
                 read_op=`echo "$new_value2" | cut -d " " -f 4`
                 read_sc=`echo "$new_value2" | cut -d " " -f 6`
                 write_op=`echo "$new_value2" | cut -d " " -f 8`
                 write_sc=`echo "$new_value2" | cut -d " " -f 10`
                 ticks=`echo "$new_value2" | cut -d " " -f 13`
             else
                 new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \+/ /gp'`
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
 