import aiofiles
from fastapi import HTTPException, BackgroundTasks
from bson.objectid import ObjectId
from ..database import database
import csv

candidate_collection = database.get_collection("candidate_collection")

def candidate_helper(candidate) -> dict:
    return {
        "id": str(candidate["_id"]),
        "fullname": candidate["fullname"],
        "email": candidate["email"],
        "address": candidate["address"],
        "education": candidate["education"],
        "phone_number": candidate["phone_number"],
        "experience_years": candidate["experience_years"],
        "skills": candidate["skills"]
    }
    
async def retrieve_candidates(page: int = 1, limit: int = 10):
    
    # Calculate the number of documents to skip based on the page number and limit
    skip = (page - 1) * limit
    # Find all candidates and apply pagination
    candidates = []
    async for candidate in candidate_collection.find().skip(skip).limit(limit):
        candidates.append(candidate_helper(candidate))
    
    return candidates


async def add_candidate(candidate_data: dict) -> dict:
    candidate_exists = await candidate_collection.find_one({"email": candidate_data["email"]})
    if candidate_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    candidate = await candidate_collection.insert_one(candidate_data)
    new_candidate = await candidate_collection.find_one({"_id": candidate.inserted_id})
    return candidate_helper(new_candidate)


# Retrieve a candidate with a matching ID
async def retrieve_candidate(id: str) -> dict:
    candidate = await candidate_collection.find_one({"_id": ObjectId(id)})
    if candidate:
        return candidate_helper(candidate)


async def update_candidate(id: str, data: dict):
    if len(data) < 1:
        return False
    candidate = await candidate_collection.find_one({"_id": ObjectId(id)})
    if candidate:
        updated_candidate = await candidate_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_candidate:
            return True
        return False


# Delete a candidate from the database
async def delete_candidate(id: str):
    candidate = await candidate_collection.find_one({"_id": ObjectId(id)})
    if candidate:
        await candidate_collection.delete_one({"_id": ObjectId(id)})
        return True

async def generate_csv_report():
    headers = ["ID", "Full Name", "Email", "Address", "Education", "Phone Number", "Experience Years", "Skills"]
    print("Generate called")

    async def fetch_and_prepare_candidates():
        candidates = []
        async for candidate in candidate_collection.find():
            candidates.append(candidate)  # Simplified for demonstration
        return candidates

    candidates = await fetch_and_prepare_candidates()

    file_path = 'report.csv'
    with open(file_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)  # Write the header row
        for candidate in candidates:
            writer.writerow([
                str(candidate.get('id', '')),
                candidate.get('fullname', ''),
                candidate.get('email', ''),
                candidate.get('address', ''),
                candidate.get('education', ''),
                candidate.get('phone_number', ''),
                str(candidate.get('experience_years', '')),
                ', '.join(candidate.get('skills', []))
            ])

    # Read the file synchronously to verify its content
    with open(file_path, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        rows = [row for row in reader]
        if len(rows) > 1:  # Check if more than just the header row exists
            print(f"File verified: {len(rows)} rows found.")
        else:
            print("File verification failed: No data found.")

    return file_path