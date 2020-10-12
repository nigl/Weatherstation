from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD
import pytz
import pandas as pd
from influx.influx_client import InfluxClient
import datetime 
BOARD.setup()

TIME_KEY = "0__time"

class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            sleep(.5)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()
            

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True) 
        self.save_to_influx(bytes(payload).decode("utf-8",'ignore'))
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT) 
    
    def save_to_influx(self, wind):
        current_time = datetime.datetime.utcnow()
        try:
            wind = float(wind.replace('\x00',''))
        except ValueError:
            print("Not a float")
        cleaned_dict = {"wind":wind}
        df = pd.DataFrame(cleaned_dict, index=[current_time])
        df = df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
        client = InfluxClient("lora")
        client.insert_pandas(df)

lora = LoRaRcvCont(verbose=False)
lora.set_mode(MODE.STDBY)

#  Medium Range  Defaults after init are 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on 13 dBm

lora.set_pa_config(pa_select=1)

try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
