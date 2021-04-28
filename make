#!/bin/bash


# # make sure can bus is set up for testing
modprobe can
# ip link set can0 down
# ip link set can0 up type can bitrate 125000

# # make sure virtual can bus is set up for testing
# modprobe vcan
# ip link add dev vcan0 type vcan
# ip link set up vcan0

# make binary files executable, these are the looping files run by our services
chmod +x install
chmod +x make
chmod +x scada
chmod +x sorter/sorter.py
chmod +x calibrator/calibrator.py
chmod +x logger/logger.py
chmod +x watcher/watcher.py
chmod +x GUI/MainGUI.py


# copy binary files to /usr/bin
cp scada /usr/bin/scada

#Copying down i2c sorter 
# cp drivers/i2c_sorter.py /usr/bin/i2c_sorter.py
# #copying down can sorter
# cp drivers/can_driver.py /usr/bin/can_driver.py

cp sorter/sorter.py /usr/bin/scada_sorter.py
cp calibrator/calibrator.py /usr/bin/scada_calibrator.py
cp logger/logger.py /usr/bin/scada_logger.py
cp watcher/watcher.py /usr/bin/scada_watcher.py
cp GUI/MainGUI.py /usr/bin/scada_gui.py
cp GUI/dash2.py /usr/bin/scada_dash.py
cp rtc_setup.py /usr/bin/scadartc_setup.py

# create a workspace and copy important files into it
mkdir -p /usr/etc/scada
rm -rf /usr/etc/scada/utils
cp -r utils /usr/etc/scada/utils
rm -rf /usr/etc/scada/config
cp -r config /usr/etc/scada/config
cp ./install /usr/etc/scada
cp ./make /usr/etc/scada
rm -rf /usr/etc/scada/GUI
cp -r GUI /usr/etc/scada/GUI
rm -rf /usr/etc/scada/drivers
cp -r drivers /usr/etc/scada/drivers

# copy service files for systemd
cp sorter/sorter.service /etc/systemd/system
cp calibrator/calibrator.service /etc/systemd/system
cp logger/logger.service /etc/systemd/system
cp watcher/watcher.service /etc/systemd/system
cp GUI/gui.service /etc/systemd/system

systemctl daemon-reload

## Enabling Services to Allow for Automatic Startup on Booot
systemctl enable sorter
systemctl enable calibrator
systemctl enable logger
systemctl enable watcher

echo 'MAKE COMPLETE'

# /usr/bin/scada_gui.py
