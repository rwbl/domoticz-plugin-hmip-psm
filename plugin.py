# Domoticz Home Automation - homematicIP Pluggable Switch and Meter (HMIP-PSM)
# Switch and measure, in regular intervals, the power (W), energy (Wh), voltage (V), current (mA).
# Dependencies:
# RaspberryMatic XML-API CCU Addon (https://github.com/hobbyquaker/XML-API)
# Library ElementTree (https://docs.python.org/3/library/xml.etree.elementtree.html#)
# Notes:
# 1. After every change: delete the hardware using the plugin homematicIP Thermostat
# 2. After every change: restart domoticz by running from terminal the command: sudo service domoticz.sh restart
# 3. Domoticz Python Plugin Development Documentation (https://www.domoticz.com/wiki/Developing_a_Python_plugin)
# 4. Only two adevice attributes are used. The plugin is flexible to add more attributes as required (examples WTH-2: HUMIDITY, eTRV-2: LEVEL)
#
# Author: Robert W.B. Linn
# Version: See plugin xml definition

"""
<plugin key="HmIP-PSM" name="homematicIP Pluggable Switch and Meter (HmIP-PSM)" author="rwbL" version="1.5.1 (Build 20210125)">
    <description>
        <h2>homematicIP Pluggable Switch and Meter (HmIP-PSM) v1.5.1</h2>
        <ul style="list-style-type:square">
            <li>Switch the device On or Off.</li>
            <li>Measure, in regular intervals, the power (W), energy (Wh), voltage (V), current (mA).</li>
        </ul>
        <h3>Domoticz Devices (Type,SubType) [XML-API Device Datapoint Type]</h3>
        <ul style="list-style-type:square">
            <li>Energy (kWh) [ENERGY_COUNTER] [POWER]</li>
            <li>Voltage (Voltage) [VOLTAGE]</li>
            <li>Current (Current) [CURRENT]</li>
            <li>Switch (Switch) [STATE]</li>
        </ul>
        <h3>Hardware Configuration</h3>
        <ul style="list-style-type:square">
            <li>CCU IP Address (default: 192.168.1.225)</li>
            <li>Device ID (default: 1418, get via XML-API script http://ccu-ip-address/addons/xmlapi/statelist.cgi)</li>
            <li>Datapoint ID STATE (default: 1451, get via XML-API script http://ccu-ip-address/addons/xmlapi/statelist.cgi using HomeMatic WebUI Device Channel, i.e. HmIP-PSM 0001D3C99C6AB3:3 (switch))</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="CCU IP" width="200px" required="true" default="192.168.1.225"/>
        <param field="Mode1" label="Device ID" width="75px" required="true" default="1418"/>
        <param field="Mode2" label="Datapoint ID STATE" width="75px" required="true" default="1451"/>
        <param field="Mode5" label="Check Interval (sec)" width="75px" required="true" default="60"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug" default="true"/>
                <option label="False" value="Normal"/>
            </options>
        </param>
    </params>
</plugin>
"""

# Set the plugin version
PLUGINVERSION = "v1.5.1"
PLUGINSHORTDESCRIPTON = "HMIP-PSM"

## Imports
import Domoticz
import urllib
import urllib.request
from datetime import datetime
import json
import xml.etree.ElementTree as etree

## Domoticz device units used for creating & updating devices
UNIT_ENERGY_COUNTER = 1                 # TypeName: kWh
TYPE_ENERGY_COUNTER = "ENERGY_COUNTER"
TYPE_POWER = "POWER"                    # NOT USED = Measured only
UNIT_VOLTAGE = 2                        # TypeName: Voltage
TYPE_VOLTAGE = "VOLTAGE"
UNIT_CURRENT = 3                        # TypeName: Current (Single)
TYPE_CURRENT = "CURRENT"
UNIT_SWITCH = 4                         # TypeName: Switch
TYPE_STATE = "STATE"

# Task to perform
TASKSWITCH = 1
TASKMETER = 2

