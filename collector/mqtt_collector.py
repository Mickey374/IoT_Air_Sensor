import paho.mqtt.client as mqtt
import json
from database import Database
import tabulate
from datetime import datetime

# Define Variables
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60
MQTT_TOPIC = "info"
MQTT_MSG = "hello MQTT"

class MqttClient:
    def on_connect(self, client, mosq, obj, rc):
        self.client.subscribe(MQTT_TOPIC, 0)
    
    def on_message(self, client, userdata, msg):
        print("Payload: " + str(msg.payload))
        print("QOS: " + str(msg.qos))
        print("Topic: " + str(msg.topic))

        receivedData = json.loads(msg.payload)
        temperature = receivedData["temp"]
        humidity = receivedData["humidity"]
        light = receivedData["light"]
        gas = receivedData["gas"]

        if receivedData["light"] == 0:
            light = "INTENSE"
        elif receivedData["light"] == 1:
            light = "NORMAL"
        else:
            light = "DIM"
        
        dt = datetime.now()
        curr_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `mqttsensors`  (`temperature`, `humidity`, `light`, `gas`, `timestamp`) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (temperature, humidity, light, gas, curr_dt))
        
        self.connection.commit()
    
        with self.connection.cursor() as new_cursor:
            sql = "SELECT * FROM `mqttsensors`"
            new_cursor.execute(sql)
            results = new_cursor.fetchall()
            header = results[0].keys() if len(results) > 0 else []  
            rows = [x.values() for x in results]
            print(tabulate.tabulate(rows, header, tablefmt='grid'))

    def mqtt_client(self):
        self.db = Database()
        self.connection = self.db.connect_db()
        print("Mqtt client starting")
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
            print("Connected\n")
        except Exception as e:
            print(str(e))
        self.client.loop_forever()