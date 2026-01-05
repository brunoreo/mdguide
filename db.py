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

# Use the Environment Variable from Render; Fallback to local for testing
MONGO_URI = os.environ.get('MONGO_URI', "mongodb://localhost:27017/mediguide")

client = MongoClient(MONGO_URI)
db = client.get_database() # This automatically picks the DB name from the URI

# Collections
users = db['users']
resets = db['resets']
meds = db['meds']
history = db['history']