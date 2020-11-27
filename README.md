# Dashboard Writer - Push CAN Data to InfluxDB [BETA]

This project lets you DBC decode CAN data from your CANedge into physical values - and push the data into an InfluxDB database. From here, the data can be displayed via your own customized, open source Grafana dashboard.

For the full step-by-step guide to setting up your dashboard, see the [CANedge intro](https://canlogger.csselectronics.com/canedge-getting-started/log-file-tools/browser-dashboards).

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

## Installation
We recommend to install Python 3.7 for Windows ([32 bit](https://www.python.org/ftp/python/3.7.9/python-3.7.9.exe)/[64 bit](https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe)) or [Linux](https://www.python.org/downloads/release/python-379/).

Next, intall script dependencies via the `requirements.txt`:  
  ``pip install -r requirements.txt``

---
## Deployment

### 1: Test script with sample data
1. Download this repository incl. the J1939 data and demo DBC
2. In `inputs.py` add your InfluxDB details, then run `python main.py` via the command line

*Note: If you use a free InfluxDB Cloud user, the sample data will be removed after a period (as it is >30 days old).*

### 2: Modify script with your own details
1. Local disk: Add your own data next to the scripts as per the SD structure:
   `LOG/<device_ID>/<session>/<split>.MF4`
2. S3 server: Add your S3 server details in `inputs.py` and set `s3 = True`
3. In `inputs.py` update the DBC path list and the device list to match yours
4. Optionally modify the signal filters or resampling frequency

---

## Automation 
There are multiple ways to automate the script execution. 

### 3A: Use task scheduler
One approach is via periodic execution, triggered e.g. by Windows Task Scheduler or Linux cron jobs. By default, the script is 'dynamic' meaning that it will only process log files that have not yet been added to the InfluxDB database. The script achieves this by fetching the 'most recent' timestamp (across signals) for each device in InfluxDB. The script will then only fetch log files that contain newer data vs. this timestamp. 

If no timestamps are found in InfluxDB for a device, `default_start` is used. Same goes if `dynamic = False` is used.

For details on setting up task scheduler, see the CANedge Intro guide for browser dashboards.

### 3B: Set up AWS Lambda function
Antoher approach is to use event based triggers, e.g. via AWS Lambda functions. We provide a detailed description of setting up AWS Lambda functions in the `aws_lambda_example/` sub folder.  

---
## Other practical information

### Change timestamps 
If you wish to test the script using old data, you can change the timestamps so that the data is 'rebaselined' to today, minus an offset number of days. This is useful e.g. if you want to use the InfluxDB Cloud Starter, which will delete data that is older than 30 days. To rebaseline your data to start today minus 2 days, simply add `days_offset=2` in the `DataWriter` initialization. 

### Change verbosity
By default, summary information is printed as part of the processing. You can parse `verbose=False` as an input argument in `list_log_files`, `SetupInflux` and `DataWriter` to avoid this.

### Delete data from InfluxDB
If you need to delete data in InfluxDB that you e.g. uploaded as part of a test, you can use the `delete_influx(name)` function from the `SetupInflux` class. Call it by parsing the name of the 'measurement' to delete (i.e. the device ID):

``influx.delete_influx("958D2219")``

### Multiple channels
If your log files contain data from two CAN channels, you may need to adjust the script in case you have duplicate signal names across both channels. For example, if you're extracting the signal `EngineSpeed` from both channels. 