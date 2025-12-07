from fastapi import APIRouter

from data.elements.cable import EnergyCable
from data.elements.deployment import DeploymentEnergy, DeploymentPlanEnergy
from data.elements.function import read_energy_cable, read_deployment_energy_1, read_deployment_energy_2, find_correct_valley_energy

energy_route = APIRouter(prefix="/energy")

@energy_route.get("/1")
async def line_1():
    energy_cable = []
    for cable in read_energy_cable():
        energy_cable.append(EnergyCable(
            cable_type=cable[0],
            cable_number=cable[1],
            cable_lenght=cable[2],
            cable_sheat=cable[3]
        ))
    
    deployment_list = read_deployment_energy_1()
    deploymentPlanEnergy1 = DeploymentPlanEnergy()

    for deployment in deployment_list:
        deploymentPlanEnergy1.add(deployment=DeploymentEnergy(
            date=deployment[0],
            building=deployment[1],
            start_building=deployment[2],
            end_building=deployment[3],
            deployment_length=int(deployment[4]),
            line_number=deployment[5],
            cable=find_correct_valley_energy(k=deployment[6], valley_list=energy_cable),
            start_km=deployment[7],
            end_km=deployment[8],
            splice_km=deployment[9]
        ))
    
    energy_result = []
    for deployment in deploymentPlanEnergy1.splice_information():
        energy_result.append(deployment) 

    return energy_result

@energy_route.get("/2")
async def line_2():
    energy_cable = []
    for cable in read_energy_cable():
        energy_cable.append(EnergyCable(
            cable_type=cable[0],
            cable_number=cable[1],
            cable_lenght=cable[2],
            cable_sheat=cable[3]
        ))
    
    deployment_list = read_deployment_energy_2()
    deploymentPlanEnergy2 = DeploymentPlanEnergy()

    for deployment in deployment_list:
        deploymentPlanEnergy2.add(deployment=DeploymentEnergy(
            date=deployment[0],
            building=deployment[1],
            start_building=deployment[2],
            end_building=deployment[3],
            deployment_length=int(deployment[4]),
            line_number=deployment[5],
            cable=find_correct_valley_energy(k=deployment[6], valley_list=energy_cable),
            start_km=deployment[7],
            end_km=deployment[8],
            splice_km=deployment[9]
        ))
    
    energy_result = []
    for deployment in deploymentPlanEnergy2.splice_information():
        energy_result.append(deployment) 

    return energy_result