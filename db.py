from pymongo import MongoClient

MONGO_URI = "mongodb+srv://djembrunou002:nAkAmA_002@cluster0.a60e9cy.mongodb.net/"

client = MongoClient(MONGO_URI)

db = client["mediguide"]

users = db["users"]
meds = db["medications"]
history = db["history"]
# db.py updates
resets = db["password_resets"]
