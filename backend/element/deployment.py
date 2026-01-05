from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DeploymentList:
    # TODO: Tüm string değerlerin içeriğindeki gereksiz " " ve \t leri falan temizle
    # TODO: Date'i date türüne çevir!
    # TODO: Cablo str olarak değil cable class'ı olarak gelecek ama hangi kablo olduğunu tespit etmen ve doğru cable class'ını girmen gerekiyor. Class'dan gelen class verilerini deployment'den silmen gerekiyor.
    # TODO: Valley lenght kablonun başlangıç uzunluğu olarak veriliyor bu doğru değil makaranın total uzunluğu olmalı
    # TODO: Tüm int verileri doğru bir şekilde alman lazım

    technical_building: str
    date: str
    valley_ticket: str
    start_location: str
    end_location: str
    cable_type: str
    valley_number: str
    valley_lenght: int
    valley_start_lenght: int
    valley_end_lenght: int
    start_building: str
    start_km: int
    end_building: str
    end_km: int
    line_number: int
    splice_km: Optional[int]
    valley_remain_lenght: int
    deployment_lenght: int


class Deployment:
    def __init__(self, deployment_list: list[DeploymentList]) -> None:
        self.deployment_list = deployment_list
