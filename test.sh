#!/bin/bash
# http://matelight.rocks

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
    done > buffer.crap;
    j=$(($j+23));
    cat buffer.crap > /dev/udp/127.0.0.1/1337;
    echo $j
done
