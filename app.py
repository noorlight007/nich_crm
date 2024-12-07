from flask import Flask, render_template, jsonify
from db_handler import DatabaseHandler

app = Flask(__name__)

# Initialize Database Handler
db_config = {
    "host": "localhost",
    "user": "developer_admin",
    "password": "6984125oO!",
    "db_name": "AutoParts"
}



@app.route('/')
def index():
    db_handler = DatabaseHandler(**db_config)
    total_parts = db_handler.get_total_parts()
    total_customers = db_handler.get_total_customers()
    return render_template('index.html', total_parts=total_parts, total_customers=total_customers)


@app.route('/parts')
def parts_table():
    db_handler = DatabaseHandler(**db_config)
    try:
        parts_data = db_handler.get_parts_data()
        return render_template('parts.html', parts=parts_data)
    except Exception as e:
        return f"Error: {str(e)}"
    
@app.route('/parts?checked=true')
def checked_parts_table():
    db_handler = DatabaseHandler(**db_config)
    try:
        parts_data = db_handler.get_credited_parts_data()
        return render_template('parts.html', parts=parts_data , checked = "yes")
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/customers')
def customers_table():
    db_handler = DatabaseHandler(**db_config)
    try:
        customers_data = db_handler.get_customers_data()
        return render_template('customers.html', customers=customers_data)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/users')
def users_table():
    db_handler = DatabaseHandler(**db_config)
    try:
        users_data = db_handler.get_users_data()
        return render_template('users_table.html', users=users_data)
    except Exception as e:
        return f"Error: {str(e)}"

@app.teardown_appcontext
def close_db_connection(exception=None):
    db_handler = DatabaseHandler(**db_config)
    """
    Close the database connection when the app context ends.
    """
    try:
        db_handler.close()
    except Exception as e:
        print(f"Error closing database connection: {e}")

if __name__ == '__main__':
    app.run(debug=True,host = '0.0.0.0', port= 8000)
