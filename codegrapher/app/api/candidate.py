from fastapi import HTTPException
from bson.objectid import ObjectId
from ..database import database
from typing import Optional
import csv

candidate_collection = database.get_collection("candidate_collection")

def candidate_helper(candidate) -> dict:
    """
    Helper function to format candidate data.

    Args:
        candidate (dict): Candidate data from the database.

    Returns:
        dict: Formatted candidate data.
    """
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
    
async def retrieve_candidates(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None
):
    """
    Retrieves a list of candidates with pagination and search.

    Args:
        page (int): Page number for pagination.
        limit (int): Number of candidates per page.
        search (Optional[str]): Search term for filtering candidates.

    Returns:
        list: List of formatted candidate data.
    """
    skip = (page - 1) * limit

    query = {}
    if search:
        query = {
            "$or": [
                {"fullname": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"address": {"$regex": search, "$options": "i"}},
                {"education": {"$regex": search, "$options": "i"}},
                {"phone_number": {"$regex": search, "$options": "i"}},
                {"skills": {"$regex": search, "$options": "i"}}
            ]
        }

    candidates = []
    async for candidate in candidate_collection.find(query).skip(skip).limit(limit):
        candidates.append(candidate_helper(candidate))

    return candidates

async def add_candidate(candidate_data: dict) -> dict:
    """
    Adds a new candidate to the database.

    Args:
        candidate_data (dict): Candidate data to add.

    Returns:
        dict: Formatted candidate data of the newly added candidate.

    Raises:
        HTTPException: If candidate with the same email already exists.
    """
    candidate_exists = await candidate_collection.find_one({"email": candidate_data["email"]})
    if candidate_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    candidate = await candidate_collection.insert_one(candidate_data)
    new_candidate = await candidate_collection.find_one({"_id": candidate.inserted_id})
    return candidate_helper(new_candidate)

async def retrieve_candidate(id: str) -> dict:
    """
    Retrieves a candidate by ID.

    Args:
        id (str): Candidate ID.

    Returns:
        dict: Formatted candidate data if found.
    """
    candidate = await candidate_collection.find_one({"_id": ObjectId(id)})
    if candidate:
        return candidate_helper(candidate)

async def update_candidate(id: str, data: dict):
    """
    Updates a candidate by ID.

    Args:
        id (str): Candidate ID.
        data (dict): Data to update.

    Returns:
        dict: Formatted updated candidate data if successful.
    """
    if not data:
        return None
    candidate = await candidate_collection.find_one({"_id": ObjectId(id)})
    if not candidate:
        return None
    updated_result = await candidate_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    if updated_result.modified_count > 0:
        return await candidate_collection.find_one({"_id": ObjectId(id)})
    return None

async def delete_candidate(id: str):
    """
    Deletes a candidate by ID.

    Args:
        id (str): Candidate ID.

    Returns:
        bool: True if candidate was deleted, False otherwise.
    """
    candidate = await candidate_collection.find_one({"_id": ObjectId(id)})
    if candidate:
        await candidate_collection.delete_one({"_id": ObjectId(id)})
        return True

async def generate_csv_report():
    
    """
    Generates a CSV report of all candidates and saves it to a file.

    Returns:
        str: Path to the generated CSV file.

    Raises:
        Exception: If there is an error writing to the file.
    """
    
    
    headers = ["ID", "Full Name", "Email", "Address", "Education", "Phone Number", "Experience Years", "Skills"]

    async def fetch_and_prepare_candidates(batch_size=1000):
        candidates = []
        cursor = candidate_collection.find({})
        async for candidate in cursor:
            candidates.append(candidate)
            if len(candidates) == batch_size:
                yield candidates
                candidates = []
        if candidates:
            yield candidates

    file_path = 'report.csv'

    try:
        with open(file_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            async for batch in fetch_and_prepare_candidates():
                for candidate in batch:
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
    except Exception as e:
        # Handle file write errors
        print(f"Error writing to file: {e}")
        raise e

    return file_path