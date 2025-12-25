from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.settings import settings
from .api.v1.auth import router as v1_auth_router
from .api.v1.fake_parse import router as v1_parse_router
from .api.v1.event import router as v1_event_router

from .websocket.routers import router as ws_router


app = FastAPI()


# cors middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
)

# include routers

# auth router
app.include_router(v1_auth_router, prefix=settings.API_V1_STR)

# parse router
app.include_router(v1_parse_router, prefix=settings.API_V1_STR)

# event router
app.include_router(v1_event_router, prefix=settings.API_V1_STR)

# websocket router
app.include_router(ws_router, prefix=settings.API_V1_STR)




