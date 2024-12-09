from flask import Flask, render_template, jsonify,request,session, redirect, url_for
from flask_session import Session
from datetime import timedelta
from db_handler import DatabaseHandler

app = Flask(__name__)
app.config['secret_key'] = '5800d5d9e4405020d527f0587538abbe'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize Database Handler
db_config = {
    "host": "localhost",
    "user": "developer_admin",
    "password": "6984125oO!",
    "db_name": "AutoParts"
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        opt_code = request.form.get('opt_code')
        pin = request.form.get('pin')

        try:
            db_handler = DatabaseHandler(**db_config)
            user = db_handler.validate_user(opt_code, pin)
            if user:
                # Set session data
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('index'))  # Redirect to a dashboard or home page
            else:
                return render_template('signin.html', error="Invalid OPT Code or PIN.")
        except Exception as e:
            return f"Error: {str(e)}"
    return render_template('signin.html')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('login')
    db_handler = DatabaseHandler(**db_config)
    total_parts = db_handler.get_total_parts()
    total_customers = db_handler.get_total_customers()
    total_admins = db_handler.get_total_admins()
    return render_template('index.html', total_parts=total_parts, total_customers=total_customers, total_admins = total_admins)


@app.route('/parts')
def parts_table():
    db_handler = DatabaseHandler(**db_config)
    all_companies = db_handler.get_all_company_with_acccount_no() 
    try:
        # Check the query parameter
        checked = request.args.get('checked')
        if checked == 'true':
            parts_data = db_handler.get_credited_parts_data()
            return render_template('parts.html', parts=parts_data, checked="yes", all_companies = all_companies)
        else:
            parts_data = db_handler.get_parts_data()
            return render_template('parts.html', parts=parts_data, checked="no", all_companies = all_companies)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/customers/<state_count>')
def customers_table(state_count):
    db_handler = DatabaseHandler(**db_config)
    try:
        # Get the total number of customers
        total_customers = db_handler.get_total_customers()
        db_handler = DatabaseHandler(**db_config)
        # Check the query parameter for 'first_half' or 'last_half'
        if state_count:
            if state_count == "first_half":
                # Get the first half of the customer data
                first_half = db_handler.get_customers_data(0, total_customers // 2)
                return render_template('customers.html', customers=first_half,  state = 'first_half')

            elif state_count == "last_half":
                # Get the second half of the customer data
                last_half = db_handler.get_customers_data(total_customers // 2, total_customers)
                return render_template('customers.html', customers=last_half,  state = 'last_half')

        else:
            # Default behavior (if no 'count' parameter is passed)
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
