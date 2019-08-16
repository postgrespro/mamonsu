#!/bin/bash
rval=`cat /proc/diskstats`

count=1
value=0
while read line; do
       if [[ ${line} != '' ]]; then
            IFS="|" values=(${line})

            if [[ $count == 1 ]]; then    # for loop0 case          
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \+/ /gp'`
                # echo $new_value2
                new_value3=`echo "$new_value2" | cut -d " " -f 3`
                ticks=`echo "$new_value2" | cut -d " " -f 13`
            else
                new_value2=`echo ${values[0]} | sed -n '/[0-9]/s/ \+/ /gp'`
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
    