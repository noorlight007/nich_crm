import MySQLdb

class DatabaseHandler:
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.connection = None

    def connect(self):
        """
        Establish a connection to the MySQL database. Reconnect if a connection already exists but is not valid.
        """
        try:
            if self.connection and self.connection.open:
                print("Connection is already active.")
                return
            self.connection = MySQLdb.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.db_name
            )
            print("Database connection established.")
        except MySQLdb.MySQLError as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def ensure_connection(self):
        """
        Ensure the connection is active, reconnect if necessary.
        """
        try:
            if not self.connection or not self.connection.open:
                self.connect()
            else:
                self.connection.ping(reconnect=True)
        except MySQLdb.MySQLError as e:
            print(f"Error ensuring connection: {e}")
            raise

    def get_parts_data(self):
        """
        Fetch parts data with related user and customer information, ordered by `updated_at` descending.
        """
        try:
            self.ensure_connection()
            cursor = self.connection.cursor()
            query = """
                SELECT 
                    p.id,
                    p.partname, 
                    p.quantity, 
                    p.reason, 
                    c.accountNumber, 
                    c.company, 
                    p.unique_id, 
                    u.name AS added_by, 
                    p.credited, 
                    p.updated_at
                FROM 
                    parts p
                JOIN 
                    users u ON p.user_id = u.id
                JOIN 
                    customers c ON p.customer_id = c.id
                ORDER BY 
                    p.updated_at DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def get_customers_data(self):
        """
        Fetch all customer data from the 'customers' table.
        """
        try:
            self.ensure_connection()
            cursor = self.connection.cursor()
            query = """
                SELECT id, accountNumber, username, company, created_at, updated_at
                FROM customers
            """
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def get_users_data(self):
        """
        Fetch all user data from the 'users' table.
        """
        try:
            self.ensure_connection()
            cursor = self.connection.cursor()
            query = """
                SELECT id, name, optCode, pin, email, email_verified_at, created_at, updated_at
            """
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def close(self):
        """
        Close the database connection safely.
        """
        if self.connection and self.connection.open:
            try:
                self.connection.close()
                print("Database connection closed.")
            except MySQLdb.MySQLError as e:
                print(f"Error closing connection: {e}")
        else:
            print("No active database connection to close.")
