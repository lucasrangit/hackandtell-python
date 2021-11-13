#!/bin/bash

OUT=$(mktemp) || { echo "Failed to create temp file"; exit 1; }

j=0;
while true; do
    for y in `seq 1 16`; do
        for x in `seq 1 40`; do
            #red
            printf "\x$(printf "%x" "$((($x+$j)%255))")";
            #green
            printf "\x$(printf "%x" "$((($x+$y+$j)%255))")";
            #blue
            printf "\x$(printf "%x" "$((($y+$j)%255))")";
        done
    done > $OUT;
    j=$(($j+23));
    cat $OUT > /dev/udp/127.0.0.1/1337;
    echo $j
done
