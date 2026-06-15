from pathlib import Path
import re
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from routes import semaphores, robots, teams, missions, shapes, health, config, grille, segment

app = FastAPI()

app.include_router(semaphores.router)
app.include_router(robots.router)
app.include_router(teams.router)
app.include_router(missions.router)
app.include_router(shapes.router)
app.include_router(health.router)
app.include_router(config.router)
app.include_router(grille.router)
app.include_router(segment.router)