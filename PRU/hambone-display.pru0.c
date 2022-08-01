////////////////////////////////////////
//	neopixelRpmsg.c
//	Uses rpmsg to control the NeoPixels via /dev/rpmsg_pru30 on the ARM
//	Usage:	echo index R G B > /dev/rpmsg_pru30 to set the color at the given index
//			echo -1 0 0 0    > /dev/rpmsg_pru30 to update the string
//			echo 0 0xf0 0 0  > /dev/rpmsg_pru30 Turns pixel 0 to Red
//			neopixelRainbow.py to display moving rainbow pattern
//	Wiring:	The NeoPixel Data In goes to P9_29, the plus lead to P9_3 or P9_4
//			and the ground to P9_1 or P9_2.  If you have more then 40 some
//			NeoPixels you will need and external supply.
//	Setup:	config_pin P9_29 pruout
//	See:
//	PRU:	pru0
////////////////////////////////////////
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>			// atoi
#include <string.h>
#include <stdbool.h>
#include <pru_cfg.h>
#include <pru_intc.h>
#include <rsc_types.h>
#include <pru_rpmsg.h>
#include "resource_table_0.h"
#include "prugpio.h"

volatile register uint32_t __R30;
volatile register uint32_t __R31;

/* Host-0 Interrupt sets bit 30 in register R31 */
#define HOST_INT			((uint32_t) 1 << 30)

/* The PRU-ICSS system events used for RPMsg are defined in the Linux device tree
 * PRU0 uses system event 16 (To ARM) and 17 (From ARM)
 * PRU1 uses system event 18 (To ARM) and 19 (From ARM)
 * Be sure to change the values in resource_table_0.h too.
 */
#define TO_ARM_HOST			16
#define FROM_ARM_HOST		17

/*
* Using the name 'rpmsg-pru' will probe the rpmsg_pru driver found
* at linux-x.y.z/drivers/rpmsg/rpmsg_pru.c
*/
#define CHAN_NAME			"rpmsg-pru"
#define CHAN_DESC			"Channel 30"
#define CHAN_PORT			30

/*
 * Used to make sure the Linux drivers are ready for RPMsg communication
 * Found at linux-x.y.z/include/uapi/linux/virtio_config.h
 */
#define VIRTIO_CONFIG_S_DRIVER_OK	4

char payload[RPMSG_BUF_SIZE];

#define STR_LEN             42                          // Number of pixels
#define NANO_SEC_PER_CYCLE  5
#define	oneCyclesOn		    700/NANO_SEC_PER_CYCLE	    // Stay on for 700ns
#define oneCyclesOff	    600/NANO_SEC_PER_CYCLE
#define zeroCyclesOn	    350/NANO_SEC_PER_CYCLE
#define zeroCyclesOff   	800/NANO_SEC_PER_CYCLE
#define resetCycles		    70000/NANO_SEC_PER_CYCLE    // Must be at least 50u, use 51u. 70us seems to be the sweet spot

#define PREDEFINED_SEGMENT_COUNT 4

#define CODE_DRAW                                   -1
#define CODE_CLEAR                                  -2
#define CODE_DESTINATION_BUFFER_WRITE_START_INDEX   STR_LEN                                                             // For user defined fades
#define CODE_DESTINATION_BUFFER_WRITE_END_INDEX     (STR_LEN + (STR_LEN - 1))
#define CODE_DEFAULT_SEGMENT_START_INDEX            (CODE_DESTINATION_BUFFER_WRITE_END_INDEX + 1)                         // For built in entire segment fades
#define CODE_DEFAULT_SEGMENT_END_INDEX              (CODE_DEFAULT_SEGMENT_START_INDEX + (PREDEFINED_SEGMENT_COUNT - 1))

#define DELTA_US(start, stop) (((stop).tv_sec - (start).tv_sec) * 1000000 + ((stop).tv_usec - (start).tv_usec))
#define DELTA_MS(start, stop) (DELTA_US((start), (stop))/1000)
#define RED(color)            (((color) & 0x0000FF00) >> 8)
#define GREEN(color)          (((color) & 0x00FF0000) >> 16)
#define BLUE(color)           (((color) & 0x000000FF) >> 0)
#define PACK_COLOR(r, g, b)   (((g)<<16)|((r)<<8)|(b))

