from db_handler import DatabaseHandler

# Initialize Database Handler
db_config = {
    "host": "localhost",
    "user": "developer_admin",
    "password": "6984125oO!",
    "db_name": "ap_autopart"
}

db_handler = DatabaseHandler(**db_config)
account_numbers = db_handler.get_goods_salary()

print(account_numbers)