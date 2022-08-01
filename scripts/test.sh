#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source "$SCRIPT_DIR/utils.sh"

DELAY_BETWEEN_TESTS=5
testNo=0

function incTest(){
    testNo=$((testNo + 1))
    echo "$testNo"
}

function nextTest(){
    local delay="${1:-$DELAY_BETWEEN_TESTS}"
    local testNo=$1
    sleep "$delay"
    clearDisplay
    echo
    echo
    echo
    echo "Test $testNo"
}

function end(){
    sleep "$DELAY_BETWEEN_TESTS"
    echo 'Tests complete.'
    clearDisplay
}

declare -a TESTS

incTest
TESTS=("${TESTS[@]}" "test_$testNo")
function test_1() {
    nextTest 1
    echo 'All red'
    setAndDrawAll 255 0 0
}


incTest
TESTS=("${TESTS[@]}" "test_$testNo")
function test_2() {
    nextTest 2
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
}


incTest
TESTS=("${TESTS[@]}" "test_$testNo")
function test_3(){
    nextTest 3
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
}

incTest
TESTS=("${TESTS[@]}" "test_$testNo")
function test_4(){
    nextTest 4
    echo 'User defined segments (UDS). UDS use fading.'
    for (( i=0; i<LED_COUNT; i++ )); do
        index=$((i + LED_COUNT))
        echo "($i, $index) on"
        echo "$index 255 0 0" > "$PRU_SYSFS"
        draw
        sleep 0.1
        echo "($i, $index) off"
        echo "$index 0 0 0" > "$PRU_SYSFS"
    done
}


incTest
TESTS=("${TESTS[@]}" "test_$testNo")
function test_5() {
    nextTest 5
    local blinkCount=10
    echo "Use user defined segment to blink last LED $blinkCount times"
    for (( i=0; i<blinkCount; i++ )); do
        index=$(((LED_COUNT - 1) + LED_COUNT))
        echo "$index on"
        echo "$index 255 0 0" > "$PRU_SYSFS"
        draw
        sleep 1
        echo "($index) off"
        echo "$index 0 0 0" > "$PRU_SYSFS"
    done
}

for i in "${!TESTS[@]}"; do   ${TESTS[$i]}; done

end
