#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source "$SCRIPT_DIR/variables.sh"
source "$SCRIPT_DIR/utils.sh"

DELAY_BETWEEN_TESTS=5
test=0

function nextTest(){
    local delay="${1:-$DELAY_BETWEEN_TESTS}"
    sleep "$delay"
    clearDisplay
    test=$((test + 1))
    echo
    echo
    echo
    echo "Test $test"
}

function end(){
    sleep "$DELAY_BETWEEN_TESTS"
    clearDisplay
}



nextTest 0
echo 'All red'
setAndDrawAll 255 0 0



nextTest
echo 'Segment test'
echo 'Segment 1=RED'
setSegment 1 255 0 0
echo 'Segment 2=GREEN'
setSegment 2 0 255 0
echo 'Segment 3=BLUE'
setSegment 3 0 0 255
draw

echo 'Transition To: 1=BLUE, 2=RED, 3=GREEN'
echo 'After 1 second'
sleep 1
setSegment 1 0 0 255
setSegment 2 255 0 0
setSegment 3 0 255 0
draw



nextTest
echo 'Test bounds'
echo 'Fade first pixel to red'
index=$((0 + LED_COUNT))
echo "(0, $index) on"
echo "$index 255 0 0" > "$PRU_SYSFS"
draw
echo 'Fade last pixel to red'
index=$((LED_COUNT + (LED_COUNT - 1)))
echo "($((LED_COUNT - 1)), $index) on"
echo "$index 255 0 0" > "$PRU_SYSFS"
draw



nextTest
echo 'User defined segments (UDS). UDS use fading.'
for (( i=0; i<LED_COUNT; i++ )); do
    index=$((i + LED_COUNT))
    echo "($i, $index) on"
    echo "$index 255 0 0" > "$PRU_SYSFS"
    draw
    sleep 1
    echo "($i, $index) off"
    echo "$index 0 0 0" > "$PRU_SYSFS"
done



end
