import paho.mqtt.client as mqtt
import json
from database import Database
import tabulate

class MQTTClient():
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with code " + str(rc))
        self.client.subscribe("aqi-info")
    
    def on_message(self, client, userdata, msg):
        print("Message topic " + str(msg.payload))
        data = json.loads(msg.payload)
        node_id = data["node"]
        aqi = data["aqi"]
        
        if aqi < 51:
            self.client.publish("led","good")
        elif 51 <= aqi <= 100:
            self.client.publish("led","moderate")
        else:
            self.client.publish("led","bad")
        timestamp = data["timestamp"]

        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `mqtt` (`node_id`,`aqi`,`timestamp`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (node_id, aqi, timestamp))
        self.connnection.commit()

        with self.connection.cursor() as new_cursor:
            new_cursor.execute("SELECT * FROM `mqtt`")
            header, rows = [x.keys() for x in new_cursor], [x.values() for x in new_cursor] 
            print(tabulate.tabulate(rows, header, tablefmt='grid'))

    def mqtt_client(self):
        self.db = Database
        self.connection = self.db.connect_db()
        print("MQTT Client Starting...")
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect("127.0.0.1", 1883, 60)
        except Exception as e:
            print(str(e))
        self.client.loop_forever()