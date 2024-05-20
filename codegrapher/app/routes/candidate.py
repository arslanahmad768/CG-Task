from fastapi import APIRouter, Body, Query, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from ..helpers import ResponseModel, ErrorResponseModel
from ..models.candidate import Candidate
from fastapi.responses import FileResponse

from ..api.candidate import (
    add_candidate,
    retrieve_candidates,
    retrieve_candidate,
    update_candidate,
    delete_candidate,
    generate_csv_report
)

CandidateRouter = APIRouter()


@CandidateRouter.get("/generate-report", response_description="Candidate data added into the database")
async def root():
    file_path  = await generate_csv_report()
    return FileResponse(file_path, media_type='text/csv')

@CandidateRouter.post("/", response_description="Candidate data added into the database")
async def add_candidate_data(candidate: Candidate = Body(...)):
    candidate = jsonable_encoder(candidate)
    new_candidate = await add_candidate(candidate)
    return ResponseModel(new_candidate, "Candidate added successfully.")

@CandidateRouter.get("/all-candidates", response_description="candidates retrieved")
async def get_candidates(page: int = Query(1, alias="page"), limit: int = Query(10, alias="limit")):
    candidates = await retrieve_candidates(page, limit)
    if candidates:
        return ResponseModel(candidates, "Candidates data retrieved successfully")
    return ResponseModel(candidates, "Empty list returned")


@CandidateRouter.get("/{id}", response_description="candidate data retrieved")
async def get_candidate_data(id):
    candidate = await retrieve_candidate(id)
    if candidate:
        return ResponseModel(candidate, "Candidate data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "candidate doesn't exist.")

@CandidateRouter.put("/{id}")
async def update_candidate_data(id: str, req: Candidate = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_candidate = await update_candidate(id, req)
    if updated_candidate:
        return ResponseModel(
            "Candidate with ID: {} name update is successful".format(id),
            "Candidate name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the candidate data.",
    )

@CandidateRouter.delete("/{id}", response_description="Candidate data deleted from the database")
async def delete_candidate_data(id: str):
    deleted_candidate = await delete_candidate(id)
    if deleted_candidate:
        return ResponseModel(
            "Candidate with ID: {} removed".format(id), "Candidate deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "Candidate with id {0} doesn't exist".format(id)
    )
    


