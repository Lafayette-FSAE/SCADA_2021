#ifndef USB7204_DRIVER_H
#define USB7204_DRIVER_H

#ifdef __cplusplus
extern "C" { 
#endif

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <ctype.h>
#include <stdint.h>
#include <math.h>

#include "pmd.h"
#include "usb-7204.h"


void setup_usb7204();
double readChannel(int channel);
void writeToChannel(uint8_t channel, float voltage);

#ifdef __cplusplus
} /* closing brace for extern "C" */
#endif
#endif // USB7204_DRIVER_H