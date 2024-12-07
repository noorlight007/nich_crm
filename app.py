from flask import Flask, render_template
from db_handler import DatabaseHandler

app = Flask(__name__)

# Initialize Database Handler
db_config = {
    "host": "localhost",
    "user": "developer_admin",
    "password": "6984125oO!",
    "db_name": "AutoParts"
}
db_handler = DatabaseHandler(**db_config)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/parts')
def parts_table():
    try:
        parts_data = db_handler.get_parts_data()
        return render_template('parts.html', parts=parts_data)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/customers')
def customers_table():
    try:
        customers_data = db_handler.get_customers_data()
        return render_template('customers.html', customers=customers_data)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/users')
def users_table():
    try:
        users_data = db_handler.get_users_data()
        return render_template('users_table.html', users=users_data)
    except Exception as e:
        return f"Error: {str(e)}"

@app.teardown_appcontext
def close_db_connection(exception=None):
    """
    Close the database connection when the app context ends.
    """
    try:
        db_handler.close()
    except Exception as e:
        print(f"Error closing database connection: {e}")

if __name__ == '__main__':
    app.run(debug=True,host = '0.0.0.0', port= 8000)
