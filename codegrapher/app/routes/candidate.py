from typing import Annotated, Optional
from fastapi import APIRouter, Body, Query, Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from ..helpers import ResponseModel, ErrorResponseModel
from ..models.candidate import Candidate
from ..models.user import User
from fastapi.responses import FileResponse, JSONResponse
from ..api.users import get_current_active_user
from ..api.candidate import (
    add_candidate,
    retrieve_candidates,
    retrieve_candidate,
    update_candidate,
    delete_candidate,
    generate_csv_report
)

CandidateRouter = APIRouter()


@CandidateRouter.get("/generate-report", response_description="Generate CSV report of all candidates")
async def generate_report():
    """
    Generates a CSV report of all candidates and returns the file.

    Returns:
        FileResponse: CSV file containing the report.
    """
    try:
        file_path = await generate_csv_report()
        return FileResponse(file_path, media_type='text/csv', filename='report.csv')
    except Exception as e:
        print(f"An error occurred: {e}")
        return ErrorResponseModel("An error occurred.", 404, f"{e}")

@CandidateRouter.post("/", response_description="Candidate data added into the database")
async def add_candidate_data(current_user: User = Depends(get_current_active_user), candidate: Candidate = Body(...)):
    """
    Adds a new candidate to the database.

    Args:
        current_user (User): The currently authenticated user.
        candidate (Candidate): The candidate data to add.

    Returns:
        ResponseModel: Response with the newly added candidate data.
    """
    candidate = jsonable_encoder(candidate)
    new_candidate = await add_candidate(candidate)
    return ResponseModel(new_candidate, "Candidate added successfully.")

@CandidateRouter.get("/all-candidates", response_description="Retrieve all candidates with pagination and search")
async def get_candidates(
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, alias="page"),
    limit: int = Query(10, alias="limit"),
    search: Optional[str] = Query(None, alias="search")
):
    """
    Retrieves all candidates with optional pagination and search functionality.

    Args:
        current_user (User): The currently authenticated user.
        page (int): Page number for pagination.
        limit (int): Number of candidates per page.
        search (Optional[str]): Search term for filtering candidates.

    Returns:
        ResponseModel: Response with the list of candidates.
    """
    candidates = await retrieve_candidates(page, limit, search)
    if candidates:
        return ResponseModel(candidates, "Candidates data retrieved successfully")
    return ResponseModel(candidates, "No record found")

@CandidateRouter.get("/{id}", response_description="Retrieve candidate data by ID")
async def get_candidate_data(id: str, current_user: User = Depends(get_current_active_user)):
    """
    Retrieves candidate data by ID.

    Args:
        id (str): Candidate ID.
        current_user (User): The currently authenticated user.

    Returns:
        ResponseModel: Response with the candidate data if found.
        ErrorResponseModel: Error response if candidate not found.
    """
    candidate = await retrieve_candidate(id)
    if candidate:
        return ResponseModel(candidate, "Candidate data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "candidate doesn't exist.")

@CandidateRouter.put("/{id}", response_description="Update candidate data by ID")
async def update_candidate_data(
    id: str,
    current_user: User = Depends(get_current_active_user),
    req: Candidate = Body(...)
):
    """
    Updates candidate data by ID.

    Args:
        id (str): Candidate ID.
        current_user (User): The currently authenticated user.
        req (Candidate): The candidate data to update.

    Returns:
        ResponseModel: Response with the updated candidate data if successful.
        ErrorResponseModel: Error response if update failed.
    """
    updated_candidate = await update_candidate(id, req.dict())
    if updated_candidate:
        return ResponseModel(
            updated_candidate,
            "Candidate updated successfully",
        )
    return ErrorResponseModel(
        "Error",
        404,
        "There was an error updating the candidate data.",
    )

@CandidateRouter.delete("/{id}", response_description="Delete candidate data by ID")
async def delete_candidate_data(
    id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Deletes candidate data by ID.

    Args:
        id (str): Candidate ID.
        current_user (User): The currently authenticated user.

    Returns:
        ResponseModel: Response confirming the candidate was deleted.
        ErrorResponseModel: Error response if candidate not found.
    """
    deleted_candidate = await delete_candidate(id)
    if deleted_candidate:
        return ResponseModel(
            {}, "Candidate deleted successfully"
        )
    return ErrorResponseModel(
        "Error", 404, "Candidate with id {0} doesn't exist".format(id)
    )