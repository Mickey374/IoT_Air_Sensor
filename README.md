# Air House Sensor Project

Air House Sensor Project is an IoT initiative developed for monitoring temperature and humidity levels within a household environment. This project is made for the course of "Internet of Things"  at the University of Pisa(Artificial Intelligence and Data Engineering). It is primarily implemented using Java for the collector built into a jar file and C languages which incorporates various technologies such as MQTT & CoAP.

To get started with the project, follow the steps below:

## Cloning the Project

Make sure to clone the project into the "/contiki-ng/examples" directory.

## MySQL Setup

- Create a user "admin" with the password "admin@374" to access the MySQL database.
- Set up the necessary database and tables for sensor data storage.

### Database Setup

Create a MySQL database named "sensors" for storing temperature and humidity data from sensors installed within the house.

#### Table: mqtt_temperature
This table records temperature data in the house.
Columns:
- id (int, auto_increment, primary key) 🆔
- time (varchar) ⏰
- date (varchar) 📅
- temperature (int) 🌡️
- heating (varchar) 🔥

#### Table: mqtt_humidity
This table records humidity data in the house.
Columns:
- id (int, auto_increment, primary key) 🆔
- time (varchar) ⏰
- date (varchar) 📅
- humidity (int) 💧
- irrigation (varchar) 💦

## Getting Started

Follow the project slides for detailed explanation on projecy scope.

For future improvement, feel free to contribute to this project by submitting bug fixes, enhancements, or additional functionalities via pull requests(PR) since this project was tested in 2024 January.

Your contributions are valuable in enhancing the capabilities and reliability of the House Sensor Project!

       /\
      /  \
     /    \
    /______\
   |   __   |
   |  |__|  |
   |        |
   |________|
   |  __  __|
   | |__||__|
   |________|
   |   ||   |
   |___||___|

