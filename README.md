# Domoticz Plugin homematicIP Pluggable Switch and Meter (HMIP-PSM)
v1.0 (Build 20190702)

# Objectives
* To switch the device on and off.
* To measure, in regular intervals, the power (W), energy (Wh), voltage (V), current (mA).

_Abbreviations_: GUI=Domoticz Web UI, CCU=HomeMatic Central-Control-Unit

## Solution
To switch the power on/off and measure power (W) & energy consumption(Wh), a homematicIP Pluggable Switch and Meter (HMIP-PSM, Product ref.: 140666A0) is used.
The HMIP-PSM is 
* an actuator switch with status report measured value channel.
* connected to a homematicIP system.

The homematic IP system used is a [RaspberryMatic](https://raspberrymatic.de/) operating system running the HomeMatic Central-Control-Unit (CCU).

The CCU has the additional software XML-API CCU Addon installed.

Communication between Domoticz and the CCU is via HTTP XML-API requests with HTTP XML response.

__Note__
This is my first attempt to create a Domoticz plugin for a HomeMatic device connected to a CCU (RaspberryMatic).
There might be better solutions, but so far this solution is working ok .. and will be refined whilst working on next devices.

![domoticz-plugin-hmip-psm-f](https://user-images.githubusercontent.com/47274144/60536359-5ac90980-9d06-11e9-8863-4b968fb69d2c.PNG)

## Hardware
* Raspberry Pi 3B+ (RaspberryMatic System)
* homematicIP Pluggable Switch and Meter (HMIP-PSM, Product ref.: 140666A0)

## Software
Versions for developing & using this plugin.
* Raspberry Pi Raspian  4.19.42-v7+ #1219
* RaspberryMatic 3.45.7.20190622 [info](https://raspberrymatic.de/)
* XML-API CCU Addon 1.20 [info](https://github.com/jens-maus/XML-API)
* Python 3.5.3
* Python module ElementTree

## Prepare
The RaspberryMatic system has been setup according [these](https://github.com/jens-maus/RaspberryMatic) guidelines.

The XML-API CCU Addon is required and installed via the HomeMatic WebUI > Settings > Control panel > Additional software (download the latest version from previous URL shared).

### Python Module ElementTree
The Python Module **ElementTree XML API** is used to parse the XML-API response.
This module is part of the standard package and provides limited support for XPath expressions for locating elements in a tree. 

_Hint_
(Optional)
For full XPath support install the module **ElementPath** from the terminal command-line for Python 2.x and 3.x via pip:
``` 
sudo pip install elementpath
sudo pip3 install elementpath
```

## Plugin Folder and File
Each plugin requires a dedicated folder which contains the plugin, mandatory named plugin.py.
``` 
mkdir /home/pi/domoticz/plugins/hmip-psm
``` 

As a starter, take the template from [here](https://github.com/domoticz/domoticz/blob/master/plugins/examples/BaseTemplate.py) .
Save as __plugin.py__ (this is a mandatory file name) in the folder __/home/pi/domoticz/plugins/hmip-psm__.

## Development Setup
Development PC:
* A shared drive Z: pointing to /home/pi/domoticz
* GUI > Setup > Log
* GUI > Setup > Hardware
* GUI > Setup > Devices
* WinSCP session connected to the Domoticz server (upload files)
* Putty session connected to the Domoticz server (restarting Domoticz during development)

The various GUI's are required to add the new hardware with its devices and monitor if the plugin code is running without errors.

## Development Iteration
The development process step used are:
1. Develop z:\plugins\hmip-psm\plugin.py
2. Make changes and save plugin.py
3. Restart Domoticz from a terminal: sudo service domoticz.sh restart
4. Wait a moment and refresh GUI > Log
5. Check the log and fix as required

!IMPORTANT!
In the **GUI > Setup > Settings**, enable accepting new hardware.
This is required to add new devices created by the plugin.

## Datapoints
To communicate between the CCU and Domoticz vv, the ise_id's for devices, channels and datapoint are used (id solution).
Another option could be to use the name (i.e. name="HmIP-RF.0001D3C99C6AB3:3.STATE") but this requires to obtain the full device state list for every action.
Tested the name solution, but the communication was rather slow.
The id soltion is much faster and also more flexible in defining and obtaning information for devices, channels and datapoints.

## Device Datapoint ID
Steps to obtain the device datapoint id to be able to switch or read the meter data.
The device datapoint id will be used in the plugin __parameter Mode1__.

### Get Device Channels
Get the device channels from the HomeMatic WebUI > Status and control > Devices > select name HMIP-PSM 0001D3C99C6AB3.
There are two channels:
* HMIP-PSM 0001D3C99C6AB3:3 Switch actuator
* HMIP-PSM 0001D3C99C6AB3:6 Status report measured value channel

### Get All Devices Statelist
Submit in a webbrowser the HTTP URL XMLAPI request:
``` 
http://ccu-ip-address/config/xmlapi/statelist.cgi
``` 
The HTTP response is an XML string with the state list for all devices used (can be rather large depending number of devices connected).

### Get Channel Datapoints
In the XML response, search for the channels name HMIP-PSM 0001D3C99C6AB3:3 (the switch) and HMIP-PSM 0001D3C99C6AB3:6 (the meter).

__Channel HMIP-PSM 0001D3C99C6AB3:3__
_Example_
``` 
<channel ise_id="1446" name="HMIP-PSM 0001D3C99C6AB3:3" operate="true" visible="true" index="3">
	<datapoint ise_id="1448" name="HmIP-RF.0001D3C99C6AB3:3.PROCESS" operations="5" timestamp="1562085867" valueunit="" valuetype="16" value="0" type="PROCESS"/>
	<datapoint ise_id="1449" name="HmIP-RF.0001D3C99C6AB3:3.SECTION" operations="5" timestamp="1562085867" valueunit="" valuetype="16" value="2" type="SECTION"/>
	<datapoint ise_id="1450" name="HmIP-RF.0001D3C99C6AB3:3.SECTION_STATUS" operations="5" timestamp="1562085867" valueunit="" valuetype="16" value="0" type="SECTION_STATUS"/>
	<datapoint ise_id="1451" name="HmIP-RF.0001D3C99C6AB3:3.STATE" operations="7" timestamp="1562085867" valueunit="" valuetype="2" value="true" type="STATE"/>
</channel>
``` 
The datapoint type="STATE" is used to switch the device via the XML-API script statechange.cgi using the ise_id (i.e. 1451).
This datapoint id will be used in the plugin __parameter Mode2__.
The value is from valuetype 2 = boolean, i.e. true or false.

__Channel HMIP-PSM 0001D3C99C6AB3:6__
_Example_
``` 
<channel ise_id="1464" name="HMIP-PSM 0001D3C99C6AB3:6" operate="true" visible="true" index="6">
	<datapoint ise_id="1465" name="HmIP-RF.0001D3C99C6AB3:6.CURRENT" operations="5" timestamp="1561984819" valueunit="mA" valuetype="4" value="292.000000" type="CURRENT"/>
	<datapoint ise_id="1466" name="HmIP-RF.0001D3C99C6AB3:6.CURRENT_STATUS" operations="5" timestamp="1561984819" valueunit="" valuetype="16" value="0" type="CURRENT_STATUS"/>
	<datapoint ise_id="1467" name="HmIP-RF.0001D3C99C6AB3:6.ENERGY_COUNTER" operations="5" timestamp="1561984819" valueunit="Wh" valuetype="4" value="431.200000" type="ENERGY_COUNTER"/>
	<datapoint ise_id="1468" name="HmIP-RF.0001D3C99C6AB3:6.ENERGY_COUNTER_OVERFLOW" operations="5" timestamp="1561984819" valueunit="" valuetype="2" value="false" type="ENERGY_COUNTER_OVERFLOW"/>
	<datapoint ise_id="1469" name="HmIP-RF.0001D3C99C6AB3:6.FREQUENCY" operations="5" timestamp="1561984819" valueunit="Hz" valuetype="4" value="49.990000" type="FREQUENCY"/>
	<datapoint ise_id="1470" name="HmIP-RF.0001D3C99C6AB3:6.FREQUENCY_STATUS" operations="5" timestamp="1561984819" valueunit="" valuetype="16" value="0" type="FREQUENCY_STATUS"/>
	<datapoint ise_id="1471" name="HmIP-RF.0001D3C99C6AB3:6.POWER" operations="5" timestamp="1561984819" valueunit="W" valuetype="4" value="41.580000" type="POWER"/>
	<datapoint ise_id="1472" name="HmIP-RF.0001D3C99C6AB3:6.POWER_STATUS" operations="5" timestamp="1561984819" valueunit="" valuetype="16" value="0" type="POWER_STATUS"/>
	<datapoint ise_id="1473" name="HmIP-RF.0001D3C99C6AB3:6.VOLTAGE" operations="5" timestamp="1561984819" valueunit="V" valuetype="4" value="230.800000" type="VOLTAGE"/>
	<datapoint ise_id="1474" name="HmIP-RF.0001D3C99C6AB3:6.VOLTAGE_STATUS" operations="5" timestamp="1561984819" valueunit="" valuetype="16" value="0" type="VOLTAGE_STATUS"/>
</channel>
``` 
Various datapoint types (with id) are used: CURRENT (1465), ENERGY_COUNTER (1467), POWER (1471), VOLTAGE (1473).
The datapoints id will be used in the plugin __parameter Mode3__ (comma separated list).

### Test Switching
Test switching the device via webbrowser HTTP URL XML-API request using the statechange.cgi script with the datapoint id and new value true or false.
Switch ON:
``` 
http://ccu-ip-address/config/xmlapi/statechange.cgi?ise_id=1451&new_value=true
``` 
The HTTP response is an XML string.
_Example_
``` 
<?xml version="1.0" encoding="ISO-8859-1"?>
<result>
	<changed id="1451" new_value="true"/>
</result>
``` 
Switch OFF:
``` 
http://ccu-ip-address/config/xmlapi/statechange.cgi?ise_id=1451&new_value=false
``` 

_Note_
Check the HomeMatic WebUI if the state of the channel has changed as well.

<ADD SCREENSHOT>

## Domoticz Devices
The **Domoticz homematicIP Pluggable Switch and Meter Devices** created are Name (TypeName):
* Energy (kWh)
* Voltage (Voltage)
* Current (Current)
* Powerswitch (Switch)

![domoticz-plugin-hmip-psm-d](https://user-images.githubusercontent.com/47274144/60536568-ce6b1680-9d06-11e9-98d0-f482067f062f.png)

## Plugin Pseudo Code
Source code (well documented): plugin.py in folder /home/pi/domoticz/plugins/hmip-psm
__INIT__
* set self vars to handle http connection, heartbeat count, datapoints list, switch state, set task
	
__FIRST TIME__
* _onStart_ to create the Domoticz Devices
	
__NEXT TIME(S)__
* _onHeardbeat_
	* create ip connection http with the raspberrymatic
* _onConnect_
	* depending task, define the data (get,url,headers) to send to the ip connection
	* send the data and disconnect
* _onMessage_
	* parse the xml response
	* if task switch update switch device and sync with homematic switch state
	* if task meter update meter (enegergy) devices
* _onCommand_
	* set task switch and create ip connection which is handled by onConnect

If required, add the devices manually to the Domoticz Dashboard or create a roomplan / floorplan.

## Restart Domoticz
Restart Domoticz to find the plugin:
```
sudo systemctl restart domoticz.service
```

**Note**
When making changes to the Python plugin code, ensure to restart Domoticz and refresh any of the Domoticz Web UI's.
This is the iteration process during development - build the solution step-by-step.

## Domoticz Add Hardware
**IMPORTANT**
Prior adding, set GUI > Settings the option to allow new hardware.
If this option is not enabled, no new devices are created.
Check the GUI > Setup > Log as error message Python script at the line where the new device is used
(i.e. Domoticz.Debug("Device created: "+Devices[1].Name))

In the GUI > Setup > Hardware add the new hardware **homematicIP Pluggable Switch and Meter (HMIP-PSM)**.
The initial check interval is set at 60 seconds. This is a good value for testing, but for final version set to higher value like every 5 minutes (300 seconds).

## Add Hardware - Check the Domoticz Log
After adding, ensure to check the Domoticz Log (GUI > Setup > Log)
Example:
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

## Domoticz Log Entry with Debug=False
The plugin runs every 60 seconds (Heartbeat interval) which is shown in the Domoticz log.
```
2019-07-02 19:13:42.528 (MakeLab Energy) Updated: E=26.46;82.8,V=231.2,A=0.19,S=true;1
```

## ToDo
See TODO.md
