from fastapi import APIRouter
from ...dependencies import db_dependency, jwt_dependency
from ...schemas.events_schemas import EventCreateIn, EventCreateOut, EventUpdateIn, EventUpdateOut, EventRetrieveIn, EventRetrieveOut, EventDeleteIn, EventDeleteOut
from ...repository.event.event_repo import EventRepository
from ...services.event.event_service import EventService


router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/create/", response_model=EventCreateOut)
def create_event(event_in: EventCreateIn, db: db_dependency, access_token: jwt_dependency):
    repo = EventRepository(db)
    service = EventService(repo)
    
    return service.create_event(event_in, access_token)

@router.post("/update/", response_model=EventUpdateOut)
def update_event(event_in: EventUpdateIn, db: db_dependency,  access_token: jwt_dependency):
    repo = EventRepository(db)
    service = EventService(repo)
    
    return service.update_event(event_in, access_token)

@router.post("/retrieve/", response_model=EventRetrieveOut)
def retrieve_event(event_in: EventRetrieveIn, db: db_dependency, access_token: jwt_dependency):
    repo = EventRepository(db)
    service = EventService(repo)
    
    return service.get_event(event_in, access_token)

@router.post("/delete/", response_model=EventDeleteOut)
def delete_event(event_in: EventDeleteIn, db: db_dependency, access_token: jwt_dependency):
    repo = EventRepository(db)
    service = EventService(repo)
    
    return service.delete_event(event_in, access_token)