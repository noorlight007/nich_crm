from db_handler import DatabaseHandler

# Initialize Database Handler
db_config = {
    "host": "localhost",
    "user": "developer_admin",
    "password": "6984125oO!",
    "db_name": "AutoParts"
}

db_handler = DatabaseHandler(**db_config)
account_numbers = db_handler.get_top_companies_by_quantity_this_month()

print(account_numbers)