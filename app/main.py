import yaml
from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from .core.settings import settings
from .api.v1.auth import router as v1_auth_router
from .api.v1.fake_parse import router as v1_parse_router
from .api.v1.event import router as v1_event_router

from .websocket.routers import router as ws_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_V1_STR.strip("/").split("/")[-1],
    description="This is a FastAPI application with JWT authentication, task scheduling using Celery, and WebSocket support.",
    contact={
        "name": "Jamshidbek Shodibekov",
        "email": "W3E5S@example.com",
    },
)


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




# OpenAPI JSON ni olish
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_json():
    return app.openapi()

# OpenAPI YAML ni olish
@app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml():
    openapi_json = app.openapi()
    yaml_str = yaml.dump(openapi_json, default_flow_style=False, allow_unicode=True)
    
    return Response(
        content=yaml_str,
        media_type="application/x-yaml",
        headers={
            "Content-Disposition": "attachment; filename=openapi.yaml"
        }
    )

# Swagger UI dan foydalanuvchilar uchun
@app.get("/docs/yaml", include_in_schema=False)
async def download_yaml():
    openapi_json = app.openapi()
    yaml_str = yaml.dump(openapi_json, default_flow_style=False, allow_unicode=True)
    
    return Response(
        content=yaml_str,
        media_type="application/x-yaml",
        headers={
            "Content-Disposition": "attachment; filename=api_documentation.yaml"
        }
    )

