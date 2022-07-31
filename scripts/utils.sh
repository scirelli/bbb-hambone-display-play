#!/usr/bin/env bash

function setAllFast() {
    r=$1
    g=$2
    b=$3
    echo "$SEGMENT_ONE $r $g $b" > "$PRU_SYSFS"
    echo -1 0 0 0 > "$PRU_SYSFS"
}

function setAll() {
    r=$1
    g=$2
    b=$3
	for (( i=0; i<=LED_COUNT; i++ )); do
            echo "$i $r $g $b" > "$PRU_SYSFS"
    done

    echo -1 0 0 0 > "$PRU_SYSFS"
}

function clearDisplay2() {
	echo -2 0 0 0 > "$PRU_SYSFS"
}

function clearDisplay() {
	for (( i=0; i<=LED_COUNT; i++ )); do
		echo "$i 0 0 0" > "$PRU_SYSFS"
	done

	echo -1 0 0 0 > "$PRU_SYSFS"
}
