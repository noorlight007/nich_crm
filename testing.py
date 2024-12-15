from db_handler import DatabaseHandler

# Initialize Database Handler
db_config = {
    "host": "localhost",
    "user": "developer_admin",
    "password": "6984125oO!",
    "db_name": "AutoParts"
}

db_handler = DatabaseHandler(**db_config)
account_numbers = db_handler.get_credit_status_counts_for_today()

print(account_numbers)