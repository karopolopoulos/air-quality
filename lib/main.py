import time
import os
import aqi
from datetime import datetime
from sds011 import SDS011
from dotenv import load_dotenv
from Adafruit_IO import Client
# from awsiot import mqtt_connection_builder

load_dotenv()
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = '../data/air-quality.csv'
ADAFRUIT_IO_USERNAME = os.getenv('ADAFRUIT_IO_USERNAME')
ADAFRUIT_IO_KEY = os.getenv('ADAFRUIT_IO_KEY')
ADAFRUIT_PM_2_5_FEED = 'air-quality.melbourne-pm-two-five'
ADAFRUIT_PM_10_FEED = 'air-quality.melbourne-pm-ten'
ADAFRUIT_AQI_2_5_FEED = 'air-quality.melbourne-aqi-two-five'
ADAFRUIT_AQI_10_FEED = 'air-quality.melbourne-aqi-ten'

AIO = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
SENSOR = SDS011("/dev/ttyUSB0", use_query_mode=True)


def get_pm_data(n=3):
    pmt_2_5 = 0
    pmt_10 = 0

    # turn on fan
    SENSOR.sleep(sleep=False)

    # sleep for a bit while it stabilizes
    # get average air quality levels over a period of 6 seconds by default
    time.sleep(10)
    for _ in range(n):
        x = SENSOR.query()
        pmt_2_5 = pmt_2_5 + x[0]
        pmt_10 = pmt_10 + x[1]
        time.sleep(2)

    pmt_2_5 = round(pmt_2_5/n, 1)
    pmt_10 = round(pmt_10/n, 1)

    # turn fan back off
    SENSOR.sleep(sleep=True)

    return pmt_2_5, pmt_10


def convert_pm_aqi(pmt_2_5, pmt_10):
    aqi_2_5 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pmt_2_5))
    aqi_10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pmt_10))

    return aqi_2_5, aqi_10


def save_log(pmt_2_5, pmt_10, aqi_2_5, aqi_10):
    log_path = os.path.join(DIR_PATH, LOG_FILE)

    if not os.path.exists(os.path.dirname(log_path)):
        os.makedirs(os.path.dirname(log_path))
    with open(log_path, "a") as log:
        dt = datetime.now()
        log.write(f"{dt},{pmt_2_5},{aqi_2_5},{pmt_10},{aqi_10}\n")


def send_data_adafruit(pmt_2_5, pmt_10, aqi_2_5, aqi_10):
    AIO.send(ADAFRUIT_PM_2_5_FEED, str(pmt_2_5))
    AIO.send(ADAFRUIT_PM_10_FEED, str(pmt_10))
    AIO.send(ADAFRUIT_AQI_2_5_FEED, str(aqi_2_5))
    AIO.send(ADAFRUIT_AQI_10_FEED, str(aqi_10))


def main():
    print('Collecting data...')
    pmt_2_5, pmt_10 = get_pm_data()
    aqi_2_5, aqi_10 = convert_pm_aqi(pmt_2_5, pmt_10)
    print(
        f"PM2.5: {pmt_2_5}, AQI2.5: {aqi_2_5}    |    PM10: {pmt_10}, AQI10: {aqi_10}")

    print('')
    print('Saving data to logs...')
    save_log(pmt_2_5, pmt_10, aqi_2_5, aqi_10)

    print('')
    print('Sending data to AdaFruit...')
    send_data_adafruit(pmt_2_5, pmt_10, aqi_2_5, aqi_10)

    # print('')
    # print('Sending data to AWS IoT...')
    # send_data_aws_iot(pmt_2_5, pmt_10, aqi_2_5, aqi_10)

    print('Sleeping...')


while True:
    main()
    time.sleep(30)
