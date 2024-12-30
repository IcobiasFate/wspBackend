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
cars_db = []
maintenance_db = []

# Input DTOs
class GarageCreateDTO(BaseModel):
    name: str
    location: str
    city: str
    capacity: int

class CarCreateDTO(BaseModel):
    make: str
    model: str
    productionYear: int
    licensePlate: str
    garageIds: List[int]  # A list of garage IDs

class MaintenanceCreateDTO(BaseModel):
    carId: int
    date: date
    description: str
    cost: float

# Output DTOs
class GarageDTO(BaseModel):
    id: int
    name: str
    location: str
    city: str
    capacity: int

class CarDTO(BaseModel):
    id: int
    make: str
    model: str
    productionYear: int
    licensePlate: str
    garages: List[GarageDTO]  # A list of associated garages


class MaintenanceDTO(BaseModel):
    id: int
    carId: int
    date: date
    description: str
    cost: float


# Garage-related functions
def get_garage_by_id(garage_id: int) -> Optional[GarageDTO]:
    for garage in garages_db:
        if garage.id == garage_id:
            return garage
    return None

def add_garage_to_db(garage_create_dto: GarageCreateDTO) -> GarageDTO:
    garage_id = len(garages_db) + 1  # Assign the id to the new garage
    new_garage = GarageDTO(id=garage_id, **garage_create_dto.dict())
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

# Car-related functions
def get_car_by_id(car_id: int) -> Optional[CarDTO]:
    for car in cars_db:
        if car.id == car_id:
            return car
    return None

def add_car_to_db(car_create_dto: CarCreateDTO) -> CarDTO:
    car_id = len(cars_db) + 1
    new_car = CarDTO(id=car_id, **car_create_dto.dict(), garages=[])
    # Assign garages to car based on garage IDs
    for garage_id in car_create_dto.garageIds:
        garage = get_garage_by_id(garage_id)
        if garage:
            new_car.garages.append(garage)
    cars_db.append(new_car)
    return new_car

def update_car_in_db(car_id: int, car_dto: CarDTO) -> Optional[CarDTO]:
    for index, existing_car in enumerate(cars_db):
        if existing_car.id == car_id:
            cars_db[index] = car_dto
            return car_dto
    return None

def delete_car_from_db(car_id: int) -> Optional[CarDTO]:
    for index, car in enumerate(cars_db):
        if car.id == car_id:
            return cars_db.pop(index)
    return None


# Maintenance-related functions (not working)
def get_maintenance_by_id(maintenance_id: int) -> Optional[MaintenanceDTO]:
    for maintenance in maintenance_db:
        if maintenance.id == maintenance_id:
            return maintenance
    return None

def add_maintenance_to_db(maintenance_create_dto: MaintenanceCreateDTO) -> MaintenanceDTO:
    maintenance_id = len(maintenance_db) + 1
    new_maintenance = MaintenanceDTO(id=maintenance_id, **maintenance_create_dto.dict())
    maintenance_db.append(new_maintenance)
    return new_maintenance

def update_maintenance_in_db(maintenance_id: int, maintenance_dto: MaintenanceDTO) -> Optional[MaintenanceDTO]:
    for index, existing_maintenance in enumerate(maintenance_db):
        if existing_maintenance.id == maintenance_id:
            maintenance_db[index] = maintenance_dto
            return maintenance_dto
    return None

def delete_maintenance_from_db(maintenance_id: int) -> Optional[MaintenanceDTO]:
    for index, maintenance in enumerate(maintenance_db):
        if maintenance.id == maintenance_id:
            return maintenance_db.pop(index)
    return None
# Garage route
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

# Car routes
@app.get("/cars", response_model=List[CarDTO])
async def get_cars(carMake: Optional[str] = None,
                   garageId: Optional[int] = None,
                   fromYear: Optional[int] = None,
                   toYear: Optional[int] = None):

    filtered_cars = cars_db

    # Apply filters
    if carMake:
        filtered_cars = [car for car in filtered_cars if car.make.lower() == carMake.lower()]

    if garageId:
        filtered_cars = [car for car in filtered_cars if any(garage.id == garageId for garage in car.garages)]

    if fromYear:
        filtered_cars = [car for car in filtered_cars if car.productionYear >= fromYear]

    if toYear:
        filtered_cars = [car for car in filtered_cars if car.productionYear <= toYear]


    return filtered_cars

@app.post("/cars", response_model=CarDTO)
async def add_car(car_create_dto: CarCreateDTO):
    car = add_car_to_db(car_create_dto)
    return car

@app.put("/cars/{car_id}", response_model=CarDTO)
async def update_car(car_id: int, car_dto: CarCreateDTO):
    existing_car = get_car_by_id(car_id)
    if not existing_car:
        raise HTTPException(status_code=404, detail="Car not found")

    updated_car = CarDTO(id=car_id, **car_dto.dict(), garages=[])
    # Assign updated garages based on garage IDs
    for garage_id in car_dto.garageIds:
        garage = get_garage_by_id(garage_id)
        if garage:
            updated_car.garages.append(garage)

    updated_car = update_car_in_db(car_id, updated_car)
    if not updated_car:
        raise HTTPException(status_code=404, detail="Car not found")

    return updated_car

@app.delete("/cars/{car_id}", response_model=CarDTO)
async def delete_car(car_id: int):
    removed_car = delete_car_from_db(car_id)
    if not removed_car:
        raise HTTPException(status_code=404, detail="Car not found")
    return removed_car





@app.get("/cars/dailyAvailabilityReport", response_model=List[GarageDTO])
async def get_car_report(start_date: date, end_date: date):

    return garages_db
