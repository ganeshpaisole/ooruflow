from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import rides, auth, drivers, recurring, payments, ratings, pool, tracking, admin, locations


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="OoruFlow — Bengaluru Office Commute",
    description=(
        "Pre-scheduled ride-hailing for Bengaluru office goers. "
        "Book by 8 PM IST, ride confirmed overnight."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rides.router)
app.include_router(drivers.router)
app.include_router(recurring.router)
app.include_router(payments.router)
app.include_router(ratings.router)
app.include_router(pool.router)
app.include_router(tracking.router)
app.include_router(admin.router)
app.include_router(locations.router)


@app.get("/", tags=["health"])
def read_root():
    return {"message": "Welcome to OoruFlow API", "city": "Bengaluru", "status": "Online"}
