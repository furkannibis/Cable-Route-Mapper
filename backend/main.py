from fastapi import FastAPI

from data.route import data_route

app = FastAPI()
app.include_router(data_route)
