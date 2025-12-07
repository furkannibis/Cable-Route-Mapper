from cable import FiberCable
from deployment import DeploymentFiber, DeploymentPlanFiber
from function import read_fiber_cable, find_correct_valley, read_deployment_241
import pandas as pd

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



# for deployment in deploymentPlanFiber241.find_all_splice_points():
#     print(deploymentPlanFiber241.find_splice_point(deployment))

for x in deploymentPlanFiber241.splice_information():
    pass

# deploymentPlanFiber241.find_cable_information(cable_number="TUR06250845-1")
