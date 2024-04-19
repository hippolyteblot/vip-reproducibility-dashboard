"""
Database client module. Allows to connect to a database and execute queries such as insert, fetch...
"""
import mysql.connector


class DatabaseClient:
    """Database client class"""
    def __init__(self, host, user, password, database):
        self.connection = None
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connect()

    def connect(self):
        """Connect to the database using the given credentials"""
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            auth_plugin='mysql_native_password'
        )

    def disconnect(self):
        """Disconnect from the database"""
        self.connection.close()

    def execute(self, query, params=None):
        """Execute a query on the database and return the last inserted id"""
        self.check_connection()
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        cursor.close()
        return cursor.lastrowid

    def fetch(self, query, params=None):
        """Fetch all the results from a query on the database"""
        self.check_connection()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return result

    def fetch_one(self, query, params=None):
        """Fetch one result from a query on the database"""
        self.check_connection()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params)
        results = cursor.fetchall() # can be better to use fetchone ? but crash sometimes
        result = results[0] if results else None
        cursor.close()
        self.connection.close()
        return result

    def check_connection(self):
        """Check if the connection is still active"""
        if not self.connection.is_connected():
            self.connect()
