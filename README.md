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

## Requirements
To use the script, install dependencies via the `requirements.txt`:

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
4. In `last_run.txt`, specify when you wish to load log files from (e.g. `2020-01-13 00:00:00`)
5. Optionally modify the signal filters or resampling frequency

---

## Automation 
There are multiple ways to automate the script execution. 

### 3A: Enable dynamic start time
One approach is via periodic execution, triggered e.g. by Windows Task Scheduler. In this case, the 'dynamic' start time can be enabled, which will ensure the script only processes log files uploaded since the last script execution by updating the `last_run.txt` on each execution. 


1. In `inputs.py` set `dynamic = True`
2. Follow the CANedge Intro guide for setting up e.g. Windows Task Scheduler

### 3B: Set up AWS Lambda function
Antoher approach is to use event based triggers, e.g. via AWS Lambda functions. We provide a detailed description of setting up AWS Lambda functions in the `aws_lambda_example/` sub folder.  

---
## Other practical information

### Change verbosity
By default, summary information is printed as part of the processing. You can parse `verbose=False` as an input argument in `list_log_files`, `SetupInflux` and `DataWriter` to avoid this.

### Delete data from InfluxDB
If you need to delete data in InfluxDB that you e.g. uploaded as part of a test, you can use the `delete_influx(name)` function from the `SetupInflux` class. Call it by parsing the name of the 'measurement' to delete (i.e. the device ID):

``influx.delete_influx("958D2219")``

### Multiple channels
If your log files contain data from two CAN channels, you may need to adjust the script in case you have duplicate signal names across both channels. For example, if you're extracting the signal `EngineSpeed` from both channels. 

---
## Regarding cloud data transfer costs 
If your data is stored on e.g. an AWS S3 cloud server, processing the data may result in data transfer costs, e.g. if you're running the scripts on your own PC. In contrast, if the script is run on an AWS EC2 instance in the same region as your S3 bucket, there is no data transfer cost. CSS Electronics does not take responsibility for e.g. unexpected costs related to use of the API tools and we encourage you to monitor your costs during initial testing.