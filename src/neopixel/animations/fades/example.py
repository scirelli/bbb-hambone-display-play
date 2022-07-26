#!/usr/bin/env python3
import math
from time import sleep

len = 42
amp = 12
f = 44
shift = 3
phase = 0
x = 0
# Open a file
fo = open("/tmp/example_rainbow.txt", "wb", 0)  # Write binary unbuffered

while x < 10*len:
    for i in range(0, len):
        r = (amp * (math.cos(2*math.pi*f*(i-phase-0*shift)/len) + 1)) + 1
        g = (amp * (math.cos(2*math.pi*f*(i-phase-1*shift)/len) + 1)) + 1
        b = (amp * (math.cos(2*math.pi*f*(i-phase-2*shift)/len) + 1)) + 1
        fo.write("%d %d %d %d\n".encode("utf-8") % (i, r, g, b))
        # print("0 0 127 %d" % (i))
    x = x + 1
    fo.write("-1 0 0 0\n".encode("utf-8"));
    phase = phase + 1
    sleep(0.1)

for i in range(0, len):
    r = 0
    g = 0
    b = 0
    fo.write("%d %d %d %d\n".encode("utf-8") % (i, r, g, b))
fo.write("-1 0 0 0\n".encode("utf-8"))

# Close opened file
fo.close()
