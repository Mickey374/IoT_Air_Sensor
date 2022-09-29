import pymysql.cursors

class Database:
    connection = None

    def __init__(self):
        print("Initializing Database...")

    def connect(self):
        if self.connection is not None:
            return self.connection
        else:
            # Connect to the database
            self.connection = pymysql.connect(host='localhost',
                                        user='user',
                                        password='admin@374',
                                        database='air_sensor_iot',
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)
            return self.connection