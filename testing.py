from db_handler import DatabaseHandler

# Initialize Database Handler
db_config = {
    "host": "localhost",
    "user": "developer_admin",
    "password": "6984125oO!",
    "db_name": "AutoParts"
}

db_handler = DatabaseHandler(**db_config)
account_numbers = db_handler.get_all_account_number()

flat_list = [item[0] for item in account_numbers]
print(flat_list)