package iot.unipi.it;

import java.util.Date;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.TimeUnit;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.SimpleDateFormat;

import org.eclipse.californium.core.CoapClient;
import org.eclipse.californium.core.CoapResponse;
import org.eclipse.californium.core.coap.MediaTypeRegistry;
import org.eclipse.paho.client.mqttv3.MqttException;


public class Interface {

    public boolean dehumidificationReq = false;
    public boolean heatingReq = false;
    public boolean hum_set = false;
    public boolean temp_set = false;
    public String dehumidification_status = null;
    public String heating_status = null;
    static CoAPServer coapServer = new CoAPServer(5683);
    static public Map<String,Resource> registeredResources = new TreeMap<String,Resource>();
    
    public static void main(String[] args) throws MqttException {

        startServer();
        
        try {
        	CombinedMqttClient MqttClient = new CombinedMqttClient();
        }catch (Error e) {
        	System.out.print(e);
        }
     

        showMenu();

    }


    private static void startServer() {
        new Thread() {
            public void run() {
                coapServer.start();
            }
        }.start();
    }

    public static void showMenu() {
        System.out.print("\nxxxxxxxxxxxxxxxxxxx AIR SENSOR MONITORING SYSTEM xxxxxxxxxxxxxxxxxxx\n"
                + "\nThis application serves to monitor and regulate humidity and temperature levels in an indoor environment.\n"
                + "It provides real-time data analysis for maintaining optimal air quality and comfort.\n"
                + "\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n\n");
    }

    
    public void MonitorHumidity() throws SQLException {
		int hum = 0;
		
		try {
			Class.forName("com.mysql.cj.jdbc.Driver");
		} catch (ClassNotFoundException e1) {
			e1.printStackTrace();
		}
		  String connectionUrl = "jdbc:mysql://localhost:3306/sensors";
		  String query = "SELECT * FROM mqtt_humidity ORDER BY time DESC LIMIT 1;";
		  try {
			  Connection conn = DriverManager.getConnection(connectionUrl,"admin","admin@374");
			  Statement st = conn.createStatement();
			  ResultSet rs = st.executeQuery(query);
			  
			  if (rs.next()) {
				  hum = rs.getInt(4);
		        }
			  
			  
			  if(hum < 20) {
				  System.out.println("Dehumidification is required.\n");
				  dehumidificationReq = true;
				  actuatorActivation("dehumidification-actuator");
				  regulateHumidity();
			  } else {System.out.println("Dehumidification is not required.\n");}
			  
			  dehumidificationReq = false;
			  hum_set = false;
			  conn.close();
			  
		  }catch(SQLException e){
			  e.printStackTrace();
		  }  
	}
    
