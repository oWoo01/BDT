#!/usr/bin/bash

for dir in */; do
    folder=${dir%/}
    echo $folder
    if [ "$folder" == "input" ]; then
        continue
    fi

    python process.py "$folder" > $folder/proc-log 2>&1 &
done
