# Main Functions:-

- `hash_password(password: str) -> str`: This funcitons takes a password as input and returns the hashed and salted version of the password

- `connectdb()` -> `mysql.connector.connect() object`, `mysql.connector.connect.cursor() object`: This function connects to the database and returns the connection object and the cursor object

- `setupdb()`: This function connects to MySQL and creates the main VIDEOSCHOOL database and the required tables with the defined schema

- `add_user(username: str, password: str, user_type: str)`: This function creates and adds a new user to the database

- `delete_user(user_id: int)`: This function sets the user status to INACTIVE in the database

- `add_channel(channel_id: str, channel_name: str, user_id: int)`: This function adds a new channel to the database (NOTE: will be updated in the future to allow for google auth token storage)

- `delete_channel(channel_id: str)`: This function sets the channel status to DELETED in the database

- `update_channel_status(channel_id: str, status: str)`: This function updates the status of the channel in the database

- `assign_user_to_channel(user_id: int, channel_id: str, user_type: str)`: This function assigns a user to the relevant role in the specified channel (E.g. Manager, Editor and Creator)

- `login_log(user_id: int, log_type: str, log_date: int)`: This function logs the login activity of the user