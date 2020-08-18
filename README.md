# Dashboard Writer - Push CAN Data to InfluxDB [BETA]

This project lets you DBC decode CAN data from your CANedge into physical values - and push the data into a time series database. From here, the data can be displayed via your own customized, open source Grafana dashboard.

For the step-by-step guide to setting up your dashboard, see the [CANedge intro](https://canlogger.csselectronics.com/canedge-getting-started/log-file-tools/browser-dashboards).

---

## Features
```
- easily load MDF4 log files from local disk or S3 server
- fetch data from hardcoded time period - or automate with dynamic periods
- DBC-decode data and optionally extract specific signals
- optionally resample data to specific frequency
- write the data to your own InfluxDB time series database
```
---

## Requirements
To use the script, install dependencies via the `requirements.txt`:

``pip install -r requirements.txt``

---
## Deployment

### 1: Test script with sample data 

1. Download the CANedge J1939 [sample data](https://canlogger.csselectronics.com/canedge-getting-started/log-file-tools/) and extract next to script
2. In `inputs.py` add your InfluxDB details and run `main.py`
3. Verify success by viewing the data in the InfluxDB explorer (for Jan 13, 2020)

*Note: If you use a free InfluxDB Cloud user, the sample data will be removed after a period as it is >30 days old.*

### 2: Modify script with your own details 
1. Local data: Add your own data next to the scripts as per the SD structure:
   `LOG/<device_ID>/<session>/<split>.MF4`
2. S3 server: Add your S3 server details in `inputs.py` and set `use_s3 = True`
3. In `inputs.py` update the DBC path and the device list to match yours
4. In `last_run.txt`, specify from when you wish to load log files (e.g. `2020-01-13 00:00:00`)
5. Optionally modify the signal filters or resampling frequency


### 3: Enable dynamic start time
1. In `inputs.py` set `dynamic = True` 
2. Follow the CANedge Intro guide for setting up e.g. Windows Task Scheduler

---
## Deleting data from InfluxDB 
If you need to delete data in InfluxDB that you e.g. uploaded as part of a test, you can use the `delete_influx(name)` function from `utils.py`. You can call this by parsing the name of the 'measurement' to delete (i.e. the device serial number).
