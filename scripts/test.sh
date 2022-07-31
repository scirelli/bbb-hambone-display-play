#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source "$SCRIPT_DIR/variables.sh"
source "$SCRIPT_DIR/utils.sh"

test=0

function nextTest(){
    sleep 2
    clearDisplay
    test=$((test + 1))
    echo
    echo
    echo
    echo "Test $test"
}

function end(){
    sleep 5
    clearDisplay
}

nextTest
echo 'All red'
setAll 255 0 0


nextTest
echo 'Segment test'
echo '1=RED, 2=GREEN, 3=BLUE'
echo "121 255 0 0" > "$PRU_SYSFS"
echo "122 0 255 0" > "$PRU_SYSFS"
echo "123 0 0 255" > "$PRU_SYSFS"
draw

echo 'Transition To: 1=BLUE, 2=RED, 3=GREEN'
echo 'After 1 second'
sleep 1
echo "121 0 0 255" > "$PRU_SYSFS"
echo "122 255 0 0" > "$PRU_SYSFS"
echo "123 0 255 0" > "$PRU_SYSFS"
draw


nextTest
echo 'User defined segments (UDS). UDS use fading.'
for (( i=0; i<=LED_COUNT; i++ )); do
    index=$((i + LED_COUNT))
    echo "($i, $index) on"
    echo "$index 255 0 0" > "$PRU_SYSFS"
    draw
    sleep 1
    echo "($i, $index) off"
    echo "$index 0 0 0" > "$PRU_SYSFS"
done

end
