def setup_fs(s3, key, secret, endpoint, cert=""):
    """Given a boolean specifying whether to use local disk or S3, setup filesystem
    """

    if s3:
        import s3fs

        fs = s3fs.S3FileSystem(
            key=key,
            secret=secret,
            client_kwargs={
                "endpoint_url": endpoint,
                # "verify": cert, # uncomment this when using MinIO with TLS enabled
            },
        )

    else:
        from pathlib import Path
        import canedge_browser

        base_path = Path(__file__).parent
        fs = canedge_browser.LocalFileSystem(base_path=base_path)

    return fs


# -----------------------------------------------
def load_dbc_files(dbc_paths):
    """Given a list of DBC file paths, create a list of conversion rule databases
    """
    import can_decoder
    from pathlib import Path

    db_list = []
    for dbc in dbc_paths:
        db = can_decoder.load_dbc(Path(__file__).parent / dbc)
        db_list.append(db)

    return db_list


# -----------------------------------------------
def list_log_files(fs, devices, dynamic, verbose=True):
    """Given a list of device paths, list log files from specified filesystem.
    Data is loaded based on start datetime found via the load_last_run function.
    If dynamic is used, the start time is updated for the next script execution
    """
    import canedge_browser

    start = load_last_run(verbose)

    if dynamic:
        set_last_run(verbose)

    log_files = canedge_browser.get_log_files(fs, devices, start_date=start)

    if verbose:
        print(f"Found {len(log_files)} log files\n")

    return log_files


def load_last_run(verbose=True):
    """Helper function for loading the date of last run (if not found, set to 7 days ago)
    """
    from datetime import datetime, timedelta, timezone
    from pathlib import Path

    # get the root folder path and specify path to the file with datetime
    f_path = Path(__file__).parent / "last_run.txt"

    fmt = "%Y-%m-%d %H:%M:%S"

    try:
        with open(f_path, mode="r") as file:
            file_data = file.read()
    except:
        print(f"Warning: Unable to load file from {f_path}")

    try:
        last_run = datetime.strptime(file_data.replace("\n", ""), fmt)
        if verbose:
            print(f"{f_path} found - loading data from {last_run}")
    except:
        last_run = datetime.utcnow() - timedelta(days=7)
        print(f"{f_path} is invalid - loading data from {last_run} (7 days ago)")

    return last_run.replace(tzinfo=timezone.utc)


def set_last_run(verbose=True):
    """Helper function for writing the last run date & time to local file
    """
    from datetime import datetime, timedelta, timezone
    from pathlib import Path

    # get the root folder path and specify path to the file with datetime
    f_path = Path(__file__).parent / "last_run.txt"

    fmt = "%Y-%m-%d %H:%M:%S"
    with open(f_path, mode="w") as file:
        file.write(datetime.utcnow().strftime(fmt))


# -----------------------------------------------
class SetupInflux:
    def __init__(self, influx_url, token, org_id, influx_bucket, debug=False, verbose=True):
        self.influx_url = influx_url
        self.token = token
        self.org_id = org_id
        self.influx_bucket = influx_bucket
        self.debug = debug
        self.verbose = verbose
        return

    def write_influx(self, name, df):
        """Helper function to write data to InfluxDB
        """
        from influxdb_client import InfluxDBClient, WriteOptions

        if self.influx_url == "influx_endpoint":
            print("- WARNING: Please add your InfluxDB credentials\n")
            return

        client = InfluxDBClient(url=self.influx_url, token=self.token, org=self.org_id, debug=False)

        try:
            test = client.query_api().query(f'from(bucket:"{self.influx_bucket}") |> range(start: -10s)')
        except Exception as err:
            self.print_influx_error(str(err))
            return

        _write_client = client.write_api(
            write_options=WriteOptions(batch_size=5000, flush_interval=1_000, jitter_interval=2_000, retry_interval=5_000,)
        )

        _write_client.write(
            self.influx_bucket, record=df, data_frame_measurement_name=name,
        )

        if self.verbose:
            print(f"- SUCCESS: {len(df.index)} records of {name} written to InfluxDB\n\n")

        _write_client.__del__()
        client.__del__()

    def delete_influx(self, name):
        """Given a 'measurement' name (e.g. device ID), delete the related data from InfluxDB
        """
        from influxdb_client import InfluxDBClient

        client = InfluxDBClient(url=self.influx_url, token=self.token, org=self.org_id, debug=False)

        start = "1970-01-01T00:00:00Z"
        stop = "2099-01-01T00:00:00Z"

        delete_api = client.delete_api()
        delete_api.delete(
            start, stop, f'_measurement="{name}"', bucket=self.influx_bucket, org=self.org_id,
        )

    def print_influx_error(self, err):
        warning = "- WARNING: Unable to write data to InfluxDB |"

        if "CERTIFICATE_VERIFY_FAILED" in err:
            print(f"{warning} check your influx_url ({self.influx_url})")
        elif "organization name" in err:
            print(f"{warning} check your org_id ({self.org_id})")
        elif "unauthorized access" in err:
            print(f"{warning} check your influx_url and token")
        elif "could not find bucket" in err:
            print(f"{warning} check your influx_bucket ({self.influx_bucket})")
        else:
            print(err)


