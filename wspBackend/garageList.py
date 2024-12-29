from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

app = FastAPI()


origins = [
    "http://localhost:3000",  # React frontend URL
    "http://127.0.0.1:3000",  # Alternative localhost URL for React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mock data storage
garages_db = []
reports_db = []


# Input DTOs
class GarageCreateDTO(BaseModel):
    name: str
    location: str
    city: str
    capacity: int


# Output DTOs
class GarageDTO(BaseModel):
    id: int
    name: str
    location: str
    city: str
    capacity: int


class GarageReportEntryDTO(BaseModel):
    date: date
    requests: int
    availableCapacity: int


# Service functions for interacting with the database
def get_garage_by_id(garage_id: int) -> Optional[GarageDTO]:
    for garage in garages_db:
        if garage.id == garage_id:
            return garage
    return None


def add_garage_to_db(garage_create_dto: GarageCreateDTO) -> GarageDTO:
    garage_id = len(garages_db) + 1  # Assign the id to the new garage
    new_garage = GarageDTO(id=garage_id, **garage_create_dto.dict())  # Create a GarageDTO from the input
    garages_db.append(new_garage)
    return new_garage


def update_garage_in_db(garage_id: int, garage_dto: GarageDTO) -> Optional[GarageDTO]:
    for index, existing_garage in enumerate(garages_db):
        if existing_garage.id == garage_id:
            garages_db[index] = garage_dto
            return garage_dto
    return None


def delete_garage_from_db(garage_id: int) -> Optional[GarageDTO]:
    for index, garage in enumerate(garages_db):
        if garage.id == garage_id:
            return garages_db.pop(index)
    return None


# Routes for managing garages
@app.get("/garages", response_model=List[GarageDTO])
async def get_garages(city: Optional[str] = None):
    if city:
        filtered_garages = [garage for garage in garages_db if garage.city.lower() == city.lower()]
        return filtered_garages
    return garages_db


@app.post("/garages", response_model=GarageDTO)
async def add_garage(garage_create_dto: GarageCreateDTO):
    garage = add_garage_to_db(garage_create_dto)
    return garage


@app.put("/garages/{garage_id}", response_model=GarageDTO)
async def update_garage(garage_id: int, garage_dto: GarageCreateDTO):
    existing_garage = get_garage_by_id(garage_id)
    if not existing_garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    # Convert the incoming DTO into a GarageDTO for the response
    updated_garage = GarageDTO(id=garage_id, **garage_dto.dict())
    updated_garage = update_garage_in_db(garage_id, updated_garage)

    if not updated_garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    return updated_garage


@app.delete("/garages/{garage_id}", response_model=GarageDTO)
async def delete_garage(garage_id: int):
    removed_garage = delete_garage_from_db(garage_id)
    if not removed_garage:
        raise HTTPException(status_code=404, detail="Garage not found")
    return removed_garage


# Route for fetching garage reports
@app.get("/garages/dailyAvailabilityReport", response_model=List[GarageReportEntryDTO])
async def get_garage_report(garageId: int, start_date: date, end_date: date):
    #data for testing
    reports_db.append(GarageReportEntryDTO(date=date.today(), requests=10, availableCapacity=50))

    filtered_reports = [
        report for report in reports_db if report.date >= start_date and report.date <= end_date
    ]
    return filtered_reports
