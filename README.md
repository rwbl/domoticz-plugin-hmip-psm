# Domoticz Plugin homematicIP Pluggable Switch and Meter (HMIP-PSM)
Domoticz plugin for the homematicIP Pluggable Switch and Meter (HMIP-PSM).

# Objectives
* To switch the device on and off.
* To measure, in regular intervals, the power (W), energy (Wh), voltage (V), current (mA).

## Solution
The HMIP-PSM is connected to a homematic IP system.
The homematic IP system used is a [RaspberryMatic](https://raspberrymatic.de/) operating system running the Homematic Central-Control-Unit (CCU).
The CCU has the additional software XML-API CCU Addon installed.
Communication between Domoticz and the CCU is via HTTP XML-API requests with HTTP XML response.

In Domoticz, following device(s) is/are created:
(Type,SubType) [XML-API Device Datapoint Type] - Note)
* Energy (kWh) [ENERGY_COUNTER] [POWER] - Power is not used for a device, just logged only
* Voltage (Voltage) [VOLTAGE]
* Current (Current) [CURRENT]
* Switch (Switch) [STATE]

The device state is updated every 60 seconds (default).

If required, further actions can defined, by for example creating a dzVents script to send a notification / email (see below "dzVents Example").

## Hardware
Hardware subject to change.
* Raspberry Pi 3B+ (RaspberryMatic System)
* homematicIP Pluggable Switch and Meter (HMIP-PSM)

