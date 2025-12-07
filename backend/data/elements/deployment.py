from typing import Optional
from data.elements.cable import FiberCable, EnergyCable

class Deployment:
    def __init__(self, date: str, building: str, start_building: str, end_building: str,
    start_km: int, end_km: int, line_number: int, splice_km: Optional[int], deployment_length: int) -> None:
        self.date = date
        self.building = building
        self.start_building = start_building
        self.end_building = end_building
        self.start_km = start_km
        self.end_km = end_km
        self.line_number = line_number
        self.splice_km = splice_km
        self.deployment_length = deployment_length
    

class DeploymentFiber(Deployment):
    def __init__(self, date: str, building: str, start_building: str, end_building: str, start_km: int, end_km: int, line_number: int, splice_km: Optional[int], deployment_length: int, cable: FiberCable) -> None:
        super().__init__(date, building, start_building, end_building, start_km, end_km, line_number, splice_km, deployment_length)
        self.cable = cable


class DeploymentEnergy(Deployment):
    def __init__(self, date: str, building: str, start_building: str, end_building: str, start_km: int, end_km: int, line_number: int, splice_km: Optional[int], deployment_length: int, cable: EnergyCable) -> None:
        super().__init__(date, building, start_building, end_building, start_km, end_km, line_number, splice_km, deployment_length)
        self.cable = cable

class DeploymentPlanFiber:
    def __init__(self) -> None:
        self.deployments: list[DeploymentFiber] = []

    def add(self, deployment: Deployment) -> None:
        if isinstance(deployment, DeploymentFiber):
            self.deployments.append(deployment)
            deployment.cable.use_cable(lenght=deployment.deployment_length)
            deployment.cable.change_last_locagion(location=deployment.end_building)

    def find_splice_point(self, km):
        lower_cable_number = None
        higher_cable_number = None

        for deployment in self.deployments:
            if deployment.end_km == km:
                lower_cable_number = deployment.cable.cable_number
                break

        for deployment in self.deployments:
            if deployment.start_km == km:
                higher_cable_number = deployment.cable.cable_number
                break
        return (lower_cable_number, higher_cable_number)
    
    def find_all_splice_points(self):
        splice_points = []
        for deployment in self.deployments:
            if deployment.start_km not in splice_points:
                splice_points.append(deployment.start_km)
            if deployment.end_km not in splice_points:
                splice_points.append(deployment.end_km)
        
        return splice_points

    def find_cable_information(self, cable_number):
        for deployment in self.deployments:
            if deployment.cable.cable_number == cable_number:
                return {
                    "Cable Type": deployment.cable.cable_type,
                    "Cable Number": deployment.cable.cable_number,
                    "Cable Core Number": deployment.cable.cable_core_number,
                    "Cable Sheat Type": deployment.cable.cable_sheat,
                    "Cable Lenght": deployment.cable.cable_lenght,
                    "Cable Remain Lenght": deployment.cable.find_remain_lenght(),
                    "Cable Used Lenght": deployment.cable.used_lenght,
                    "Cable Last Location": deployment.cable.find_last_location()
                }

    def splice_information(self) -> list[dict]:
        splice_points = []
        for deployment in self.deployments:
            splice_points.append({
                "Splice KM": deployment.start_km,
                "Splice Lower Information": self.find_cable_information(cable_number=self.find_splice_point(km=deployment.start_km)[0]),
                "Splice Higher Information": self.find_cable_information(cable_number=self.find_splice_point(km=deployment.start_km)[1]),
            })
    
        return splice_points
    
class DeploymentPlanEnergy:
    def __init__(self) -> None:
        self.deployments: list[DeploymentEnergy] = []

    def add(self, deployment: Deployment) -> None:
        if isinstance(deployment, DeploymentEnergy):
            self.deployments.append(deployment)
            deployment.cable.use_cable(lenght=deployment.deployment_length)
            deployment.cable.change_last_locagion(location=deployment.end_building)

    def find_splice_point(self, km):
        lower_cable_number = None
        higher_cable_number = None

        for deployment in self.deployments:
            if deployment.end_km == km:
                lower_cable_number = deployment.cable.cable_number
                break

        for deployment in self.deployments:
            if deployment.start_km == km:
                higher_cable_number = deployment.cable.cable_number
                break
        return (lower_cable_number, higher_cable_number)
    
    def find_all_splice_points(self):
        splice_points = []
        for deployment in self.deployments:
            if deployment.start_km not in splice_points:
                splice_points.append(deployment.start_km)
            if deployment.end_km not in splice_points:
                splice_points.append(deployment.end_km)
        
        return splice_points

    def find_cable_information(self, cable_number):
        for deployment in self.deployments:
            if deployment.cable.cable_number == cable_number:
                return {
                    "Cable Type": deployment.cable.cable_type,
                    "Cable Number": deployment.cable.cable_number,
                    "Cable Sheat Type": deployment.cable.cable_sheat,
                    "Cable Lenght": deployment.cable.cable_lenght,
                    "Cable Remain Lenght": deployment.cable.find_remain_lenght(),
                    "Cable Used Lenght": deployment.cable.used_lenght,
                    "Cable Last Location": deployment.cable.find_last_location()
                }

    def splice_information(self) -> list[dict]:
        splice_points = []
        for deployment in self.deployments:
            splice_points.append({
                "Splice KM": deployment.start_km,
                "Splice Lower Information": self.find_cable_information(cable_number=self.find_splice_point(km=deployment.start_km)[0]),
                "Splice Higher Information": self.find_cable_information(cable_number=self.find_splice_point(km=deployment.start_km)[1]),
            })
    
        return splice_points