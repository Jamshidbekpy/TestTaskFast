from pydantic import BaseModel

class EventCreateIn(BaseModel):
    title: str
    description: str | None = None
    start_time: str
    end_time: str
    all_day: bool = False
    repeat: str | None = None
    url : str | None = None
    note: str | None = None

class EventCreateOut(BaseModel):
    id: str
    title: str
    description: str | None = None
    start_time: str
    end_time: str
    all_day: bool = False
    repeat: str | None = None
    url : str | None = None
    note: str | None = None

        
class EventRetrieveIn(BaseModel):
    id: str

class EventRetrieveOut(BaseModel):
    id: str
    title: str
    description: str | None = None
    start_time: str
    end_time: str
    all_day: bool = False
    repeat: str | None = None
    url : str | None = None
    note: str | None = None     

class EventUpdateIn(BaseModel):
    title: str | None = None
    description: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    all_day: bool | None = None
    repeat: str | None = None
    url : str | None = None
    note: str | None = None
    
class EventUpdateOut(BaseModel):
    id: str
    title: str
    description: str | None = None
    start_time: str
    end_time: str
    all_day: bool = False
    repeat: str | None = None
    url : str | None = None
    note: str | None = None
    
class EventDeleteIn(BaseModel):
    id: str

class EventDeleteOut(BaseModel):
    id: str
    message: str
