#!/bin/bash

echo "press CTRL-C to stop." ;

# remove screenshot after {x} seconds
interval=1
number_of_image_rm=5 ; # remove {y} images
rm_screenshot_after=10 ; # start remove image after {x} seconds
screenshot_rm_timeout=0 ; # counter
for (( ; ; ))
do
  ((screenshot_rm_timeout+=1)) ;
  current_unix_second=$(date +%s) ;
  # echo "$current_unix_second"
  if [ $screenshot_rm_timeout -eq rm_screenshot_after ]
  then
    remove_from=$((current_unix_second - rm_screenshot_after + 1)) ;
    remote_end=$((remove_from + number_of_image_rm - 1)) ;
    echo "Start remove image from ${remove_from} to ${remove_end}" ;
    eval rm -f "/home/highside/screen/{$remove_from..$remote_end}.jpeg" ;
    ((screenshot_rm_timeout=0)) ;
  fi
  sleep "${interval}" ;
done
