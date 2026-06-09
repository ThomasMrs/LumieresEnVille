from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import semaphores, robots, teams, missions, shapes, health, config

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(semaphores.router)
app.include_router(robots.router)
app.include_router(teams.router)
app.include_router(missions.router)
app.include_router(shapes.router)
app.include_router(health.router)
app.include_router(config.router)