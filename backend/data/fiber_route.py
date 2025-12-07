from fastapi import APIRouter
from data.elements.cable import FiberCable
from data.elements.deployment import DeploymentFiber, DeploymentPlanFiber
from data.elements.function import read_fiber_cable, find_correct_valley, read_deployment_241, read_deployment_242, read_deployment_2881, read_deployment_2882


fiber_route = APIRouter(prefix="/fiber")

@fiber_route.get("/241")
async def line_241():
    fiber_cable = []
    for cable in read_fiber_cable():
        fiber_cable.append(FiberCable(
            cable_type=cable[0],
            cable_core_number=cable[1],
            cable_number=cable[2],
            cable_lenght=cable[3],
            cable_sheat=cable[4]
        ))
    
    deployment_list = read_deployment_241()
    deploymentPlanFiber241 = DeploymentPlanFiber()

    for deployment in deployment_list:
        deploymentPlanFiber241.add(deployment=DeploymentFiber(
            date=deployment[0],
            building=deployment[1],
            start_building=deployment[2],
            end_building=deployment[3],
            deployment_length=int(deployment[4]),
            line_number=deployment[5],
            cable=find_correct_valley(k=deployment[6], valley_list=fiber_cable),
            start_km=deployment[7],
            end_km=deployment[8],
            splice_km=deployment[9]
        ))
    
    fiber_241_result = []
    for deployment in deploymentPlanFiber241.splice_information():
        fiber_241_result.append(deployment) 

    return fiber_241_result

@fiber_route.get("/242")
async def line_242():
    fiber_cable = []
    for cable in read_fiber_cable():
        fiber_cable.append(FiberCable(
            cable_type=cable[0],
            cable_core_number=cable[1],
            cable_number=cable[2],
            cable_lenght=cable[3],
            cable_sheat=cable[4]
        ))
    
    deployment_list = read_deployment_242()
    deploymentPlanFiber242 = DeploymentPlanFiber()

    for deployment in deployment_list:
        deploymentPlanFiber242.add(deployment=DeploymentFiber(
            date=deployment[0],
            building=deployment[1],
            start_building=deployment[2],
            end_building=deployment[3],
            deployment_length=int(deployment[4]),
            line_number=deployment[5],
            cable=find_correct_valley(k=deployment[6], valley_list=fiber_cable),
            start_km=deployment[7],
            end_km=deployment[8],
            splice_km=deployment[9]
        ))
    
    fiber_242_result = []
    for deployment in deploymentPlanFiber242.splice_information():
        fiber_242_result.append(deployment) 

    return fiber_242_result

@fiber_route.get("/2881")
async def line_2881():
    fiber_cable = []
    for cable in read_fiber_cable():
        fiber_cable.append(FiberCable(
            cable_type=cable[0],
            cable_core_number=cable[1],
            cable_number=cable[2],
            cable_lenght=cable[3],
            cable_sheat=cable[4]
        ))
    
    deployment_list = read_deployment_2881()
    deploymentPlanFiber2881 = DeploymentPlanFiber()

    for deployment in deployment_list:
        deploymentPlanFiber2881.add(deployment=DeploymentFiber(
            date=deployment[0],
            building=deployment[1],
            start_building=deployment[2],
            end_building=deployment[3],
            deployment_length=int(deployment[4]),
            line_number=deployment[5],
            cable=find_correct_valley(k=deployment[6], valley_list=fiber_cable),
            start_km=deployment[7],
            end_km=deployment[8],
            splice_km=deployment[9]
        ))
    
    fiber_2881_result = []
    for deployment in deploymentPlanFiber2881.splice_information():
        fiber_2881_result.append(deployment) 

    return fiber_2881_result

@fiber_route.get("/2882")
async def line_2882():
    fiber_cable = []
    for cable in read_fiber_cable():
        fiber_cable.append(FiberCable(
            cable_type=cable[0],
            cable_core_number=cable[1],
            cable_number=cable[2],
            cable_lenght=cable[3],
            cable_sheat=cable[4]
        ))
    
    deployment_list = read_deployment_2882()
    deploymentPlanFiber2882 = DeploymentPlanFiber()

    for deployment in deployment_list:
        deploymentPlanFiber2882.add(deployment=DeploymentFiber(
            date=deployment[0],
            building=deployment[1],
            start_building=deployment[2],
            end_building=deployment[3],
            deployment_length=int(deployment[4]),
            line_number=deployment[5],
            cable=find_correct_valley(k=deployment[6], valley_list=fiber_cable),
            start_km=deployment[7],
            end_km=deployment[8],
            splice_km=deployment[9]
        ))
    
    fiber_2882_result = []
    for deployment in deploymentPlanFiber2882.splice_information():
        fiber_2882_result.append(deployment) 

    return fiber_2882_result