# Domoticz Home Automation - homematicIP Pluggable Switch and Meter (HMIP-PSM)
# Switch and measure, in regular intervals, the power (W), energy (Wh), voltage (V), current (mA).
# @author Robert W.B. Linn
# @version See plugin xml definition
#
# NOTE: after every change run
# sudo service domoticz.sh restart
# Domoticz Python Plugin Development Documentation:
# https://www.domoticz.com/wiki/Developing_a_Python_plugin


"""
<plugin key="HMIP-PSM" name="homematicIP Pluggable Switch and Meter (HMIP-PSM)" author="rwbL" version="1.0 (Build 20190702)">
    <description>
        <h2>homematicIP Pluggable Switch and Meter (HMIP-PSM) v1.0</h2>
        <ul style="list-style-type:square">
            <li>Switch the device On or Off.</li>
            <li>Measure, in regular intervals, the power (W), energy (Wh), voltage (V), current (mA).</li>
        </ul>
        <h2>Domoticz Devices Name (TypeName)</h2>
        <ul style="list-style-type:square">
            <li>Energy (kWh)</li>
            <li>Voltage (Voltage)</li>
            <li>Current (Current)</li>
            <li>Powerswitch (Switch)</li>
        </ul>
        <h2>Configuration</h2>
        <ul style="list-style-type:square">
            <li>Address (CCU IP address, i.e. 192.168.1.225)</li>
            <li>IDs (obtained via XML-API script http://ccu-ip-address/config/xmlapi/statelist.cgi using the HomeMatic WebUI Device Channel, i.e. HMIP-PSM 0001D3C99C6AB3:3 (switch) or :6 (meter):</li>
            <li>Device HMIP-PSM (i.e. 1418)</li>
            <li>Datapoint SWITCH: STATE (i.e. 1451)</li>
            <li>Datapoints ENERGY(#4): ENERGY_COUNTER, POWER, VOLTAGE, CURRENT as comma separated list in this order (i.e. 1467,1471,1473,1465)</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="Host" width="200px" required="true" default="ccu-ip-address"/>
        <param field="Mode1" label="Device ID" width="75px" required="true" default="1418"/>
        <param field="Mode2" label="Datapoint SWITCH STATE" width="75px" required="true" default="1451"/>
        <param field="Mode3" label="Datapoints ENERGY" width="200px" required="true" default="1467,1471,1473,1465"/>
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
PLUGINVERSION = "v1.0"
PLUGINSHORTDESCRIPTON = "HMIP-PSM"

## Imports
import Domoticz
import urllib
import urllib.request
from datetime import datetime
import json
from lxml import etree

## Domoticz device units used for creating & updating devices
UNITENERGY = 1      # TypeName: kWh
UNITVOLTAGE = 2     # TypeName: Voltage
UNITCURRENT = 3     # TypeName: Current (Single)
UNITSWITCH = 4      # TypeName: Switch

# Index of the datapoints from the datapoints list
# The datapoints are defined as a comma separated string in parameter Mode2
# Syntax:DATAPOINTINDEX<Type> - without blanks or underscores
DATAPOINTINDEXENERGYCOUNTER = 0
DATAPOINTINDEXPOWER = 1
DATAPOINTINDEXVOLTAGE = 2
DATAPOINTINDEXCURRENT = 3

# Task to perform
TASKSWITCH = 1
TASKMETER = 2

class BasePlugin:

    def __init__(self):

        # HTTP Connection
        self.httpConn = None
        self.httpConnected = 0

        # List of datapoints - energy counter, power, voltage, current
        self.DatapointsList = []

        # Task to complete - default is measure energy
        self.Task = TASKMETER

        # Switch state as string as the datapoint value defined 
        self.SwitchState = 'false'
        
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
            Domoticz.Device(Name="Energy", Unit=UNITENERGY, TypeName="kWh", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITENERGY].Name)
            Domoticz.Device(Name="Voltage", Unit=UNITVOLTAGE, TypeName="Voltage", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITVOLTAGE].Name)
            Domoticz.Device(Name="Current", Unit=UNITCURRENT, TypeName="Current (Single)", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITCURRENT].Name)
            Domoticz.Device(Name="Powerswitch", Unit=UNITSWITCH, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITSWITCH].Name)
            Domoticz.Debug("Creating new devices: OK")

        # Heartbeat
        Domoticz.Debug("Heartbeat set: "+Parameters["Mode5"])
        Domoticz.Heartbeat(self.HeartbeatInterval)

        # Create the datapoints list using the datapoints as defined in the parameter Mode3
        ## The string contains multiple datapoints separated by comma (,). This enables to define more devices.
        DatapointsParam = Parameters["Mode3"]
        Domoticz.Debug("Datapoints:" + DatapointsParam)
        ## Split the parameter string into a list of datapoints
        self.DatapointsList = DatapointsParam.split(',')
        # Check the list length (4 because 4 datapoints required, i.e. energy counter, power, voltage, current)
        if len(self.DatapointsList) < 4:
            ## Devices[UNITTEXTSTATUS].Update( nValue=0, sValue="[ERROR] UID parameter not correct! Should contain 5 UIDs." )
            Domoticz.Log("[ERROR] Datapoints parameter not correct! Should contain 4 datapoints.")
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
                ## url example = 'http://192.168.1.225/config/xmlapi/state.cgi?device_id=1418'
                url = '/config/xmlapi/state.cgi?device_id=' + Parameters["Mode1"]
                       
            # request state change for the switch with datapoint and new value
            if self.Task == TASKSWITCH:
                ## url example = 'http://192.168.1.225/config/xmlapi/statechange.cgi?ise_id=1451&new_value=true'
                url = '/config/xmlapi/statechange.cgi?ise_id=' + Parameters["Mode2"] + '&new_value=' + self.SwitchState

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
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Port"]+" with error: "+Description)
            return

    # Parse the http xml response and update the domoticz devices
    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")
        
        # If not conected, then leave
        if self.httpConnected == 0:
            return

        # Parse the JSON Data Object with keys Status (Number) and Data (ByteArray)
        responseStatus = int(Data["Status"])         # 200 is OK
        # Domoticz.Debug("STATUS="+ str(responseStatus))
        responseData = Data["Data"].decode()         # XML string
        # Domoticz.Debug("DATA=" + responseData)

        if (responseStatus != 200):
            Domoticz.Log("[ERROR] XML-API response: " + str(responseStatus) + ";" + resonseData)
            return

        # Parse the xml string 
        # Get the xml tree - requires several conversions
        tree = etree.fromstring(bytes(responseData, encoding='utf-8'))

        # Handle the respective task to update the domoticz devices
        
        if self.Task == TASKMETER:
            Domoticz.Debug("TASKMETER")
            # Get the values for energy counter, power, voltage, current
            # note that a list is returned from tree.xpath, but holds only 1 value
            energycountervalue = tree.xpath('//datapoint[@ise_id=' + self.DatapointsList[DATAPOINTINDEXENERGYCOUNTER] + ']/@value')   # Domoticz.Debug(energycountervalue[0])
            powervalue = tree.xpath('//datapoint[@ise_id=' + self.DatapointsList[DATAPOINTINDEXPOWER] + ']/@value')  # Domoticz.Debug(powervalue[0])
            voltagevalue = tree.xpath('//datapoint[@ise_id=' + self.DatapointsList[DATAPOINTINDEXVOLTAGE] + ']/@value')  # Domoticz.Debug(voltagevalue[0])
            currentvalue = tree.xpath('//datapoint[@ise_id=' + self.DatapointsList[DATAPOINTINDEXCURRENT] + ']/@value')  # Domoticz.Debug(currentvalue[0])
            switchstate = tree.xpath('//datapoint[@ise_id=' + Parameters['Mode2'] + ']/@value')  # Domoticz.Debug(switchstate[0])
            ## Update the devices and log
            Devices[UNITENERGY].Update( nValue=0, sValue=str(round(float(powervalue[0]),2)) + ";" + str(round(float(energycountervalue[0]),2)) )
            Devices[UNITVOLTAGE].Update( nValue=0, sValue=str(round(float(voltagevalue[0]),2)) )
            Devices[UNITCURRENT].Update( nValue=0, sValue=str(round(float(currentvalue[0]) * 0.001,2)) )
            Domoticz.Log("Updated: E=" + Devices[UNITENERGY].sValue + ",V=" +  Devices[UNITVOLTAGE].sValue + ",A=" + Devices[UNITCURRENT].sValue + ",S=" + switchstate[0] + ";" + str(Devices[UNITSWITCH].nValue) )

            ## Option to sync the switchstate if changed by the homematic webui
            if (switchstate[0] == 'true') and (Devices[UNITSWITCH].nValue == 0):
                Devices[UNITSWITCH].Update( nValue=1, sValue= '0')
                Domoticz.Debug("Switch SYNC=" + switchstate[0] + ";" + str(Devices[UNITSWITCH].nValue) )

            if (switchstate[0] == 'false') and (Devices[UNITSWITCH].nValue == 1):
                Devices[UNITSWITCH].Update( nValue=0, sValue= '0')
                Domoticz.Debug("Switch SYNC=" + switchstate[0] + ";" + str(Devices[UNITSWITCH].nValue) )

        if self.Task == TASKSWITCH:
            # The xml response data for the switch is like:
            # <?xml version="1.0" encoding="ISO-8859-1" ?><result><changed id="1451" new_value="false" /></result>
            Domoticz.Debug("TASKSWITCH:" + responseData)
            # Update the switch state
            if (self.SwitchState == 'true'):
                Devices[UNITSWITCH].Update( nValue=1, sValue= '0')
            else:
                Devices[UNITSWITCH].Update( nValue=0, sValue= '0')        

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
                Domoticz.Log("[ERROR] Check settings, correct and restart Domoticz.")
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

