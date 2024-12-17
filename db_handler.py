import MySQLdb
from datetime import datetime, timedelta

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

    
    def get_parts_data(self, per_page, offset):
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
                    p.created_at, 
                    p.updated_at
                FROM 
                    parts p
                JOIN 
                    users u ON p.user_id = u.id
                JOIN 
                    customers c ON p.customer_id = c.id
                ORDER BY 
                    p.updated_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (per_page, offset))
            results = cursor.fetchall()

            # Get total number of rows for pagination
            cursor.execute("SELECT COUNT(*) AS total FROM parts")
            total_parts = cursor.fetchone()["total"]
            return results , total_parts
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def get_credit_status_counts_for_today(self):
        """
        Get the count of credited and not-credited items for today.
        If `credited` is 1, the item is credited. Otherwise, it is not-credited.
        """
        try:
            self.ensure_connection()
            cursor = self.connection.cursor()
            # Calculate today's date range: 00:00:00 to 23:59:59
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1) - timedelta(seconds=1)
            print(f"{today_start} - {today_end}")
            query = """
                SELECT 
                    SUM(CASE WHEN credited = 1 THEN 1 ELSE 0 END) AS credited_count,
                    SUM(CASE WHEN credited != 1 THEN 1 ELSE 0 END) AS not_credited_count
                FROM 
                    parts
                WHERE 
                    created_at BETWEEN %s AND %s
            """
            cursor.execute(query, (today_start, today_end))
            result = cursor.fetchone()
            return {
                "credited": result[0] or 0,
                "not_credited": result[1] or 0
            }
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def get_credited_parts_data(self):
        """
        Fetch credited parts data from the database where `credited` is 1.
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
                    p.created_at,
                    p.updated_at
                FROM 
                    parts p
                JOIN 
                    users u ON p.user_id = u.id
                JOIN 
                    customers c ON p.customer_id = c.id
                WHERE 
                    p.credited = 1
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

    def get_customers_data(self, start=None, end=None):
        """
        Fetch customer data with optional start and end to slice the result set.
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

            # If start and end are provided, slice the results
            if start is not None and end is not None:
                results = results[start:end]

            return results
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def get_all_company_with_acccount_no(self):
        """
        Fetch customer data with optional start and end to slice the result set.
        """
        try:
            self.ensure_connection()
            cursor = self.connection.cursor()
            query = """
                SELECT accountNumber, company
                FROM customers ORDER BY company
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

    def get_total_parts(self):
        """
        Get the total number of parts in the 'parts' table.
        """
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) FROM parts"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    


    def get_total_customers(self):
        """
        Get the total number of customers in the 'customers' table.
        """
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) FROM customers"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def get_total_admins(self):
        """
        Get the total number of admins in the 'users' table.
        """
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = "SELECT COUNT(*) FROM users"
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def validate_user(self, opt_code, pin):
        """
        Validate user credentials against the users table.
        """
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = """
                SELECT id, name 
                FROM users 
                WHERE optCode = %s AND pin = %s
            """
            cursor.execute(query, (opt_code, pin))
            result = cursor.fetchone()
            return result  # Returns the user record if found, else None
        except MySQLdb.MySQLError as e:
            print(f"Error validating user: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def get_user_data(self, admin_id):
        """
        Validate user credentials against the users table.
        """
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = """
                SELECT * 
                FROM users 
                WHERE id = %s
            """
            cursor.execute(query, (admin_id,))
            result = cursor.fetchone()
            return result  # Returns the user record if found, else None
        except MySQLdb.MySQLError as e:
            print(f"Error validating user: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def get_customer_by_account_number(self, acc_number):
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = "SELECT id, accountNumber, company FROM customers WHERE accountNumber = %s"
            cursor.execute(query, (acc_number,))
            result = cursor.fetchall()
            return result
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def get_customerID_by_account_number(self, acc_number):
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = "SELECT id FROM customers WHERE accountNumber = %s"
            cursor.execute(query, (acc_number,))
            result = cursor.fetchone()  # Use fetchone() for a single row
            return result[0] if result else None  # Return the id or None if no result
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def get_all_account_number(self):
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = "SELECT accountNumber FROM customers"
            cursor.execute(query)
            result = cursor.fetchall()
            flat_list = [item[0] for item in result]
            return flat_list
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def create_part(self, customer_id, partname, credited, quantity, reason, unique_id, user_id, created_at, updated_at):
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = """
                INSERT INTO parts (customer_id, partname, credited, quantity, reason, unique_id, user_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (customer_id, partname, credited, quantity, reason, unique_id,  user_id, created_at, updated_at))
            self.connection.commit()
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def create_customer(self, accountNumber, username, company):
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = """
                INSERT INTO customers (accountNumber, username, company, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (accountNumber, username, company, datetime.now(), datetime.now()))
            self.connection.commit()
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def delete_part(self, part_id):
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = "DELETE FROM parts WHERE id = %s"
            cursor.execute(query, (part_id,))
            self.connection.commit()

            if cursor.rowcount > 0:
                return True  # Successfully deleted
            else:
                return False  # No rows deleted (ID not found)
        except MySQLdb.MySQLError as e:
            print(f"Error executing delete query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def delete_customer(self, customer_id):
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = "DELETE FROM customers WHERE id = %s"
            cursor.execute(query, (customer_id,))
            self.connection.commit()

            if cursor.rowcount > 0:
                return True  # Successfully deleted
            else:
                return False  # No rows deleted (ID not found)
        except MySQLdb.MySQLError as e:
            print(f"Error executing delete query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def get_partCredited_byID(self, partID):
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = "SELECT credited FROM parts WHERE id = %s"
            cursor.execute(query, (partID,))
            result = cursor.fetchone()  # Use fetchone() for a single row
            print(result[0])
            return result[0] if result else None  # Return the id or None if no result
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    def mark_part(self, part_id, value_credited):
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            query = "Update parts set credited = %s where id= %s"
            cursor.execute(query, (value_credited, part_id,))
            self.connection.commit()

            if cursor.rowcount > 0:
                return True  # Successfully deleted
            else:
                return False  # No rows deleted (ID not found)
        except MySQLdb.MySQLError as e:
            print(f"Error executing delete query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def update_part(self, part_id, part_name, credited, quantity, reason, unique_id, customer_id):
        """
        Update part details in the database.
        """
        try:
            self.ensure_connection()
            cursor = self.connection.cursor()

            # Update query
            query = """
                UPDATE parts
                SET 
                    partname = %s,
                    credited = %s,
                    quantity = %s,
                    reason = %s,
                    unique_id = %s,
                    customer_id = %s,
                    updated_at = NOW()
                WHERE 
                    id = %s
            """
            cursor.execute(query, (part_name, credited, quantity, reason, unique_id, customer_id, part_id))
            self.connection.commit()

            # Return success status
            return cursor.rowcount > 0
        except self.MySQLdb.MySQLError as e:
            print(f"Error updating part: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def update_customer(self, customer_id, accountNumber, username, company):
        """
        Update customer details in the database.
        """
        try:
            self.ensure_connection()
            cursor = self.connection.cursor()

            # Update query
            query = """
                UPDATE customers
                SET 
                    accountNumber = %s,
                    username = %s,
                    company = %s,
                    updated_at = NOW()
                WHERE 
                    id = %s
            """
            cursor.execute(query, (accountNumber, username, company, customer_id))
            self.connection.commit()

            # Return success status
            return cursor.rowcount > 0
        except self.MySQLdb.MySQLError as e:
            print(f"Error updating part: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def get_top_companies_by_quantity_this_month(self):
        """
        Get the top 5 companies with the highest total quantity of parts for the current month.
        """
        try:
            self.ensure_connection()
            cursor = self.connection.cursor()
            # Calculate the start and end of the current month
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = month_start + timedelta(days=32)
            month_end = next_month.replace(day=1) - timedelta(seconds=1)

            query = """
                SELECT 
                    c.company, 
                    SUM(p.quantity) AS total_quantity
                FROM 
                    parts p
                JOIN 
                    customers c ON p.customer_id = c.id
                WHERE 
                    p.created_at BETWEEN %s AND %s
                GROUP BY 
                    c.company
                ORDER BY 
                    total_quantity DESC
                LIMIT 5
            """
            cursor.execute(query, (month_start, month_end))
            results = cursor.fetchall()
            # Convert Decimal to int
            return [{"company": row[0], "total_quantity": int(row[1])} for row in results]
        except MySQLdb.MySQLError as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()


    # ap_autopart database
    def get_goods_salary(self):
        """
        Get the top 5 companies with the highest total quantity of parts for the current month.
        """
        try:
            self.ensure_connection()
            cursor = self.connection.cursor()
            # Calculate the start and end of the current month
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = month_start + timedelta(days=32)
            month_end = next_month.replace(day=1) - timedelta(seconds=1)

            query = """
                SELECT 
                    SUM(Goods) AS total_profit
                FROM 
                    iHeads
                WHERE 
                    Prefix  = 'C' AND DateTime BETWEEN %s AND %s      
            """
            cursor.execute(query, (month_start, month_end))
            result = cursor.fetchone()
            return result[0] if result else 0
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
