import os
import sqlite3

# Ensure the folder exists
if not os.path.exists("data"):
    os.makedirs("data")

# Connect to SQLite database
conn = sqlite3.connect("data/user_logs.db", check_same_thread=False)
c = conn.cursor()
