import time
import os
import aqi
import json
from datetime import datetime
from sds011 import SDS011
from dotenv import load_dotenv
from Adafruit_IO import Client
from awsiot import mqtt_connection_builder
from awscrt import mqtt, io

load_dotenv()
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = '../data/air_quality.csv'
IOT_CERT_FOLDER = '../certs'
IOT_ENDPOINT = os.getenv('IOT_ENDPOINT')
ADAFRUIT_IO_USERNAME = os.getenv('ADAFRUIT_IO_USERNAME')
ADAFRUIT_IO_KEY = os.getenv('ADAFRUIT_IO_KEY')
PM_2_5_TOPIC = 'air-quality.home-pm-2-5'
PM_10_TOPIC = 'air-quality.home-pm-10'
AQI_2_5_TOPIC = 'air-quality.home-aqi-2-5'
AQI_10_TOPIC = 'air-quality.home-aqi-10'

SENSOR = SDS011("/dev/SDS011", use_query_mode=True)
AIO = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
MQTT = mqtt_connection_builder.mtls_from_path(
    endpoint=IOT_ENDPOINT,
    cert_filepath=os.path.join(DIR_PATH, IOT_CERT_FOLDER, 'certificate.pem'),
    pri_key_filepath=os.path.join(
        DIR_PATH, IOT_CERT_FOLDER, 'private.key'),
    ca_filepath=os.path.join(
        DIR_PATH, IOT_CERT_FOLDER, 'ca.pem'),
    client_id='air-quality-pi',
    client_bootstrap=client_bootstrap)
MQTT.connect()


def get_pm_data(n=10):
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
    AIO.send(PM_2_5_TOPIC, str(pmt_2_5))
    AIO.send(PM_10_TOPIC, str(pmt_10))
    AIO.send(AQI_2_5_TOPIC, str(aqi_2_5))
    AIO.send(AQI_10_TOPIC, str(aqi_10))


def send_data_aws_iot(pmt_2_5, pmt_10, aqi_2_5, aqi_10):
    MQTT.publish(topic=PM_2_5_TOPIC, payload=json.dumps(
        {"aqi": int(pmt_2_5)}), qos=mqtt.QoS.AT_LEAST_ONCE)
    MQTT.publish(topic=PM_10_TOPIC, payload=json.dumps(
        {"aqi": int(pmt_10)}), qos=mqtt.QoS.AT_LEAST_ONCE)
    MQTT.publish(topic=AQI_2_5_TOPIC, payload=json.dumps(
        {"aqi": int(aqi_2_5)}), qos=mqtt.QoS.AT_LEAST_ONCE)
    MQTT.publish(topic=AQI_10_TOPIC, payload=json.dumps(
        {"aqi": int(aqi_10)}), qos=mqtt.QoS.AT_LEAST_ONCE)


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
    try:
        send_data_adafruit(pmt_2_5, pmt_10, aqi_2_5, aqi_10)
    except:
        print('Unable to connect to AdaFruit...')

    print('Sending data to AWS IoT...')
    try:
        send_data_aws_iot(pmt_2_5, pmt_10, aqi_2_5, aqi_10)
    except:
        print('Unable to connect to AWS IoT...')

    print('')
    print('Sleeping...')
    print('')


while True:
    try:
        main()
    except:
        print('Sensor failed to return data')
        SENSOR = SDS011("/dev/SDS011", use_query_mode=True)
    time.sleep(30)
