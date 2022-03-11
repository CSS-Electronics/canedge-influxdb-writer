# CANedge InfluxDB Writer - Push CAN Bus Data to InfluxDB

This project lets you DBC decode CAN data from your CANedge - and push the data into an InfluxDB database. From here, the data can be displayed via your own customized, open source Grafana dashboard.

For the full step-by-step guide to setting up your dashboard, see the [CANedge intro](https://canlogger.csselectronics.com/canedge-getting-started/log-file-tools/browser-dashboards).


## Backend vs. Writer
We provide two options for integrating your CANedge data with Grafana dashboards:

The [CANedge Grafana Backend](https://github.com/CSS-Electronics/canedge-grafana-backend) app only processes data 'when needed' by an end user - and requires no database. It is ideal when you have large amounts of data - as you only process the data you need to visualize. 

In contrast, the [CANedge InfluxDB Writer](https://github.com/CSS-Electronics/canedge-influxdb-writer) integration requires that you process relevant data in advance (e.g. periodically or on-file-upload) and write the decoded data to a database (e.g. InfluxDB). It is ideal if the dashboard loading speed is critical - but with the downside that large amounts of data is processed & stored (at a cost) without being used.

----

## Features
```
- easily load MF4 log files from local disk or S3 server
- fetch data from hardcoded time period - or automate with dynamic periods
- DBC-decode data and optionally extract specific signals
- optionally resample data to specific frequency
- write the data to your own InfluxDB time series database
```
---

## Installation
We recommend to install Python 3.7 for Windows ([32 bit](https://www.python.org/ftp/python/3.7.9/python-3.7.9.exe)/[64 bit](https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe)) or [Linux](https://www.python.org/downloads/release/python-379/). Once installed, download and unzip the repository, then navigate to the folder with the `requirements.txt` file.

In your explorer path, write `cmd` and hit enter to open your command prompt.

Next, enter the below and hit enter to install script dependencies:
  
  ``pip install -r requirements.txt``
 
**Tip:** Watch [this video walkthrough](https://canlogger1000.csselectronics.com/img/dashboard-writer-get-started.mp4) of the above.


---
## Test the script

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
5. On the 1st run, the script will process data starting from `default_start` (you may want to modify this)

---

## Automation 
There are multiple ways to automate the script execution. 

### Use task scheduler
One approach is via periodic execution, triggered e.g. by Windows Task Scheduler or Linux cron jobs. By default, the script is 'dynamic' meaning that it will only process log files that have not yet been added to the InfluxDB database. The script achieves this by fetching the 'most recent' timestamp (across signals) for each device in InfluxDB. The script will then only fetch log files that contain newer data vs. this timestamp. 

If no timestamps are found in InfluxDB for a device, `default_start` is used. Same goes if `dynamic = False` is used. If the script is e.g. temporarily unable to connect to InfluxDB, no log files will be listed for processing.

For details on setting up task scheduler, see the CANedge Intro guide for browser dashboards.

### Set up AWS Lambda function
Antoher approach is to use event based triggers, e.g. via AWS Lambda functions. We provide a detailed description of setting up AWS Lambda functions in the `aws_lambda_example/` sub folder.  

---
## Other practical information

### Regarding encrypted log files
If you need to handle encrypted log files, you can provide a passwords dictionary object with similar structure as the `passwords.json` file used in the CANedge MF4 converters. The object can be provided e.g. as below (or via environmental variables):

```
pw = {"default": "password"} 			# hardcoded  
pw = json.load(open("passwords.json"))	# from local JSON file 
```

### Change timestamps 
If you wish to test the script using old data, you can change the timestamps so that the data is 'rebaselined' to today, minus an offset number of days. This is useful e.g. if you want to use the InfluxDB Cloud Starter, which will delete data that is older than 30 days. To rebaseline your data to start today minus 2 days, simply add `days_offset=2` in the `ProcessData` initialization. 

### Change verbosity
By default, summary information is printed as part of the processing. You can parse `verbose=False` as an input argument in `list_log_files`, `SetupInflux` and `ProcessData` to avoid this.

### Delete data from InfluxDB
If you need to delete data in InfluxDB that you e.g. uploaded as part of a test, you can use the `delete_influx(name)` function from the `SetupInflux` class. Call it by parsing the name of the 'measurement' to delete (i.e. the device ID):

``influx.delete_influx("958D2219")``

### Multiple channels
If your log files contain data from two CAN channels, you may need to adjust the script in case you have duplicate signal names across both channels. For example, if you're extracting the signal `EngineSpeed` from both channels. 

### Advanced processing (custom signals, transport protocol decoding, ...)
If you need to perform more advanced data processing, you may find useful functions and examples in the api-examples library under `data-processing/`.

In particular, see the guide in that repository for including transport protocol handling for UDS, J1939 or NMEA 2000 fast packets. 

---

### Add InfluxDB tags 
You can add tags to your data when using InfluxDB. This effectively adds additional dimensions to your data that you can e.g. use to color timeseries based on events or to further segment your queries when visualizing the data. The `utils_db.py` contains a basic example via the `add_signal_tags` functions that you can use as outset for building your own logic. 

---
### Regarding InfluxDB and S3 usage costs
Note that if you use the paid InfluxDB cloud and a paid S3 server, we recommend that you monitor usage during your tests early on to ensure that no unexpected cost developments occur.