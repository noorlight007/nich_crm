import MySQLdb

class DatabaseHandler:
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.connection = None

    def connect(self):
        try:
            self.connection = MySQLdb.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                db=self.db_name
            )
        except MySQLdb.MySQLError as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def get_parts_data(self):
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = """
                SELECT 
                    p.partname, 
                    p.quantity, 
                    p.reason, 
                    c.accountNumber, 
                    c.company, 
                    p.unique_id, 
                    u.name AS added_by, 
                    p.credited
                FROM 
                    parts p
                JOIN 
                    users u ON p.user_id = u.id
                JOIN 
                    customers c ON p.customer_id = c.id
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
        try:
            if not self.connection:
                self.connect()

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
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = """
                SELECT id, name, optCode, pin, email, email_verified_at, created_at, updated_at
                FROM users
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
        if self.connection:
            self.connection.close()
