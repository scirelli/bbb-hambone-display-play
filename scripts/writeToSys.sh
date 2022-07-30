#!/usr/bin/env bash
PRU_SYSFS=/dev/rpmsg_pru30
LED_COUNT=42

echo 'Test 1'
clearDisplay

echo "120 255 0 0" > "$PRU_SYSFS"
echo "121 0 255 0" > "$PRU_SYSFS"
echo "122 0 0 255" > "$PRU_SYSFS"
echo -1 0 0 0 > "$PRU_SYSFS"
sleep 1
echo "120 0 0 255" > "$PRU_SYSFS"
echo "121 255 0 0" > "$PRU_SYSFS"
echo "122 0 255 0" > "$PRU_SYSFS"
echo -1 0 0 0 > "$PRU_SYSFS"


function clearDisplay() {
	for (( i=0; i<=$LED_COUNT; i++ )); do
		echo "$i 0 0 0" > "$PRU_SYSFS"
	done

	echo -1 0 0 0 > "$PRU_SYSFS"
}
