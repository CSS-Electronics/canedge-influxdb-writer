class SetupInflux:
    def __init__(self, influx_url, token, org_id, influx_bucket, res, debug=False, verbose=True):
        from influxdb_client import InfluxDBClient

        self.influx_url = influx_url
        self.token = token
        self.org_id = org_id
        self.influx_bucket = influx_bucket
        self.debug = debug
        self.verbose = verbose
        self.res = res
        self.client = InfluxDBClient(url=self.influx_url, token=self.token, org=self.org_id, debug=False)
        self.test = self.test_influx()
        return

    def __del__(self):
        self.client.__del__()

    def get_start_times(self, devices, default_start, dynamic):
        """Get latest InfluxDB timestamps for devices for use as 'start times' for listing log files from S3"""
        from datetime import datetime, timedelta
        from dateutil.tz import tzutc

        default_start_dt = datetime.strptime(default_start, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tzutc())
        device_ids = [device.split("/")[1] for device in devices]
        start_times = []

        if dynamic == False or self.test == 0:
            for device in device_ids:
                last_time = default_start_dt
                start_times.append(last_time)
        elif self.test != 0:
            for device in device_ids:
                influx_time = self.client.query_api().query(
                    f'from(bucket:"{self.influx_bucket}") |> range(start: -100d) |> filter(fn: (r) => r["_measurement"] == "{device}") |> group() |> last()'
                )

                if len(influx_time) == 0:
                    last_time = default_start_dt
                else:
                    last_time = influx_time[0].records[0]["_time"]
                    last_time = last_time + timedelta(seconds=2)

                start_times.append(last_time)

                if self.verbose:
                    print(f"Log files will be fetched for {device} from {last_time}")

        return start_times

    def add_signal_tags(self, df_signal):
        """Advanced: This can be used to add custom tags to the signals
        based on a specific use case logic. In effect, this will
        split the signal into multiple timeseries
        """
        tag_columns = ["tag"]

        def event_test(row):
            return "event" if row[0] > 1200 else "no event"

        for tag in tag_columns:
            df_signal[tag] = df_signal.apply(lambda row: event_test(row), axis=1)

        return tag_columns, df_signal

    def write_signals(self, device_id, df_phys):
        """Given a device ID and a dataframe of physical values,
        resample and write each signal to a time series database

        :param device_id:   ID of device (used as the 'measurement name')
        :param df_phys:     Dataframe of physical values (e.g. as per output of can_decoder)
        """
        tag_columns = []

        if df_phys.empty:
            print("Warning: Dataframe is empty, no data written")
            return
        else:
            if self.res != "":
                self.write_influx(device_id, df_phys, [])

            else:
                for signal, group in df_phys.groupby("Signal")["Physical Value"]:
                    df_signal = group.to_frame().rename(columns={"Physical Value": signal})

                    if self.res != "":
                        df_signal = df_signal.resample(self.res).ffill().dropna()

                    if self.verbose:
                        print(f"Signal: {signal} (mean: {round(df_signal[signal].mean(),2)} | records: {len(df_signal)} | resampling: {self.res})")

                    # tag_columns, df_signal = self.add_signal_tags(df_signal)

                    self.write_influx(device_id, df_signal, tag_columns)

    def write_influx(self, name, df, tag_columns):
        """Helper function to write signal dataframes to InfluxDB"""
        from influxdb_client import WriteOptions

        if self.test == 0:
            print("Please check your InfluxDB credentials")
            return

        with self.client.write_api(
                write_options=WriteOptions(
                    batch_size=20_000,
                    flush_interval=1_000,
                    jitter_interval=0,
                    retry_interval=5_000,
                )
        ) as _write_client:
            _write_client.write(self.influx_bucket, record=df, data_frame_measurement_name=name,
                                data_frame_tag_columns=tag_columns)

        if self.verbose:
            print(f"- SUCCESS: {len(df.index)} records of {name} written to InfluxDB\n\n")

        _write_client.__del__()

    def delete_influx(self, device):
        """Given a 'measurement' name (e.g. device ID), delete the related data from InfluxDB"""
        start = "1970-01-01T00:00:00Z"
        stop = "2099-01-01T00:00:00Z"

        delete_api = self.client.delete_api()
        delete_api.delete(
            start,
            stop,
            f'_measurement="{device}"',
            bucket=self.influx_bucket,
            org=self.org_id,
        )

    def test_influx(self):
        """Test the connection to your InfluxDB database"""
        if self.influx_url == "influx_endpoint":
            result = 0
        else:
            try:
                test = self.client.query_api().query(f'from(bucket:"{self.influx_bucket}") |> range(start: -10s)')
                result = 1
            except Exception as err:
                self.print_influx_error(str(err))
                result = 0

        return result

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
