#include "usb7204_driver.h"

// EVERYTHING ABOVE IS FROM test-usb7204.c

int flag;
unsigned char serial[9];
uint8_t channel, gain;
int temp, i,j;
int ch;
LoadQueue  gainArray;
uint16_t in_data[1024];
int count;
uint8_t options;
float freq;
uint16_t wvalue;
uint16_t out_data[512];

libusb_device_handle *udev = NULL;
int ret;
Calibration_AIN table_AIN[NMODE][NGAINS_USB7204][NCHAN_USB7204];
struct tm date;

// udev = 0;
// gain = BP_5_00V; //ONLY SUPPORTING 5V RANGE READING

void setup_usb7204(){

  udev = 0;
  gain = BP_5_00V; 
  
  ret = libusb_init(NULL);
  if (ret < 0) {
    perror("libusb_init: Failed to initialize libusb");
    exit(1);
  }

  if ((udev = usb_device_find_USB_MCC(USB7204_PID, NULL))) {
    printf("USB-7204 Device is found!\n");
  } else {
    printf("No device found.\n");
    exit(0);
  }

  // some initialization
  printf("Building calibration table.  This may take a while ...\n");
  usbBuildGainTable_USB7204(udev, table_AIN);
  for (i = 0; i < NGAINS_USB7204; i++ ) {
    for (j = 0; j < NCHAN_USB7204/2; j++) {
      printf("Calibration Table: Range = %d Channel = %d Slope = %f   Offset = %f\n", 
	     i, j, table_AIN[DF][i][j].slope, table_AIN[DF][i][j].intercept);
    }
  }
  i = BP_10_00V;
  for (j = 0; j < NCHAN_USB7204; j++) {
    printf("Calibration Table: Range = %d Channel = %d Slope = %f   Offset = %f\n", 
	   i, j, table_AIN[SE][i][j].slope, table_AIN[SE][i][j].intercept);
  }

  //print out the wMaxPacketSize.  Should be 64.
  printf("\nwMaxPacketSize = %d\n", usb_get_max_packet_size(udev,0));

  // Print the calibration date
  getMFGCAL_USB7204(udev, &date);
  printf("\nLast Calibration date: %s", asctime(&date));
}

/**
 * @brief readChannel : reads specified channel
 * @param channel : channel to be read
 * @return
 */
double readChannel(int channel){
    int flag = fcntl(fileno(stdin), F_GETFL);
    fcntl(0, F_SETFL, flag | O_NONBLOCK);
    wvalue = usbAIn_USB7204(udev, DF, channel, gain);
    wvalue = rint(wvalue*table_AIN[DF][gain][channel].slope + table_AIN[DF][gain][channel].intercept);
    double readVal = volts_USB7204(wvalue, gain);
    fcntl(fileno(stdin), F_SETFL, flag);
    return readVal;
}

/**
 * @brief writeToChannel : writes data to specified channel
 * @param channel : channel to write data to
 * @param voltage : value to write to channel
 */
void writeToChannel(uint8_t channel, float voltage){
    usbAOut_USB7204(udev, channel, voltage);
}

