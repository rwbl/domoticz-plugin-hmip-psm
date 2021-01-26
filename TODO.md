# ToDo domoticz-plugin-hmip-psm
Status 20190706

### NEW: Sync switch state when changed in HomeMatic WebUI
A solution is implemented where Domoticz is triggering requesting the state from the CCU.
This is done during the check interval to update meter (energy) data.
Seeking for a solution where the CCU triggers the update of the Domoticz device.
_Status_
It is advised by RaspberryMatic to use the addon CUxD.
Tested an example to update a domoticz text device via CUxD device (remote control)
_Example_
```
string sDate = system.Date("%d.%m.%Y"); ! sDate = "09.08.2019"; 
string sTime = system.Date("%H:%M:%S"); ! sTime = "07:32:00"; 
string nIdx = 36;
string sMsg = sDate # " " # sTime # " - Threshold reached! Take action...";
string cAmp = "&";
string sDomUrl = "'http://ccu-ip-address:8080/json.htm";
string sUrl = sDomUrl#"?type=command"#cAmp#"param=udevice"#cAmp#"idx="#nIdx#cAmp#"nvalue=0"#cAmp#"svalue="#sMsg#"'";

! OPTION: Run the command without a return result
! res = dom.GetObject("CUxD.CUX2801001:1.CMD_EXEC").State("wget -q -O - "#sUrl);

! OPTION: Run the command with a return result
! Define the command to execute
dom.GetObject("CUxD.CUX2801001:1.CMD_SETS").State ("wget -q -O - "#sUrl);

! Set the return flag to 1 to be able to read the json result
dom.GetObject("CUxD.CUX2801001:1.CMD_QUERY_RET").State (1);

! Start the command, wait till completed and get the result JSON string, i.e.
! {"status" : "OK","title" : "Update Device"}
! NOTE: The script running on the CCU waits until the completion - ensure not to execute commands which take long time.
string sRes = dom.GetObject("CUxD.CUX2801001:1.CMD_RETS").State();
! WriteLine("VT="#sRes.VarType()#"/"#sRes); ! VT=4, {"status" : "OK","title" : "Update Device"}

! handle result
var dl = dom.GetObject ("DomoticzLog");
! Update the var with result text
if (sRes.Find("OK") > 0) {
  dl.Variable("Last update OK")
}
else {
  dl.Variable("Last update ERROR")
};
! WriteLine("VT="#dl.VarType());  ! VT=9
! WriteLine(dl.Variable());       ! shows the last update string
```
