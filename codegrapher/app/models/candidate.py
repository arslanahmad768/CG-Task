from typing import List
from pydantic import BaseModel, EmailStr, Field

class Candidate(BaseModel):
    """
    Candidate model to represent a candidate's information.

    Attributes:
        fullname (str): The full name of the candidate.
        email (EmailStr): The email address of the candidate.
        address (str): The address of the candidate.
        education (str): The education details of the candidate.
        phone_number (str): The phone number of the candidate.
        experience_years (float): The number of years of experience the candidate has.
        skills (List[str]): A list of skills possessed by the candidate.

    Config:
        json_schema_extra (dict): Example of a candidate instance.
    """
    fullname: str = Field(..., min_length=2, max_length=50)
    email: EmailStr = Field(...)
    address: str = Field(...)
    education: str = Field(...)
    phone_number: str = Field(...)
    experience_years: float = Field(..., ge=0)
    skills: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "johndoe@example.com",
                "address": "xyz, UK",
                "education": "Bachelor in CS",
                "phone_number": "12345678901",
                "experience_years": 5.5,
                "skills": ["Python", "JavaScript", "SQL"]
            }
        }
