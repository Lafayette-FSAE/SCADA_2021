#include "usb7402_interface.h"

/**
 * @brief usb7402_interface::usb7402_interface : class constructor
 * @param sensors : configures USB7204 configured sensors
 */
usb7402_interface::usb7402_interface(vector<meta *> sensors)
{
    sensorVector = sensors;
    udev = nullptr;

    int ret = libusb_init(nullptr);
    if (ret < 0) {
      perror("libusb_init: Failed to initialize libusb");
      pushMessage(initErr);
      return;
    }

    if ((udev = usb_device_find_USB_MCC(USB7204_PID, nullptr))) {
      printf("USB-7204 Device is found!\n");
      isActive = true;
    } else {
      printf("No device found.\n");
      pushMessage(initErr);
      return;
    }

    if (isActive){
        try{
        // some initialization
        printf("Building calibration table.  This may take a while ...\n");
        usbBuildGainTable_USB7204(udev, table_AIN);
        int i = 0;
        int j = 0;
        for (i = 0; i < NGAINS_USB7204; i++ ) {
          for (j = 0; j < NCHAN_USB7204/2; j++) {
            printf("Calibration Table: Range = %d Channel = %d Slope = %f   Offset = %f\n",
               i, j, static_cast<double>(table_AIN[DF][i][j].slope), static_cast<double>(table_AIN[DF][i][j].intercept));
          }
        }
        i = BP_10_00V;
        for (j = 0; j < NCHAN_USB7204; j++) {
          printf("Calibration Table: Range = %d Channel = %d Slope = %f   Offset = %f\n",
             i, j, static_cast<double>(table_AIN[SE][i][j].slope), static_cast<double>(table_AIN[SE][i][j].intercept));
        }

        //print out the wMaxPacketSize.  Should be 64.
        printf("\nwMaxPacketSize = %d\n", usb_get_max_packet_size(udev,0));

        struct tm date;

        // Print the calibration date
        getMFGCAL_USB7204(udev, &date);
        printf("\nLast Calibration date: %s", asctime(&date));
        } catch (...){
            cout << "USB_7204 interface not configured" << endl;
            pushMessage(initErr);
            isActive = false;
        }

        gain = BP_5_00V;
        voltage = static_cast<float>(4.9);
    }

    timer = new QTimer;
    connect(timer, SIGNAL(timeout()), this, SLOT(usbCheckTasks()));

    if (isActive){
        pushMessage(initSuccess);
    } else {
        pushMessage(initErr);
    }
}

/**
 * @brief usb7402_interface::~usb7402_interface : class destructor
 */
usb7402_interface::~usb7402_interface()
{

}

/**
 * @brief usb7402_interface::writeUSBData : writes data to specified channel
 * @param channel : channel to write data to
 * @param voltage : value to write to channel
 */
void usb7402_interface::writeUSBData(uint8_t channel, float voltage, bool *success){
    if (isActive){
        usbAOut_USB7204(udev, channel, voltage);
        *success = true;
    } else {
        *success = false;
        pushMessage(initErr);
    }
}

/**
 * @brief usb7402_interface::setSamplingRate : sets the sampling rate of reading USB sensors
 * @param newRate : rate to be set
 * @return
 */
void usb7402_interface::setSamplingRate(int newRate){
    samplingRate = newRate;
    stopUSBCheck();
    startUSBCheck();
}

/**
 * @brief usb7402_interface::startUSBCheck : start sampling data
 * @return
 */
void usb7402_interface::startUSBCheck(){
    cout << "Starting USB Checking" << endl;
    timer->start(samplingRate);
}

/**
 * @brief usb7402_interface::stopUSBCheck : stop sampling data
 */
void usb7402_interface::stopUSBCheck(){
    timer->stop();
}

/**
 * @brief usb7402_interface::readChannel : reads specified channel
 * @param channel : channel to be read
 * @return
 */
double usb7402_interface::readChannel(uint8_t channel){
    int flag = fcntl(fileno(stdin), F_GETFL);
    fcntl(0, F_SETFL, flag | O_NONBLOCK);
    wvalue = usbAIn_USB7204(udev, DF, channel, gain);
    wvalue = static_cast<unsigned short>(rint(wvalue*table_AIN[DF][gain][channel].slope + table_AIN[DF][gain][channel].intercept));
    double readVal = volts_USB7204(wvalue, gain);
    fcntl(fileno(stdin), F_SETFL, flag);
    return readVal;
}

/**
 * @brief usb7402_interface::usbCheckTasks : tasks to check whether sensor values have changed
 */
void usb7402_interface::usbCheckTasks(){
    for (uint i = 0; i < sensorVector.size(); i++){
        QCoreApplication::processEvents();
        double val = readChannel(static_cast<uint8_t>(sensorVector.at(i)->usbChannel));
        sensorVector.at(i)->val = val;
        emit sensorValueChanged(sensorVector.at(i));
    }
}

void usb7402_interface::rebootUSB7204(){
    if (isActive){
        stopUSBCheck();
    }

    libusb_close(udev);
    udev = nullptr;

    int ret = libusb_init(nullptr);
    if (ret < 0) {
      perror("libusb_init: Failed to initialize libusb");
      exit(1);
    }

    if ((udev = usb_device_find_USB_MCC(USB7204_PID, nullptr))) {
        printf("USB-7204 Device is found!\n");
        isActive = true;
    } else {
        isActive = false;
        printf("No device found.\n");
        pushMessage(initErr);
      return;
    }

    if (isActive){
        try{
        // some initialization
        printf("Building calibration table.  This may take a while ...\n");
        usbBuildGainTable_USB7204(udev, table_AIN);
        int i = 0;
        int j = 0;
        for (i = 0; i < NGAINS_USB7204; i++ ) {
          for (j = 0; j < NCHAN_USB7204/2; j++) {
            printf("Calibration Table: Range = %d Channel = %d Slope = %f   Offset = %f\n",
               i, j, static_cast<double>(table_AIN[DF][i][j].slope), static_cast<double>(table_AIN[DF][i][j].intercept));
          }
        }
        i = BP_10_00V;
        for (j = 0; j < NCHAN_USB7204; j++) {
          printf("Calibration Table: Range = %d Channel = %d Slope = %f   Offset = %f\n",
             i, j, static_cast<double>(table_AIN[SE][i][j].slope), static_cast<double>(table_AIN[SE][i][j].intercept));
        }

        //print out the wMaxPacketSize.  Should be 64.
        printf("\nwMaxPacketSize = %d\n", usb_get_max_packet_size(udev,0));

        struct tm date;

        // Print the calibration date
        getMFGCAL_USB7204(udev, &date);
        printf("\nLast Calibration date: %s", asctime(&date));
        } catch (...){
            cout << "USB_7204 interface not configured" << endl;
            pushMessage(initErr);
            isActive = false;
        }

        gain = BP_5_00V;
        voltage = static_cast<float>(4.9);
    }

    if (isActive){
        startUSBCheck();
        pushMessage(initSuccess);
    }
}
