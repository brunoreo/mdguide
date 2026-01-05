
from flask import Blueprint, request, jsonify
from db import history
from bson import ObjectId

history_bp = Blueprint("history", __name__)

# ---------------- BATCH ADD HISTORY (The "Duplicate Killer") ----------------
@history_bp.route("/history/batch", methods=["POST"])
def add_batch_history():
    data = request.json
    if not data or not isinstance(data, list):
        return jsonify({"success": False, "message": "List expected"}), 400
    
    try:
        for item in data:
            local_id = item.get("local_id")
            if not local_id:
                continue
            
            # Remove MongoDB internal ID if it exists in the payload
            item.pop("_id", None)
            
            # Use UPSERT: Match by local_id. 
            # If found, update. If not found, create.
            history.update_one(
                {"local_id": local_id},
                {"$set": item},
                upsert=True
            )
            
        return jsonify({"success": True, "message": "History logs reconciled"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------- INDIVIDUAL ADD ----------------
@history_bp.route("/history/add", methods=["POST"])
def add_history():
    data = request.json
    local_id = data.get("local_id")
    
    new_entry = {
        "user_id": data.get("user_id"),
        "local_id": local_id,
        "medication_name": data.get("medication_name"),
        "condition": data.get("condition", "N/A"),
        "date": data.get("date"),
        "time": data.get("time"),
        "synced_at": ObjectId().generation_time.isoformat()
    }

    try:
        if local_id:
            history.update_one({"local_id": local_id}, {"$set": new_entry}, upsert=True)
            return jsonify({"success": True, "message": "History updated/saved"}), 201
        else:
            result = history.insert_one(new_entry)
            return jsonify({"success": True, "server_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------- GET ALL HISTORY ----------------
@history_bp.route("/history/<user_id>", methods=["GET"])
def get_history(user_id):
    try:
        # Sort by date descending so newest logs appear first
        records = list(history.find({"user_id": user_id}).sort("date", -1))
        for r in records:
            r["_id"] = str(r["_id"])
        return jsonify(records), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------- DELETE ALL HISTORY (FOREVER) ----------------
@history_bp.route("/history/all/<user_id>", methods=["DELETE"])
def delete_all_history(user_id):
    try:
        result = history.delete_many({"user_id": user_id})
        return jsonify({
            "success": True, 
            "message": f"Successfully deleted {result.deleted_count} records from cloud."
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500