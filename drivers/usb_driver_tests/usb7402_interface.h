#ifndef USB7402_INTERFACE_H
#define USB7402_INTERFACE_H

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <ctype.h>
#include <stdint.h>
#include <math.h>
#include <vector>

#include "libusb_interface/pmd.h"
#include "libusb_interface/usb-7204.h"
#include <QObject>
#include <QCoreApplication>
#include <QTimer>
#include "typedefs.h"
#include "group.h"

using namespace std;

class usb7402_interface : public QObject
{
    Q_OBJECT
public:
    usb7402_interface(vector<meta *> sensors);
    ~usb7402_interface();

    //member functions
    void stopUSBCheck();
    void startUSBCheck();
    int writeChannel(int channel);
    void setSamplingRate(int newRate);
    double readChannel(uint8_t channel);

    //objects and instance vectors
    QTimer * timer;
    vector<meta *> sensorVector;

    //global variables
    bool isActive = 0;
    float voltage;
    uint8_t gain;
    uint16_t wvalue;
    int samplingRate = 1000;
    libusb_device_handle *udev;
    Calibration_AIN table_AIN[NMODE][NGAINS_USB7204][NCHAN_USB7204];

    string initErr = "ERROR: USB-7204 boot failed";
    string initSuccess = "USB-7204 boot successful";

public slots:
   void usbCheckTasks();
   void writeUSBData(uint8_t channel, float voltage, bool * success);
   void rebootUSB7204();

signals:
   void sensorValueChanged(meta * sensor);
   void pushMessage(string msg);
   void finished();
};

#endif // USB7402_INTERFACE_H
