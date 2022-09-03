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
                                        user='root',
                                        password='',
                                        database='airsensor',
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)
            return self.connection