from utils import setup_fs, load_dbc_files, list_log_files, SetupInflux, DataWriter
import inputs

# initialize connection to InfluxDB
influx = SetupInflux(influx_url=inputs.influx_url, token=inputs.token, org_id=inputs.org_id, influx_bucket=inputs.influx_bucket)
start_times = influx.get_start_times(inputs.devices, inputs.default_start, inputs.dynamic)

# setup filesystem (local/S3), load DBC files and list log files for processing
fs = setup_fs(inputs.s3, inputs.key, inputs.secret, inputs.endpoint)
db_list = load_dbc_files(inputs.dbc_paths)
log_files = list_log_files(fs, inputs.devices, start_times)

# # process the log files and write extracted signals to InfluxDB
writer = DataWriter(fs=fs, db_list=db_list, signals=inputs.signals, res=inputs.res, db_func=influx.write_influx)
writer.decode_log_files(log_files)