#define FADE_SPEED 3

#define START 0                 // Segment begin index
#define END 1                   // Segment end index

uint32_t color[STR_LEN];    	// 3 bytes each: green, red, blue
uint32_t destColor[STR_LEN];	// If dest color differs from color, transition from color to dest.
// Default segments
size_t segments[PREDEFINED_SEGMENT_COUNT][2] = {       //[x][y] x segments, y segment range: begin index, end index
    {0, STR_LEN-1},             // Entire display
    {0, 5},                     // 6 pixels long
    {6, 15},                    // 10 pixels long
    {16, STR_LEN-1}             // 26 pixels long
};

void drawToLEDs(void);
bool doFade(void);
int8_t convergeFactor(uint8_t a, uint8_t b);

/*
 * main.c
 */
void main(void) {
	struct pru_rpmsg_transport transport;
	uint16_t src, dst, len;
	volatile uint8_t *status;
	uint8_t r, g, b, d_r, d_g, d_b;
	int i, k=0;
    uint32_t colr;
	bool colorNeedsFade = false;

	// Set everything to background
	for(i=0; i<STR_LEN; i++) {
		color[i] = destColor[i] = 0x000000;
	}

	/* Allow OCP master port access by the PRU so the PRU can read external memories */
	CT_CFG.SYSCFG_bit.STANDBY_INIT = 0;

	/* Clear the status of the PRU-ICSS system event that the ARM will use to 'kick' us */
	CT_INTC.SICR_bit.STS_CLR_IDX = FROM_ARM_HOST;

	/* Make sure the Linux drivers are ready for RPMsg communication */
	status = &resourceTable.rpmsg_vdev.status;
	while (!(*status & VIRTIO_CONFIG_S_DRIVER_OK));

	/* Initialize the RPMsg transport structure */
	pru_rpmsg_init(&transport, &resourceTable.rpmsg_vring0, &resourceTable.rpmsg_vring1, TO_ARM_HOST, FROM_ARM_HOST);

	/* Create the RPMsg channel between the PRU and ARM user space using the transport structure. */
	while (pru_rpmsg_channel(RPMSG_NS_CREATE, &transport, CHAN_NAME, CHAN_DESC, CHAN_PORT) != PRU_RPMSG_SUCCESS);
	while (1) {
		/* Check bit 30 of register R31 to see if the ARM has kicked us */
		if (__R31 & HOST_INT) {
			/* Clear the event status */
			CT_INTC.SICR_bit.STS_CLR_IDX = FROM_ARM_HOST;
			/* Receive all available messages, multiple messages can be sent per kick */
			while (pru_rpmsg_receive(&transport, &src, &dst, payload, &len) == PRU_RPMSG_SUCCESS) {
			    char *ret;	// rest of payload after front character is removed
			    int index;	// index of LED to control

                // Input format is:  index red green blue
                index = atoi(payload);
                ret = strchr(payload, ' ');	// Skip over index
                r = strtol(&ret[1], NULL, 0);
                ret = strchr(&ret[1], ' ');	// Skip over r, etc.
                g = strtol(&ret[1], NULL, 0);
                ret = strchr(&ret[1], ' ');
                b = strtol(&ret[1], NULL, 0);
                colr = PACK_COLOR(r, g, b);	// String wants GRB

			    if((index >= 0) & (index < STR_LEN)) {                      // Codes to write to pixel buffer. Update the array, but don't write/draw it out.
                    color[index] = destColor[index] = colr;
			    }else if(index >= CODE_DESTINATION_BUFFER_WRITE_START_INDEX && index <= CODE_DESTINATION_BUFFER_WRITE_END_INDEX) {   // Codes to write to destination buffer only
                    destColor[index-CODE_DESTINATION_BUFFER_WRITE_START_INDEX] = colr;
                } else if (index >= CODE_DEFAULT_SEGMENT_START_INDEX && index <= CODE_DEFAULT_SEGMENT_END_INDEX) {  // Codes to write to default segments
                    for(i=segments[index - CODE_DEFAULT_SEGMENT_START_INDEX][START]; i<=segments[index - CODE_DEFAULT_SEGMENT_START_INDEX][END]; i++) {
                        destColor[i] = colr;
                    }
                }
                else {
                    switch(index) {
                    case CODE_DRAW:                // Index = CODE_DRAW; send the array to the LED string
                        //while(doFade()) {
                        //    drawToLEDs();
                        //}
            			do {
            			    colorNeedsFade = false;
                			for(k=0; k < STR_LEN; k++){
                			    if(color[k] == destColor[k]) continue;
                			    colorNeedsFade = true;
                			    b = BLUE(color[k]);
                			    r = RED(color[k]);
                			    g = GREEN(color[k]);

                			    d_b = BLUE(destColor[k]);
                			    d_r = RED(destColor[k]);
                			    d_g = GREEN(destColor[k]);

                                b += convergeFactor(b, d_b);
                                r += convergeFactor(r, d_r);
                                g += convergeFactor(g, d_g);

                                color[k] = PACK_COLOR(r, g, b);
                			}
                            drawToLEDs(); // Output the string
            			}while(colorNeedsFade);
                        break;
                    case CODE_CLEAR:                                        // Index = CODE_CLEAR; the display
                        for(k=0; k < STR_LEN; k++){
                            color[k] = destColor[k] = 0;
                        }
                        drawToLEDs();
                        break;
                    }
                }
			}
		}
	}
}

