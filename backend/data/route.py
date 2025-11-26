from fastapi import APIRouter
import pandas as pd

from data.functions import *


data_route = APIRouter(prefix="/data")

@data_route.get("/pulley")
async def get_pulley():
    df = get_exist_pulley(filename_or_buffer="./data/cable.xlsx")
    print(df)

@data_route.get("/spread")
async def get_spread():
    df = get_spread_table("./data/cable.xlsx")
    print(df.columns)
    print(df.head())

    df = df.sort_values(by="starting_km_int")

    print(build_splice_table(df=df))