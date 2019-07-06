### Status 20190706

#### NEW: Sync switch state when changed in HomeMatic WebUI
A solution is implemented where Domoticz is triggering requesting the state from the CCU.
This is done during the check interval to update meter (energy) data.
Seeking for a solution where the CCU triggers the update of the Domoticz device.
_Example_
```
! Update a Domoticz device ia HTTP REST Request
! Sample set text of device with idx 36
! This script can be used to update device in domotcz in case homematic device changes state
string stderr;
string stdout;
string url="'http://domoticz-ip-address:8080/json.htm?type=command&param=udevice&idx=36&nvalue=0&svalue=Hello World!'";
system.Exec("wget -q -O - " #url, stdout, stderr);
WriteLine(stdout);
WriteLine(stderr);
```
_Status_
Not started.