## Software
Software versions subject to change.
* Raspberry Pi OS ( Raspbian GNU/Linux 10 buster, kernel 5.4.83-v7l+)
* Domoticz 2020.2 (build 12847)
* RaspberryMatic 3.55.5.20201226 [info](https://raspberrymatic.de/)
* XML-API CCU Addon 1.20 [info](https://github.com/jens-maus/XML-API)
* Python 3.7.3
* Python module ElementTree

**Note on the Python Module ElementTree**
The Python Module **ElementTree XML API** is used to parse the XML-API response.
This module is part of the standard package and provides limited support for XPath expressions for locating elements in a tree. 

_Hint_
(Optional)
For full XPath support install the module **ElementPath** from the terminal command-line for Python 2.x and 3.x via pip:
``` 
sudo pip install elementpath
sudo pip3 install elementpath
```

## RaspberryMatic Prepare
The RaspberryMatic system has been setup according [these](https://github.com/jens-maus/RaspberryMatic) guidelines.

The XML-API CCU Addon is required and installed via the HomeMatic WebUI > Settings > Control panel > Additional software (download the latest version from previous URL shared).
**IMPORTANT**
Be aware of the security risk, in case the HomeMatic Control Center can be reached via the Internet without special protection (see XML-API Guidelines).

### XML-API Scripts
The XML-API provides various tool scripts, i.e. devices state list, device state or set new value and many more.
The scripts are submitted via HTTP XML-API requests.
The plugin makes selective use of scripts with device id and datapoint id's.
The device id is required to get the state of the device datapoints. The datapoint id's are required to get the state/value of device attributes.

#### Device ID (statelist.cgi)
Get Device ID (attribute "ise_id") from list of all devices with channels and current values: http://ccu-ip-address/addons/xmlapi/statelist.cgi.

From the HTTP XML-API response, the Device ID ("ise_id") is selected by searching for the
* Device Name (i.e. Schalt-Mess-Steckdose MakeLab) or 
* Device Channel (HMIP-PSM 0001D3C99C6AB3:3 Switch actuator). 
The data is obtained from the HomeMatic WebUI Home page > Status and control > Devices.
The Device "ise_id" is required for the plugin parameter _Mode1_.
HTTP XML-API response: Device ID = 1418.
```
...
<device name="Schalt-Mess-Steckdose MakeLab" ise_id="1418" unreach="false" config_pending="false">
	<channel...>
</device>
...
```
This script 
* has to be run once from a browser prior installing the plugin to get the device id as required by the plugin parameter Device ID ("mode1") and the next script.
* is not used in the plugin.

#### Channel Datapoint(s) (state.cgi)
Request the Channel Datapoint(s) for a Device ID to get value(s) for selected attribute(s): http://ccu-ip-address/addons/xmlapi/state.cgi?device_id=DEVICE_ISE_ID
The **Device ID 1418** is used as parameter to get the device state from which the attributes can be selected. 
The HTTP XML-API response lists eight Channels from which channels **HmIP-SWDM 001558A99D5A78:3** and **HMIP-PSM 0001D3C99C6AB3:6** are used.
The datapoint(s) used:
* Channel 3: type="STATE" with ise_id="1451" to set/get the state of the switch. The value is from valuetype 2, i.e. true (ON) or false (OFF).
* Channel 6: type=ENERGY_COUNTER, POWER, VOLTAGE, CURRENT.
The datapoint "ise_id" is required for the plugin parameter _Mode2_.
```
<device name="Schalt-Mess-Steckdose MakeLab" ise_id="1418" unreach="false" config_pending="false">
<channel name="Schalt-Mess-Steckdose MakeLab:0" ise_id="1419" index="0" visible="true" operate="false">
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.CONFIG_PENDING" type="CONFIG_PENDING" ise_id="1420" value="false" valuetype="2" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.DUTY_CYCLE" type="DUTY_CYCLE" ise_id="1424" value="false" valuetype="2" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.OPERATING_VOLTAGE" type="OPERATING_VOLTAGE" ise_id="1426" value="0.000000" valuetype="4" valueunit="V" timestamp="0" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.OPERATING_VOLTAGE_STATUS" type="OPERATING_VOLTAGE_STATUS" ise_id="1427" value="0" valuetype="16" valueunit="" timestamp="0" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.RSSI_DEVICE" type="RSSI_DEVICE" ise_id="1428" value="190" valuetype="8" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.RSSI_PEER" type="RSSI_PEER" ise_id="1429" value="178" valuetype="8" valueunit="" timestamp="1611503042" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.UNREACH" type="UNREACH" ise_id="1430" value="false" valuetype="2" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.UPDATE_PENDING" type="UPDATE_PENDING" ise_id="1434" value="false" valuetype="2" valueunit="" timestamp="1610968122" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.ACTUAL_TEMPERATURE" type="ACTUAL_TEMPERATURE" ise_id="3065" value="26.000000" valuetype="4" valueunit="°C" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.ACTUAL_TEMPERATURE_STATUS" type="ACTUAL_TEMPERATURE_STATUS" ise_id="3066" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.ERROR_CODE" type="ERROR_CODE" ise_id="3067" value="0" valuetype="8" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:0.ERROR_OVERHEAT" type="ERROR_OVERHEAT" ise_id="3068" value="false" valuetype="2" valueunit="" timestamp="1611569595" operations="5"/>
</channel>
	<channel name="HMIP-PSM 0001D3C99C6AB3:1" ise_id="1438" index="1" visible="true" operate="false">
	<datapoint name="HmIP-RF.0001D3C99C6AB3:1.PRESS_LONG" type="PRESS_LONG" ise_id="1439" value="" valuetype="2" valueunit="" timestamp="0" operations="4"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:1.PRESS_SHORT" type="PRESS_SHORT" ise_id="1440" value="" valuetype="2" valueunit="" timestamp="0" operations="4"/>
</channel>
<channel name="HMIP-PSM 0001D3C99C6AB3:2" ise_id="1441" index="2" visible="true" operate="false">
	<datapoint name="HmIP-RF.0001D3C99C6AB3:2.PROCESS" type="PROCESS" ise_id="1442" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:2.SECTION" type="SECTION" ise_id="1443" value="2" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:2.SECTION_STATUS" type="SECTION_STATUS" ise_id="1444" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
<datapoint name="HmIP-RF.0001D3C99C6AB3:2.STATE" type="STATE" ise_id="1445" value="true" valuetype="2" valueunit="" timestamp="1611569595" operations="5"/>
</channel>
	<channel name="HMIP-PSM 0001D3C99C6AB3:3" ise_id="1446" index="3" visible="true" operate="true">
	<datapoint name="HmIP-RF.0001D3C99C6AB3:3.PROCESS" type="PROCESS" ise_id="1448" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:3.SECTION" type="SECTION" ise_id="1449" value="2" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:3.SECTION_STATUS" type="SECTION_STATUS" ise_id="1450" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:3.STATE" type="STATE" ise_id="1451" value="true" valuetype="2" valueunit="" timestamp="1611569595" operations="7"/>
<datapoint name="HmIP-RF.0001D3C99C6AB3:3.COMBINED_PARAMETER" type="COMBINED_PARAMETER" ise_id="9533" value="" valuetype="20" valueunit="" timestamp="0" operations="2"/>
</channel>
<channel name="HMIP-PSM 0001D3C99C6AB3:4" ise_id="1452" index="4" visible="true" operate="true">
	<datapoint name="HmIP-RF.0001D3C99C6AB3:4.PROCESS" type="PROCESS" ise_id="1454" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:4.SECTION" type="SECTION" ise_id="1455" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:4.SECTION_STATUS" type="SECTION_STATUS" ise_id="1456" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:4.STATE" type="STATE" ise_id="1457" value="false" valuetype="2" valueunit="" timestamp="1611569595" operations="7"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:4.COMBINED_PARAMETER" type="COMBINED_PARAMETER" ise_id="9534" value="" valuetype="20" valueunit="" timestamp="0" operations="2"/>
</channel>
	<channel name="HMIP-PSM 0001D3C99C6AB3:5" ise_id="1458" index="5" visible="true" operate="true">
	<datapoint name="HmIP-RF.0001D3C99C6AB3:5.PROCESS" type="PROCESS" ise_id="1460" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:5.SECTION" type="SECTION" ise_id="1461" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:5.SECTION_STATUS" type="SECTION_STATUS" ise_id="1462" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:5.STATE" type="STATE" ise_id="1463" value="false" valuetype="2" valueunit="" timestamp="1611569595" operations="7"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:5.COMBINED_PARAMETER" type="COMBINED_PARAMETER" ise_id="9535" value="" valuetype="20" valueunit="" timestamp="0" operations="2"/>
</channel>
<channel name="HMIP-PSM 0001D3C99C6AB3:6" ise_id="1464" index="6" visible="true" operate="false">
	<datapoint name="HmIP-RF.0001D3C99C6AB3:6.CURRENT" type="CURRENT" ise_id="1465" value="290.000000" valuetype="4" valueunit="mA" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:6.CURRENT_STATUS" type="CURRENT_STATUS" ise_id="1466" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:6.ENERGY_COUNTER" type="ENERGY_COUNTER" ise_id="1467" value="17602.100000" valuetype="4" valueunit="Wh" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:6.ENERGY_COUNTER_OVERFLOW" type="ENERGY_COUNTER_OVERFLOW" ise_id="1468" value="false" valuetype="2" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:6.FREQUENCY" type="FREQUENCY" ise_id="1469" value="49.970000" valuetype="4" valueunit="Hz" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:6.FREQUENCY_STATUS" type="FREQUENCY_STATUS" ise_id="1470" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:6.POWER" type="POWER" ise_id="1471" value="50.800000" valuetype="4" valueunit="W" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:6.POWER_STATUS" type="POWER_STATUS" ise_id="1472" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:6.VOLTAGE" type="VOLTAGE" ise_id="1473" value="226.000000" valuetype="4" valueunit="V" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:6.VOLTAGE_STATUS" type="VOLTAGE_STATUS" ise_id="1474" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
</channel>
<channel name="HMIP-PSM 0001D3C99C6AB3:7" ise_id="1475" index="7" visible="true" operate="false"/>
<channel name="HMIP-PSM 0001D3C99C6AB3:8" ise_id="3069" index="8" visible="true" operate="true">
	<datapoint name="HmIP-RF.0001D3C99C6AB3:8.WEEK_PROGRAM_CHANNEL_LOCKS" type="WEEK_PROGRAM_CHANNEL_LOCKS" ise_id="3070" value="0" valuetype="16" valueunit="" timestamp="1611569595" operations="5"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:8.WEEK_PROGRAM_TARGET_CHANNEL_LOCK" type="WEEK_PROGRAM_TARGET_CHANNEL_LOCK" ise_id="3071" value="" valuetype="16" valueunit="" timestamp="0" operations="2"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:8.WEEK_PROGRAM_TARGET_CHANNEL_LOCKS" type="WEEK_PROGRAM_TARGET_CHANNEL_LOCKS" ise_id="3072" value="" valuetype="16" valueunit="" timestamp="0" operations="2"/>
	<datapoint name="HmIP-RF.0001D3C99C6AB3:8.COMBINED_PARAMETER" type="COMBINED_PARAMETER" ise_id="9536" value="" valuetype="20" valueunit="" timestamp="0" operations="2"/>
</channel>
</device>
```
This script 
* has to be run once from a browser prior installing the plugin to get the datapoint id as required by the plugin hardware Datapoint ID STATE ("mode2").
* is used in the plugin to get the device state in regular check intervals.
#### Change Value (statechange.cgi)
Change the State or Value for a Datapoint: http://ccu-ip-address/addons/xmlapi/statechange.cgi?ise_id=DATAPOINT_ISE_ID&new_value=NEW_VALUE

This script is used by the plugin to turn the switch with ise_id=1451 to state ON (new_value="true") or OFF (new_value="false")

#### Summary
The device id "1418" (for the device named "Schalt-Mess-Steckdose MakeLab") is used to 
* set/get the state "true" (ON) or "false" (OFF) of the channel "HmIP-RF.0001D3C99C6AB3:3" datapoint type "STATE", ise_id "1451". 
* get the values from the channel "HmIP-RF.0001D3C99C6AB3:6" for the types ENERGY_COUNTER, POWER, VOLTAGE, CURRENT.

## Domoticz Prepare
Open in a browser, four tabs with the Domoticz GUI Tabs: 
* Setup > Hardware = to add / delete the new hardware
* Setup > Devices = to check the devices created by the new hardware (use button Refresh to get the latest values)
* Setup > Log = to check the installation and check interval cycles for errors
* Active Menu depending Domoticz Devices created/used = to check the devices value
Ensure to have the latest Domoticz version installed: Domoticz GUI Tab Setup > Check for Update

### Domoticz Plugin Installation

### Plugin Folder and File
Each plugin requires a dedicated folder which contains the plugin, mandatory named **plugin.py**.
The folder is named according omematic IP device name. 
``` 
mkdir /home/pi/domoticz/plugins/hmip-psm
``` 

Copy the file **plugin.py** to the folder.

### Restart Domoticz
``` 
sudo service domoticz.sh restart
``` 

### Domoticz Add Hardware
**IMPORTANT**
Prior adding the hardware, set in Domoticz GUI > Settings the option to allow new hardware.
If this option is not enabled, no new devices are created.
Check the GUI > Setup > Log as error message Python script at the line where the new device is used
(i.e. Domoticz.Debug("Device created: "+Devices[1].Name))

In the GUI > Setup > Hardware add the new hardware **homematicIP Pluggable Switch and Meter (HmIP-PSM)**.
Define the hardware parameter:
* CCU IP: The IP address of the homematic CCU. Default: 192.168.1.225.
* Device ID: The device datapoint ise_id - taken from the XMLAPI statelist request. Default: 1418.
* Datapoint STATE: The STATE datapoint ise_id - taken from the XMLAPI statelist request. Default: 1451.
* Check Interval (sec): How often the state of the device is checked. Default: 60.
* Debug: Set initially to true. If the plugin runs fine, update to false.

### Add Hardware - Check the Domoticz Log
After adding, ensure to check the Domoticz Log (GUI > Setup > Log)
Example
```
2019-07-02 10:24:05.761 Status: (MakeLab Energy) Started. 
2019-07-02 10:24:06.426 (MakeLab Energy) Debug logging mask set to: PYTHON PLUGIN QUEUE IMAGE DEVICE CONNECTION MESSAGE ALL 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Mode3':'1467,1471,1473,1465' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Mode2':'1451' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'HomeFolder':'/home/pi/domoticz/plugins/hmip-psm/' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Database':'/home/pi/domoticz/domoticz.db' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Key':'HMIP-PSM' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Mode5':'60' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Version':'1.0 (Build 20190702)' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Language':'en' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'UserDataFolder':'/home/pi/domoticz/' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'DomoticzHash':'75effa672' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'HardwareID':'9' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Port':'0' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Author':'rwbL' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'DomoticzBuildTime':'2019-06-27 14:56:10' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'DomoticzVersion':'4.10935' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Mode6':'Debug' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'StartupFolder':'/home/pi/domoticz/' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Mode1':'1418' 
2019-07-02 10:24:06.426 (MakeLab Energy) 'Address':'ccu-ip-address' 
2019-07-02 10:24:06.427 (MakeLab Energy) 'Name':'MakeLab Energy' 
2019-07-02 10:24:06.427 (MakeLab Energy) Device count: 0 
2019-07-02 10:24:06.427 (MakeLab Energy) Creating new devices ... 
2019-07-02 10:24:06.427 (MakeLab Energy) Creating device 'Energy'. 
2019-07-02 10:24:06.428 (MakeLab Energy) Device created: MakeLab Energy - Energy 
2019-07-02 10:24:06.428 (MakeLab Energy) Creating device 'Voltage'. 
2019-07-02 10:24:06.429 (MakeLab Energy) Device created: MakeLab Energy - Voltage 
2019-07-02 10:24:06.429 (MakeLab Energy) Creating device 'Current'. 
2019-07-02 10:24:06.430 (MakeLab Energy) Device created: MakeLab Energy - Current 
2019-07-02 10:24:06.430 (MakeLab Energy) Creating device 'Powerswitch'. 
2019-07-02 10:24:06.431 (MakeLab Energy) Device created: MakeLab Energy - Powerswitch 
2019-07-02 10:24:06.431 (MakeLab Energy) Creating new devices: OK 
2019-07-02 10:24:06.431 (MakeLab Energy) Heartbeat set: 60 
2019-07-02 10:24:06.431 (MakeLab Energy) Pushing 'PollIntervalDirective' on to queue 
2019-07-02 10:24:06.431 (MakeLab Energy) Datapoints:1467,1471,1473,1465 
2019-07-02 10:24:06.431 (MakeLab Energy) Processing 'PollIntervalDirective' message 
2019-07-02 10:24:06.431 (MakeLab Energy) Heartbeat interval set to: 60. 
2019-07-02 10:24:06.423 Status: (MakeLab Energy) Entering work loop. 
2019-07-02 10:24:06.424 Status: (MakeLab Energy) Initialized version 1.0 (Build 20190702), author 'rwbL'
```

### Domoticz Device List
Idx, Hardware, Name, Type, SubType, Data
74, MakeLab Energy, Energy, General, kWh, 17.685 kWh
75, MakeLab Energy, Voltage, General, Voltage, 231.1 V
76, MakeLab Energy, Current, General, Current, 0.22 A
77, MakeLab Energy, Powerswitch, Light/Switch, Switch, On

### Domoticz Log Entry with Debug=False
The plugin runs every 60 seconds (Heartbeat interval).
```
2021-01-25 12:57:14.640 (MakeLab Energy) HMIP-PSM: E=31.4;17671.9,V=229.6,A=0.23,S=true;1
```

## Domoticz dzVents Script alert_energy_kwh
This is an example on how to alert via email
```
--[[
    alert_energy_kwh.dzvents
    Plugga (homematicIP device HmIP-PSM) Alert Example.
    Send notification if the actual watt exceeds defined theshold.
    20210120 rwbl
]]--

local IDX_ENERGY = 74;   -- Type General, SubType kWh
local TH_ENERGY = 32;

return {
	on = {
		devices = {
			IDX_ENERGY
		}
	},
    data = {
        notified = { initial = 0 }
    },
	execute = function(domoticz, device)
	    -- domoticz.log(('Device %s state changed to %s (%d) %.2f.'):format(
		--     device.name, device.sValue, device.nValue, device.actualWatt), domoticz.LOG_INFO)
		if device.actualWatt > TH_ENERGY and domoticz.data.notified == 0 then
		    domoticz.data.notified = 1
            -- Send notification via email
            local subject = ('ENERGY ALERT'):format()
            local message = ('Energy %s %.2fW is above threshold %dW.'):format(
                device.name, device.actualWatt, TH_ENERGY)
            domoticz.log(subject .. ':' .. message)
            domoticz.notify(subject, message, domoticz.PRIORITY_HIGH)
        else
            if domoticz.data.notified == 1 then 
                domoticz.data.notified = 0
            end
        end
	end
}
```

## ToDo
See TODO.md
