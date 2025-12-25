from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.settings import settings
from .api.v1.auth import router as v1_auth_router


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