void drawToLEDs(void){
	// Select which pins to output to.  These are all on pru1_1
	uint32_t gpio = P9_29;
    int i, j;

    for(j=0; j<STR_LEN; j++) {
        // Cycle through each bit
        for(i=23; i>=0; i--) {
            if(color[j] & (0x1<<i)) {
                __R30 |= gpio;		// Set the GPIO pin to 1
                __delay_cycles(oneCyclesOn-1);
                __R30 &= ~gpio;		// Clear the GPIO pin
                __delay_cycles(oneCyclesOff-14);
            } else {
                __R30 |= gpio;		// Set the GPIO pin to 1
                __delay_cycles(zeroCyclesOn-1);
                __R30 &= ~gpio;		// Clear the GPIO pin
                __delay_cycles(zeroCyclesOff-14);
            }
        }
    }
    // Send Reset
    __R30 &= ~gpio;	// Clear the GPIO pin
    __delay_cycles(resetCycles);
}

/*
 * doFade
 * return: true (1) if the function should be called again to continue the fade. False if fade is complete.
 */
bool doFade(void) {
	uint8_t r, g, b, d_r, d_g, d_b;
    int i;
    bool colorNeedsFade = false;
    for(i=0; i < STR_LEN; i++){
        if(color[i] == destColor[i]) continue;
        colorNeedsFade = true;
        b = BLUE(color[i]);
        r = RED(color[i]);
        g = GREEN(color[i]);

        d_b = BLUE(destColor[i]);
        d_r = RED(destColor[i]);
        d_g = GREEN(destColor[i]);

        b += convergeFactor(b, d_b);
        r += convergeFactor(r, d_r);
        g += convergeFactor(g, d_g);

        color[i] = PACK_COLOR(r, g, b);
    }
    return colorNeedsFade;
}

int8_t convergeFactor(uint8_t a, uint8_t b) {
   int8_t dif = b - a;
   if(dif > FADE_SPEED) return FADE_SPEED;
   if(dif < -FADE_SPEED) return -FADE_SPEED;
   return dif;
}

// Sets pinmux
#pragma DATA_SECTION(init_pins, ".init_pins")
#pragma RETAIN(init_pins)
const char init_pins[] =
	"/sys/devices/platform/ocp/ocp:P9_29_pinmux/state\0pruout\0" \
	"\0\0";
