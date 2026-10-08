from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .exceptions import ConflictError, DomainError, NotFoundError, ValidationError
from .routers import projects, tasks

STATIC = Path(__file__).resolve().parent.parent / "static"

# Domain error -> HTTP status. New error types only need a line here (open/closed).
STATUS_BY_ERROR = {NotFoundError: 404, ConflictError: 409, ValidationError: 422}


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="TaskBoard", lifespan=lifespan)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse({"detail": str(exc)}, status_code=STATUS_BY_ERROR.get(type(exc), 400))


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
