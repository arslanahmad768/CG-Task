# from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing import List

class Candidate(BaseModel):
    fullname: str = Field(..., min_length=2, max_length=50)
    email: EmailStr = Field(...)
    address: str = Field(...)
    education: str = Field(...)
    phone_number: str = Field(...)
    experience_years: float = Field(..., ge=0)
    skills: List[str]

    class Config:
        json_schema_extra  = {
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
