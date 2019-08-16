#!/bin/bash


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

