#!/bin/bash

trap_ctrlc()
{
  PID="${1}"
  kill $PID
  echo "stop screen_rm"
  exit
}

interval=1
echo "Capturing a screenshot every ${interval} seconds."
echo "press CTRL-C to stop."

# Take a screenshot every ${interval} seconds of the current window
./screenshot_rm.sh &
PID=$!
echo $PID
trap "trap_ctrlc '${PID}'" SIGINT
for (( ; ; ))
do
  current_unix_second=$(date +%s)
  scrot "/home/suna/screen/${current_unix_second}.jpeg" -q 70
  sleep "${interval}"
done
