
from flask import Blueprint, request, jsonify
from db import meds
from datetime import datetime
from bson import ObjectId

meds_bp = Blueprint("meds", __name__)

# ---------------- BATCH SYNC (The "Duplicate Killer") ----------------
@meds_bp.route("/prescriptions/batch", methods=["POST"])
def add_batch_prescriptions():
    data = request.json
    if not data or not isinstance(data, list):
        return jsonify({"success": False, "message": "List expected"}), 400
    
    now = datetime.utcnow().isoformat()
    try:
        for item in data:
            local_id = item.get("local_id")
            if not local_id:
                continue
            
            # Remove MongoDB's internal _id if it exists in the incoming JSON
            # This prevents errors when updating an existing record
            item.pop("_id", None)
            
            # Add timestamps
            item["updated_at"] = now
            if "created_at" not in item:
                item["created_at"] = now

            # UPSERT: If local_id exists, update it. If not, create it.
            meds.update_one(
                {"local_id": local_id},
                {"$set": item},
                upsert=True
            )
        
        return jsonify({"success": True, "message": "Batch synced successfully"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------- INDIVIDUAL ADD ----------------
@meds_bp.route("/prescriptions", methods=["POST"])
def add_prescription():
    data = request.json
    now = datetime.utcnow().isoformat()
    
    # We use update_one with upsert here too for safety
    local_id = data.get("local_id")
    
    new_med = {
        "user_id": data["user_id"],
        "local_id": local_id,
        "medication_name": data["medication_name"],
        "condition": data.get("condition"),
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date"),
        "times": data.get("times"),
        "created_at": now,
        "updated_at": now
    }
    
    if local_id:
        meds.update_one({"local_id": local_id}, {"$set": new_med}, upsert=True)
        return jsonify({"success": True, "message": "Saved/Updated", "updated_at": now}), 201
    else:
        result = meds.insert_one(new_med)
        return jsonify({"success": True, "server_id": str(result.inserted_id), "updated_at": now}), 201

# ---------------- GET ALL PRESCRIPTIONS ----------------
@meds_bp.route("/prescriptions/<user_id>", methods=["GET"])
def get_prescriptions(user_id):
    try:
        prescriptions = list(meds.find({"user_id": user_id}))
        for p in prescriptions:
            p["_id"] = str(p["_id"]) # MongoDB Object to String
        return jsonify(prescriptions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- UPDATE PRESCRIPTION ----------------
@meds_bp.route("/prescriptions/<id>", methods=["PUT"])
def update_prescription(id):
    data = request.json
    now = datetime.utcnow().isoformat()
    
    try:
        meds.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "medication_name": data.get("medication_name"),
                "condition": data.get("condition"),
                "start_date": data.get("start_date"),
                "end_date": data.get("end_date"),
                "times": data.get("times"),
                "updated_at": now
            }}
        )
        return jsonify({"success": True, "updated_at": now}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------- DELETE PRESCRIPTION ----------------
@meds_bp.route("/prescriptions/<id>", methods=["DELETE"])
def delete_prescription(id):
    try:
        # This receives a valid 24-char MongoDB ID string
        result = meds.delete_one({"_id": ObjectId(id)})
        if result.deleted_count > 0:
            return jsonify({"success": True}), 200
        return jsonify({"success": False, "message": "Not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