class BasePlugin:

    def __init__(self):

        # HTTP Connection
        self.httpConn = None
        self.httpConnected = 0

        # Task to complete - default is measure energy
        self.Task = TASKMETER

        # Switch state as string as the datapoint value defined 
        # The switchid is assigned during first check interval
        self.SwitchID = ""
        self.SwitchState = "unknown"
        
        # The Domoticz heartbeat is set to every 60 seconds. Do not use a higher value as Domoticz message "Error: hardware (N) thread seems to have ended unexpectedly"
        # The Soil Moisture Monitor is read every Parameter.Mode5 seconds. This is determined by using a hearbeatcounter which is triggered by:
        # (self.HeartbeatCounter * self.HeartbeatInterval) % int(Parameter.Mode5) = 0
        self.HeartbeatInterval = 60
        self.HeartbeatCounter = 0
        return

    def onStart(self):
        Domoticz.Debug(PLUGINSHORTDESCRIPTON + " " + PLUGINVERSION)
        Domoticz.Debug("onStart called")
        Domoticz.Debug("Debug Mode:" + Parameters["Mode6"])

        if Parameters["Mode6"] == "Debug":
            self.debug = True
            Domoticz.Debugging(1)
            DumpConfigToLog()

        # if there no  devices, create these
        if (len(Devices) == 0):
            Domoticz.Debug("Creating new devices ...")
            Domoticz.Device(Name="Energy", Unit=UNIT_ENERGY_COUNTER, TypeName="kWh", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNIT_ENERGY_COUNTER].Name)
            Domoticz.Device(Name="Voltage", Unit=UNIT_VOLTAGE, TypeName="Voltage", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNIT_VOLTAGE].Name)
            Domoticz.Device(Name="Current", Unit=UNIT_CURRENT, TypeName="Current (Single)", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNIT_CURRENT].Name)
            Domoticz.Device(Name="Powerswitch", Unit=UNIT_SWITCH, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNIT_SWITCH].Name)
            Domoticz.Debug("Creating new devices: OK")

        # Set the switchid from parameter mode2
        self.SwitchID = Parameters["Mode2"]
        Domoticz.Debug("SwitchID: "+self.SwitchID)
        
        # Heartbeat
        Domoticz.Debug("Heartbeat set: "+Parameters["Mode5"])
        Domoticz.Heartbeat(self.HeartbeatInterval)
        return

    def onStop(self):
        Domoticz.Debug("Plugin is stopping.")

    # Send the url parameter (GET request)
    # If task = energy then to obtain device state information in xml format
    # If task = switch then switch using the self.switchstate
    # The http response is parsed in onMessage()
    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called. Status: " + str(Status) + ", Description:" + Description)
        if (Status == 0):
            Domoticz.Debug("CCU connected successfully.")
            self.httpConnected = 1

            # request device id datapoints to get the energy data
            if self.Task == TASKMETER:
                ## url example = 'http://192.168.1.225/addons/xmlapi/state.cgi?device_id=1418'
                url = '/addons/xmlapi/state.cgi?device_id=' + Parameters["Mode1"]
                       
            # request state change for the switch with datapoint and new value
            if self.Task == TASKSWITCH:
                ## url example = 'http://192.168.1.225/addons/xmlapi/statechange.cgi?ise_id=1451&new_value=true'
                url = '/addons/xmlapi/statechange.cgi?ise_id=' + self.SwitchID + '&new_value=' + self.SwitchState

            Domoticz.Debug(url)
            sendData = {'Verb' : 'GET',
                        'URL' : url,
                        'Headers' : { 'Content-Type': 'text/xml; charset=utf-8', \
                                        'Connection': 'keep-alive', \
                                        'Accept': 'Content-Type: text/html; charset=UTF-8', \
                                        'Host': Parameters["Address"], \
                                        'User-Agent':'Domoticz/1.0' }
                       }
            self.httpConn.Send(sendData)
            self.httpConn.Disconnect
            return
        else:
            self.httpConnected = 0
            Domoticz.Error("IP connection faillure ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Port"]+" with error: "+Description)
            return

    # Parse the http xml response and update the domoticz devices
    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")
        
        # If not conected, then leave
        if self.httpConnected == 0:
            return

        # Parse the JSON Data Object with keys Status (Number) and Data (ByteArray)
        ## 200 is OK
        responseStatus = int(Data["Status"])
        Domoticz.Debug("STATUS=responseStatus:" + str(responseStatus) + " ;Data[Status]="+Data["Status"])

        ## decode the data using the encoding as given in the xml response string
        responseData = Data["Data"].decode('ISO-8859-1')
        ## Domoticz.Debug("DATA=" + responseData)

        if (responseStatus != 200):
            Domoticz.Error("XML-API response faillure: " + str(responseStatus) + ";" + resonseData)
            return

        # Parse the xml string 
        # Get the xml tree - requires several conversions
        tree = etree.fromstring(bytes(responseData, encoding='utf-8'))

        # Handle the respective task to update the domoticz devices
        
        if self.Task == TASKMETER:
            Domoticz.Debug("TASKMETER")
            # Get the values for energy counter, power, voltage, current
            # <datapoint name="HmIP-RF.0001D3C99C6AB3:6.ENERGY_COUNTER" type="ENERGY_COUNTER" ise_id="1467" value="17221.300000" valuetype="4" valueunit="Wh" timestamp="1611423150"/>
            energycountervalue = tree.find(".//datapoint[@type='" + TYPE_ENERGY_COUNTER + "']").attrib['value']   # Domoticz.Debug(energycountervalue[0])
            #<datapoint name="HmIP-RF.0001D3C99C6AB3:6.POWER" type="POWER" ise_id="1471" value="49.890000" valuetype="4" valueunit="W" timestamp="1611423150"/>
            powervalue = tree.find(".//datapoint[@type='" + TYPE_POWER + "']").attrib['value']  # Domoticz.Debug(powervalue[0])
            # <datapoint name="HmIP-RF.0001D3C99C6AB3:6.VOLTAGE" type="VOLTAGE" ise_id="1473" value="224.200000" valuetype="4" valueunit="V" timestamp="1611423150"/>
            voltagevalue = tree.find(".//datapoint[@type='" + TYPE_VOLTAGE + "']").attrib['value']  # Domoticz.Debug(voltagevalue[0])
            # <datapoint name="HmIP-RF.0001D3C99C6AB3:6.CURRENT" type="CURRENT" ise_id="1465" value="285.000000" valuetype="4" valueunit="mA" timestamp="1611423150"/>
            currentvalue = tree.find(".//datapoint[@type='" + TYPE_CURRENT + "']").attrib['value']  # Domoticz.Debug(currentvalue[0])
            # <datapoint name="HmIP-RF.0001D3C99C6AB3:3.STATE" type="STATE" ise_id="1451" value="true" valuetype="2" valueunit="" timestamp="1611423150"/>
            switchstate = tree.find(".//datapoint[@type='" + TYPE_STATE + "']").attrib['value']                                       # Domoticz.Debug(switchstate[0])

            ## Update the devices and log
            Devices[UNIT_ENERGY_COUNTER].Update( nValue=0, sValue=str(round(float(powervalue),2)) + ";" + str(round(float(energycountervalue),2)) )
            Devices[UNIT_VOLTAGE].Update( nValue=0, sValue=str(round(float(voltagevalue),2)) )
            Devices[UNIT_CURRENT].Update( nValue=0, sValue=str(round(float(currentvalue) * 0.001,2)) )
            # Domoticz.Log(PLUGINSHORTDESCRIPTON + ": E=" + Devices[UNIT_ENERGY_COUNTER].sValue + ",V=" +  Devices[UNIT_VOLTAGE].sValue + ",A=" + Devices[UNIT_CURRENT].sValue + ",S=" + switchstate + ";" + str(Devices[UNIT_SWITCH].nValue) )

            ## Option to sync the switchstate if changed by the homematic webui
            if (switchstate == 'true') and (Devices[UNIT_SWITCH].nValue == 0):
                Devices[UNIT_SWITCH].Update( nValue=1, sValue= '0')
                Domoticz.Debug("Switch SYNC=" + switchstate + ";" + str(Devices[UNIT_SWITCH].nValue) )

            if (switchstate == 'false') and (Devices[UNIT_SWITCH].nValue == 1):
                Devices[UNIT_SWITCH].Update( nValue=0, sValue= '0')
                Domoticz.Debug("Switch SYNC=" + switchstate + ";" + str(Devices[UNIT_SWITCH].nValue) )

        if self.Task == TASKSWITCH:
            # The xml response data for the switch is like:
            # <?xml version="1.0" encoding="ISO-8859-1" ?><result><changed id="1451" new_value="false" /></result>
            Domoticz.Debug("TASKSWITCH:" + responseData)
            # Update the switch state
            if (self.SwitchState == 'true'):
                Devices[UNIT_SWITCH].Update( nValue=1, sValue= '0')
            else:
                Devices[UNIT_SWITCH].Update( nValue=0, sValue= '0')        

        return
        
    # Handle the state change of the switch. Convert state 'On' or 'Off' to 'true' or 'false' (as used by the xml-api script statecange)
    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        
        if (Command == 'On'):
            self.SwitchState = 'true'
        else:
            self.SwitchState = 'false'

        # Create IP connection and connect - see further onConnect where the parameters are send
        self.httpConn = Domoticz.Connection(Name="CCU-"+Parameters["Address"], Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port="80")
        self.httpConn.Connect()
        self.httpConnected = 0
        self.Task = TASKSWITCH
        return

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    # Check the hearbeat counter and setup the http connection to the ccu
    # After connection, there url parameter are send - see onConnect()
    def onHeartbeat(self):
        self.HeartbeatCounter = self.HeartbeatCounter + 1
        Domoticz.Debug("onHeartbeat called. Counter=" + str(self.HeartbeatCounter * self.HeartbeatInterval) + " (Heartbeat=" + Parameters["Mode5"] + ")")
        # check the heartbeatcounter against the heartbeatinterval
        if (self.HeartbeatCounter * self.HeartbeatInterval) % int(Parameters["Mode5"]) == 0:
            try:
                # Create IP connection and connect
                self.httpConn = Domoticz.Connection(Name="CCU-"+Parameters["Address"], Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port="80")
                self.httpConn.Connect()
                self.httpConnected = 0
                self.Task = TASKMETER
            except:
                Domoticz.Error("IP connection faillure. Check settings and restart Domoticz.")
        return
        
global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

#
## Generic helper functions
#

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

