#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source "$SCRIPT_DIR/variables.sh"
source "$SCRIPT_DIR/utils.sh"

clearDisplay

echo 'Test 1'
echo '1=RED, 2=GREEN, 3=BLUE'
echo "121 255 0 0" > "$PRU_SYSFS"
echo "122 0 255 0" > "$PRU_SYSFS"
echo "123 0 0 255" > "$PRU_SYSFS"
echo -1 0 0 0 > "$PRU_SYSFS"

echo 'Transition To'
echo '1=BLUE, 2=RED, 3=GREEN'
echo 'After 1 second'
sleep 1
echo "121 0 0 255" > "$PRU_SYSFS"
echo "122 255 0 0" > "$PRU_SYSFS"
echo "123 0 255 0" > "$PRU_SYSFS"
echo -1 0 0 0 > "$PRU_SYSFS"
