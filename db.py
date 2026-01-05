# from pymongo import MongoClient

# MONGO_URI ="mongodb+srv://djembrunou002:nAkAmA_002@cluster0.a60e9cy.mongodb.net/"

# client = MongoClient(MONGO_URI)

# db = client["mediguide"]

# users = db["users"]
# meds = db["medications"]
# history = db["history"]
# # db.py updates
# resets = db["password_resets"]

import os
from pymongo import MongoClient

# 1. Get the URI from Render's Environment Variables
MONGO_URI = os.environ.get('MONGO_URI', "mongodb://localhost:27017/mediguide")

client = MongoClient(MONGO_URI)

# 2. Explicitly define the database name
# This ensures it works even if the URI doesn't end with /database_name
DB_NAME = "mediguide_db"
db = client[DB_NAME]

# Collections
users = db['users']
resets = db['resets']
meds = db['meds']
history = db['history']