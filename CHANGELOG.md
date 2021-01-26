# Changelog domoticz-plugin-hmip-psm

### v1.5.1 (Build 20210125)
* NEW: Changed datapoint attribute from ise_id to type. No need to define the datapoint ise_id anymore, only the device ise_id. 
* UPD: Minor changes.

### v1.1.0 (Build 20210118)
* CHG: Changed XML Parser from lxml to ElementTree (in Python standard package) - encountered lxml issue ("ImportError") adding multiple devices with Domoticz 2020 or higher (not found an lxml solution).
* UPD: Various minor improvements

### v1.0.3 (Build 20191223)
* UPD: various minor corrections.

### v1.0.1 (Build 20190706)
* UPD: Plugin definition enhanced; Changed error messages do domoticz.error.

### v1.0.0 (Build 20190702)
* NEW: First version published.
