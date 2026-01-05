from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from element.cable import Fiber, Energy, CableArea
from element.read import read_deployment, read_cable, read_splice, splice_neighbors

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

global_errors = list()

fiber_cables = read_cable(type="fiber")
fiber_valleys = CableArea()
for fiber in fiber_cables:
    fiber_valleys.add_cable(Fiber(valley_number=fiber["valley_number"], core=fiber["core"], shealt_type=fiber["shealt_type"], valley_lenght=fiber["valley_lenght"]))

energy_cables = read_cable(type="energy")
energy_valleys = CableArea()
for energy in energy_cables:
    energy_valleys.add_cable(Energy(valley_number=energy["valley_number"], shealt_type=energy["shealt_type"], valley_lenght=energy["valley_lenght"]))

for deployment in read_deployment("24 F/O"):
    inx = fiber_valleys.find_cable(valley_number=deployment["valley_number"])
    if not isinstance(inx, int):
        global_errors.append(f"{deployment["valley_number"]} Makara numarası bulunamadı")
        continue
    fiber_valleys[inx].use(lenght=deployment["deployment_lenght"], location=deployment["end_location"])

for deployment in read_deployment("288 F/O"):
    inx = fiber_valleys.find_cable(valley_number=deployment["valley_number"])
    if not isinstance(inx, int):
        global_errors.append(f"{deployment["valley_number"]} Makara numarası bulunamadı")
        continue
    fiber_valleys[inx].use(lenght=deployment["deployment_lenght"], location=deployment["end_location"])

for deployment in read_deployment("2X6"):
    inx = energy_valleys.find_cable(valley_number=deployment["valley_number"])
    if not isinstance(inx, int):
        global_errors.append(f"{deployment["valley_number"]} Makara numarası bulunamadı.")
        continue
    energy_valleys[inx].use(lenght=deployment["deployment_lenght"], location=deployment["end_location"])


@app.get("/valley/fiber")
async def fiber_cable():
    global fiber_valleys
    return fiber_valleys

@app.get("/valley/energy")
async def energy_cable():
    global energy_valleys
    return energy_valleys

@app.get("/valley/errors")
async def global_error():
    global global_errors
    return global_errors

@app.post("/deployment/{cable_type:path}/{line_number}")
async def deployment(cable_type: str, line_number: int):
    return read_splice(cable_type=cable_type, line_number=line_number)

@app.post("/splice/{cable_type:path}/{line_number}")
async def splice(cable_type: str, line_number: int):
    return splice_neighbors(cable_type=cable_type, line_number=line_number)