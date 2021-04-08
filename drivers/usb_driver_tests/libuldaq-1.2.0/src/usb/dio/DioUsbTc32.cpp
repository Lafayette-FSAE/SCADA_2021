/*
 * DioUsbTc32.cpp
 *
 *     Author: Measurement Computing Corporation
 */

#include "DioUsbTc32.h"

namespace ul
{

DioUsbTc32::DioUsbTc32(const UsbDaqDevice& daqDevice) : DioUsbBase(daqDevice)
{
	mDioInfo.addPort(0, FIRSTPORTA, 8, DPIOT_IN);
	mDioInfo.addPort(0, FIRSTPORTB, 32, DPIOT_NONCONFIG);

	mDioInfo.addPort(0, SECONDPORTA, 8, DPIOT_IN);
	mDioInfo.addPort(0, SECONDPORTB, 32, DPIOT_NONCONFIG);
}

DioUsbTc32::~DioUsbTc32()
{

}

void DioUsbTc32::initialize()
{
	try
	{
		initPortsDirectionMask();
		readAlarmMask();
	}
	catch(UlException& e)
	{
		UL_LOG("Ul exception occurred: " << e.what());
	}
}

unsigned long long DioUsbTc32::dIn(DigitalPortType portType)
{
	DigitalPortType portTypeCheck = portType;

	if(!daqDev().hasExp() && (portType == SECONDPORTA || portType == SECONDPORTB))
		throw UlException(ERR_BAD_PORT_TYPE);

	check_DIn_Args(portTypeCheck);

	unsigned int portVal = 0;

	if(portType == FIRSTPORTA || portType == SECONDPORTA)
	{
		unsigned char portValues[2] = {0, 0};

		daqDev().queryCmd(CMD_DIN, 0, 0, portValues, sizeof(portValues));

		unsigned short portNum = portType == SECONDPORTA ? 1 : 0;

		portVal = portValues[portNum];
	}
	else
	{
		unsigned int portValues[2] = {0, 0};

		daqDev().queryCmd(CMD_DOUT, 0, 0, (unsigned char*) portValues, sizeof(portValues));

		unsigned short portNum = portType == SECONDPORTB ? 1 : 0;

		portVal = portValues[portNum];
	}

	return portVal;
}

void DioUsbTc32::dOut(DigitalPortType portType, unsigned long long data)
{
	DigitalPortType portTypeCheck = portType;

	if(!daqDev().hasExp() && (portType == SECONDPORTB))
		throw UlException(ERR_BAD_PORT_TYPE);

	check_DOut_Args(portTypeCheck, data);

	int alarmIdx = portType == SECONDPORTB ? 1 : 0;

	if(mAlarmMask[alarmIdx].any())
		throw UlException(ERR_PORT_USED_FOR_ALARM);

#pragma pack(1)
		struct
		{
			unsigned char index;
			unsigned int value;
		}output;
#pragma pack()

	output.index = portType == SECONDPORTB ? 2 : 1;
	output.value = data;


	daqDev().sendCmd(CMD_DOUT, 0, 0, (unsigned char*) &output, sizeof(output));
}

bool DioUsbTc32::dBitIn(DigitalPortType portType, int bitNum)
{
	DigitalPortType portTypeCheck = portType;

	if(!daqDev().hasExp() && (portType == SECONDPORTA || portType == SECONDPORTB))
		throw UlException(ERR_BAD_PORT_TYPE);

	check_DBitIn_Args(portTypeCheck, bitNum);

	unsigned int portValue = dIn(portType);

	std::bitset<32> bitset(portValue);

	return bitset[bitNum];
}

void DioUsbTc32::dBitOut(DigitalPortType portType, int bitNum, bool bitValue)
{
	DigitalPortType portTypeCheck = portType;

	if(!daqDev().hasExp() && (portType == SECONDPORTB))
		throw UlException(ERR_BAD_PORT_TYPE);

	check_DBitOut_Args(portTypeCheck, bitNum);

	int alarmIdx = portType == SECONDPORTB ? 1 : 0;

	if(mAlarmMask[alarmIdx][bitNum])
		throw UlException(ERR_BIT_USED_FOR_ALARM);

	unsigned int portValues[2] = {0, 0};

	daqDev().queryCmd(CMD_DOUT, 0, 0, (unsigned char*) portValues, sizeof(portValues));

	unsigned short portNum = portType == SECONDPORTB ? 1 : 0;

	unsigned int portValue = portValues[portNum];

	std::bitset<32> bitset(portValue);

	if(bitValue)
		bitset.set(bitNum);
	else
		bitset.reset(bitNum);

	portValue = bitset.to_ulong();

#pragma pack(1)
		struct
		{
			unsigned char index;
			unsigned int value;
		}output;
#pragma pack()

	output.index = portType == SECONDPORTB ? 2 : 1;
	output.value = portValue;

	daqDev().sendCmd(CMD_DOUT, 0, 0, (unsigned char*) &output, sizeof(output));
}

unsigned long long DioUsbTc32::getCfg_PortDirectionMask(unsigned int portNum) const
{
	if(portNum == 0 || portNum == 2)
		return 0;

	throw UlException(ERR_CONFIG_NOT_SUPPORTED);
}

void DioUsbTc32::dClearAlarm(DigitalPortType portType, unsigned long long mask)
{
	if(!daqDev().hasExp() && (portType == SECONDPORTB))
		throw UlException(ERR_BAD_PORT_TYPE);

	check_DOut_Args(portType, mask);

#pragma pack(1)
		struct
		{
			unsigned char index;
			unsigned int value;
		}output;
#pragma pack()

	output.index = portType == SECONDPORTB ? 2 : 1;
	output.value = mask;


	daqDev().sendCmd(CMD_ALARM_STATUS, 0, 0, (unsigned char*) &output, sizeof(output));
}

void DioUsbTc32::readAlarmMask()
{
#pragma pack(1)
	struct
	{
		unsigned char settings[32];
		float threshold1[32];
		float threashold2[32];
	}alarm[2];
#pragma pack()

	daqDev().queryCmd(CMD_ALARM_CONFIG, 0, 0, (unsigned char*) &alarm, sizeof(alarm));

	mAlarmMask[0].reset();
	mAlarmMask[1].reset();

	for(int i = 0; i < 32; i++)
	{
		mAlarmMask[0] |=  (alarm[0].settings[i] & 0x01) << i;
		mAlarmMask[1] |=  (alarm[1].settings[i] & 0x01) << i;
	}
}



} /* namespace ul */