    public void regulateHumidity() {
		
		int min = 20;
		int max = 40;
		int newhum = (int)Math.floor(Math.random()*(max-min+1)+min);
		hum_set = true;
		dehumidification_status = "ON";
		
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		Date d = new Date();
		String[] tokens = dateFormat.format(d).split(" ");
		String date = tokens[0];
		String time = tokens[1];
		  
    	System.out.println("Dehumidification actuator: " + dehumidification_status + "\n");
    	
    	storeMqttData(time, date, newhum, dehumidificationReq, "mqtt_humidity");
    	
    	try {	
			TimeUnit.SECONDS.sleep(5);
			
			System.out.println("Dehumidification Complete!");
			actuatorDeactivation("dehumidification-actuator");
			dehumidification_status = "OFF";
			System.out.println("Dehumidification actuator: " + dehumidification_status);
			
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
    	

    	System.out.println("Humidity after regulation: " + newhum + "\n");
    
    }
    
    public void MonitorTemperature() throws SQLException {
    	int temp = 0;
		
		try {
			Class.forName("com.mysql.cj.jdbc.Driver");
		} catch (ClassNotFoundException e1) {
			e1.printStackTrace();
		}
		  String connectionUrl = "jdbc:mysql://localhost:3306/sensors";
		  String query = "SELECT * FROM mqtt_temperature ORDER BY time DESC LIMIT 1;";
		  try {
			  Connection conn = DriverManager.getConnection(connectionUrl,"admin","admin@374");
			  Statement st = conn.createStatement();
			  ResultSet rs = st.executeQuery(query);
			  
			  if (rs.next()) {//get first result
				  temp = rs.getInt(4);
		        }
			  
			  
			  if(temp < 10) {
				  System.out.println("Heating is required.\n");
				  heatingReq = true;
				  actuatorActivation("heating-actuator");
				  regulateTemperature();
			  } else {System.out.println("Heating is not required.\n");}
			  
			  heatingReq = false;
			  temp_set = false;
			  conn.close();
			  
		  }catch(SQLException e){
			  e.printStackTrace();
		  }  
	}
    
    public void regulateTemperature() {
		
		int min = 10;
		int max = 20;
		int newtemp = (int)Math.floor(Math.random()*(max-min+1)+min);
		temp_set = true;
		heating_status = "ON";
		
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		Date d = new Date();
		String[] tokens = dateFormat.format(d).split(" ");
		String date = tokens[0];
		String time = tokens[1];
		  
    	System.out.println("Heating actuator: " + heating_status + "\n");
    	
    	storeMqttData(time, date, newtemp, heatingReq, "mqtt_temperature");
    	
    	try {	
			TimeUnit.SECONDS.sleep(5);
			
			System.out.println("Heating Complete!");
			actuatorDeactivation("heating-actuator");
			heating_status = "OFF";
			System.out.println("Heating actuator: " + heating_status );
			
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
    	

    	System.out.println("Temperature after regulation: " + newtemp + "\n");
    
    }
    
    public void storeMqttData(String time, String date, int value, boolean req, String tableName) {
    	String query = null;
    	
	    if (tableName == "mqtt_humidity") {
	  	  if (req && !hum_set) { dehumidification_status = "Required";
	  	  }else if (req && hum_set) { dehumidification_status = "Regulated";
	  	  }else if (!req) { dehumidification_status = "Non-Required";}
	  	  
	  	  query = "INSERT INTO "+ tableName +" (time, date, humidity, Dehumidification) VALUES ('"+time+"','"+date+"','"+value+"','"+dehumidification_status+"')";
	    
	    }
	    else if (tableName == "mqtt_temperature") {
	  	  if (req && !temp_set) { heating_status = "Required";
	  	  }else if (req && temp_set) { heating_status = "Regulated";
	  	  }else if (!req) { heating_status = "Non-Required";}
	  	  
		  query = "INSERT INTO "+ tableName +" (time, date, temperature, heating) VALUES ('"+time+"','"+date+"','"+value+"','"+heating_status+"')";
		}
	       	
		  try {
			Class.forName("com.mysql.cj.jdbc.Driver");
		  } catch (ClassNotFoundException e1) {
			e1.printStackTrace();
		  }
		  
		  String connectionUrl = "jdbc:mysql://localhost:3306/sensors";
	  	  try {
	  		  Connection conn = DriverManager.getConnection(connectionUrl,"admin","admin@374");
	  		  PreparedStatement ps = conn.prepareStatement(query);
	  		  ps.executeUpdate();
	  		  conn.close();
	  		  
	  	  }catch(SQLException e){
	  		  e.printStackTrace();
	  	  }
	  		  
	}
    
 	public void actuatorActivation(String name) {
		/* Resource discovery */

		CoapClient client = new CoapClient(registeredResources.get(name).getCoapURI());
		
		CoapResponse res = client.post("mode="+ "on", MediaTypeRegistry.TEXT_PLAIN);
		
		String code = res.getCode().toString();
		
		registeredResources.get(name).setActuatorState(true);
		
		if(!code.startsWith("2")) {	
			System.err.print("error: " + code);
			throw new Error ("Actuator Not Turned ON!!");
		}	
			    	
	}
 	
 	public void actuatorDeactivation(String name) {
		/* Resource discovery */

		CoapClient client = new CoapClient(registeredResources.get(name).getCoapURI());
		
		CoapResponse res = client.post("mode="+ "off", MediaTypeRegistry.TEXT_PLAIN);
	
		String code = res.getCode().toString();
		
		registeredResources.get(name).setActuatorState(false);
		
		if(!code.startsWith("2")) {	
			System.err.println("error: " + code);
			throw new Error ("Actuator Not Turned OFF!!");
		}		    	
	}
 	
}