# -----------------------------------------------
class DataWriter:
    def __init__(self, fs, db_list, signals, res, db_func, days_offset=None, verbose=True):

        self.db_list = db_list
        self.signals = signals
        self.res = res
        self.fs = fs
        self.db_func = db_func
        self.days_offset = days_offset
        self.verbose = verbose
        return

    def decode_log_files(self, log_files):
        """Given a list of log files, load the raw data from the fs filesystem
        (e.g. local or S3) and convert it using a list of conversion rule databases.

        :param log_files:   list of log file paths (e.g. as per output of canedge_browser)
        """
        import mdf_iter, can_decoder

        for db in self.db_list:
            for log_file in log_files:
                with self.fs.open(log_file, "rb") as handle:
                    mdf_file = mdf_iter.MdfFile(handle)
                    device_id = self.get_device_id(mdf_file)
                    df_raw = mdf_file.get_data_frame()

                df_decoder = can_decoder.DataFrameDecoder(db)
                df_phys = df_decoder.decode_frame(df_raw)

                if df_phys.empty:
                    print("No signals were extracted")
                else:
                    # optionally re-baseline data timestamps to 'now - days_offset'
                    if type(self.days_offset) == int:
                        from datetime import datetime, timezone
                        import pandas as pd

                        delta_days = (datetime.now(timezone.utc) - df_phys.index.min()).days - self.days_offset
                        df_phys.index = df_phys.index + pd.Timedelta(delta_days, "day")

                    self.print_log_summary(device_id, log_file, df_phys)
                    self.write_signals(device_id, df_phys)

    def write_signals(self, device_id, df_phys):
        """Given a device ID and a dataframe of physical values, optionally
        filter, resample and write each signal to a time series database

        :param device_id:   ID of device (used as the 'measurement name')
        :param df_phys:     Dataframe of physical values (e.g. as per output of can_decoder)
        """

        for signal, group in df_phys.groupby("Signal")["Physical Value"]:
            if signal in self.signals or len(self.signals) == 0:
                df_signal = group.to_frame().rename(columns={"Physical Value": signal})

                if self.res != "":
                    cnt = len(df_signal)
                    df_signal = df_signal.resample(self.res).pad().dropna()

                self.print_signal_summary(signal, df_signal, cnt)
                self.db_func(device_id, df_signal)

    def print_log_summary(self, device_id, log_file, df_phys):
        """Print summary information for each log file
        """
        if self.verbose:
            print(
                "\n---------------",
                f"\nDevice: {device_id} | Log file: {log_file.split(device_id)[-1]} [Extracted {len(df_phys)} decoded frames]\nPeriod: {df_phys.index.min()} - {df_phys.index.max()}\n",
            )

    def print_signal_summary(self, signal, df_signal, cnt):
        """Print summary information for each signal
        """
        if self.verbose:
            print(f"Signal: {signal} (mean: {round(df_signal[signal].mean(),2)})")
            if self.res != "":
                print(f"- Resampling to {self.res} ({cnt} --> {len(df_signal)} records)")

    def get_device_id(self, mdf_file):
        """Extract device ID (serial number) from MDF4 log file
        """
        return mdf_file.get_metadata()["HDComment.Device Information.serial number"]["value_raw"]
