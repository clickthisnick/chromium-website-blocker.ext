#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Must pass text, times, delay for popup"
    exit 2
fi

# Re-spawn as a background process, if we haven't already.
# if [[ "$1" != "-n" ]]; then
#     nohup "$0" -n &
#     exit $?
# fi

# 1 = text
# 2 = times
# 3 = delay

# Rest of the script follows. This is just an example.
for ((i=1; i<=${2}; i++))
do

    sleep ${3}
/usr/bin/osascript <<-EOF

    tell application "System Events"
        activate
        display dialog "${i}/${2} - ${1}"
    end tell

EOF
done
