package iot.unipi.it;

import java.text.SimpleDateFormat;
import java.util.Date;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.eclipse.paho.client.mqttv3.*;


public class CombinedMqttClient implements MqttCallback{
	
	String subscriber_topic = "humidity_temperature";
	String broker = "tcp://127.0.0.1:1883";
	String clientId = "Application";
	Interface i = new Interface();
	
	MqttClient mqttClient;
	
	public CombinedMqttClient() throws MqttException{
		
		mqttClient = new MqttClient(broker,clientId);
		mqttClient.setCallback(this);
		mqttClient.connect();
		mqttClient.subscribe(subscriber_topic);
		
		System.out.println("Subscribing to the " +subscriber_topic+ " topic..\n");
		
	}
	
	public void connectionLost(Throwable cause) {
  		System.out.println(cause.getMessage());
	}

	public void messageArrived(String topic, MqttMessage message) throws Exception {
		
		String json_message = new String(message.getPayload());

		// Parse JSON message
		JSONParser parser = new JSONParser();
		JSONObject jsonObject = (JSONObject) parser.parse(json_message);
		
		if(jsonObject.containsKey("HUM")) {
			Object humidityObject = jsonObject.get("HUM");
			if (humidityObject instanceof Long) {
                long humidityValue = (Long) humidityObject;
                int humidity = (int) humidityValue;
                System.out.println("Humidity observed is: " + humidity);

                if (humidity < 20) {
                    i.dehumidificationReq = true;
                } else {
                    i.dehumidificationReq = false;
                }
                
                // Get current date and time
                SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
                Date date = new Date();
                String[] tokens = dateFormat.format(date).split(" ");
                String dateStr = tokens[0];
                String timeStr = tokens[1];
                
                // Store humidity data in the database
                i.storeMqttData(timeStr, dateStr, humidity, i.dehumidificationReq, "mqtt_humidity");
                i.MonitorHumidity();
            }
		}
		
		if(jsonObject.containsKey("TEMP")) {
			Object temperatureObject = jsonObject.get("TEMP");
			if (temperatureObject instanceof Long) {
				long tempValue = (Long) temperatureObject;
	            int temperature = (int) tempValue;
	            System.out.println("Temperature observed is: " + temperature);
				
	            if (temperature < 10) {
    				i.heatingReq = true;
    			} else i.heatingReq = false;
                
                SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
                Date d = new Date();
                String[] tokens = dateFormat.format(d).split(" ");
                String date = tokens[0];
                String time = tokens[1];
                
                i.storeMqttData(time, date, temperature, i.heatingReq, "mqtt_temperature");
    			i.MonitorTemperature();
			}

		}
	}

	public void deliveryComplete(IMqttDeliveryToken token) {
		if(token != null && token.isComplete()) {
			System.out.println("Message Delivery Complete");
		}else {
			System.out.println("Message Delivery Failed");
		}
	}
}
