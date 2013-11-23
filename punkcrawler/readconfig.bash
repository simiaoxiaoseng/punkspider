#!/bin/bash

IFS="="
while read -r name value
do
if [[ -z "$value" ]]; then
  value=None
else
  valstripped=`echo $value | cut -f1 -d"#"`
  eval $name=${valstripped//\"[]/}
fi
done < punkcrawler.cfg