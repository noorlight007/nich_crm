from flask import Flask, render_template, jsonify,request,session, redirect, url_for
from flask_session import Session
from datetime import timedelta, datetime
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

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('login'))

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
    return render_template('index.html', total_parts=total_parts, total_customers=total_customers, total_admins = total_admins, admin_name = session.get('username'))


@app.route('/parts')
def parts_table():
    if 'user_id' not in session:
        return redirect('login')
    db_handler = DatabaseHandler(**db_config)
    all_companies = db_handler.get_all_company_with_acccount_no() 
    try:
        db_handler = DatabaseHandler(**db_config)
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

@app.route('/create-part', methods=['POST'])
def create_part():
    if 'user_id' not in session:
        return redirect('login')

    referrer= request.referrer

    partname = request.form.get('partname')
    credited = request.form.get('credited')
    quantity = request.form.get('quantity')
    reason = request.form.get('reason')
    acc_number = request.form.get('acc_number')
    unique_id = request.form.get('unique_id')
    db_handler = DatabaseHandler(**db_config)
    customer_id = db_handler.get_customerID_by_account_number(acc_number)
    user_id = session.get('user_id')

    print({
        "customer_id": customer_id,
        "partname": partname,
        "credited": credited,
        "quantity": quantity,
        "reason": reason,
        "unique_id": unique_id,
        "user_id": user_id,
        "created_at": datetime.now()
    })

    # Validate quantity
    if not quantity.isdigit():
        return "Quantity must be an integer.", 400

    try:
        db_handler = DatabaseHandler(**db_config)
        db_handler.create_part(
            customer_id = int(customer_id),
            partname=partname,
            credited=int(credited),
            quantity=int(quantity),
            reason=reason,
            unique_id=unique_id,
            user_id = int(user_id),
            created_at= datetime.now(),
            updated_at= datetime.now()
        )
        return redirect(referrer)  # Redirect to parts table
    except Exception as e:
        return f"Error creating part: {str(e)}", 500
    
@app.route('/validate-account-number')
def validate_account_number():
    acc_number = request.args.get('acc_number')
    if not acc_number:
        return jsonify({"success": False})

    try:
        db_handler = DatabaseHandler(**db_config)
        customer_data = db_handler.get_customer_by_account_number(acc_number)
        if customer_data:
            return jsonify({"success": True, "company": customer_data[0][2]})  # Assuming the company name is the 3rd column
        else:
            return jsonify({"success": False})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@app.route('/delete-part/<int:part_id>', methods=['DELETE'])
def delete_part(part_id):
    db_handler = DatabaseHandler(**db_config)

    try:
        # Attempt to delete the part
        if db_handler.delete_part(part_id):
            return jsonify({"status": "success", "message": "Part deleted successfully."}), 200
        else:
            return jsonify({"status": "error", "message": "Part not found."}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db_handler.close()

@app.route('/mark-part/<int:part_id>', methods=['POST'])
def mark_part(part_id):
    db_handler = DatabaseHandler(**db_config)
    credited = db_handler.get_partCredited_byID(part_id)
    #print(credited)

    try:
        db_handler = DatabaseHandler(**db_config)
        # Attempt to delete the part
        if credited:
            if credited != 1:
                db_handler.mark_part(part_id, 1)
                return jsonify({"status": "success", "message": "Part marked as Credited successfully."}), 200
            elif credited == 1:
                db_handler.mark_part(part_id, 2)
                return jsonify({"status": "success", "message": "Part marked as Not-credited successfully."}), 200
        else:
            db_handler.mark_part(part_id, 1)
            return jsonify({"status": "success", "message": "Part marked as Not-credited successfully."}), 200

    except Exception as e:
        print("we are here")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        db_handler.close()


@app.route('/customers/<state_count>')
def customers_table(state_count):
    if 'user_id' not in session:
        return redirect('login')
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
