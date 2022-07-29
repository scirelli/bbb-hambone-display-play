#!/usr/bin/env bash
for i in {0..42}; do
        echo "$i 0 0 0" > /dev/rpmsg_pru30
done

echo -1 0 0 0 > /dev/rpmsg_pru30
