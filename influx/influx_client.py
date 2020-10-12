import pandas as pd
from influxdb import DataFrameClient

class InfluxClient:
    def __init__(self, database="eta"):
        self.client = DataFrameClient(host="localhost", port="8086", username="admin", password="admin", database=database)

    def get_numeric_data(self, df):
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        return df.select_dtypes(include=numerics)

    def insert_pandas(self, df): 
        numeric_df = self.get_numeric_data(df)
        self.client.write_points(numeric_df, 'raw', time_precision="s", batch_size=1000)    
    