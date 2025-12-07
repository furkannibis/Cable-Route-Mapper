import pandas as pd
from cable import FiberCable, EnergyCable
from typing import Optional, Any

def read_fiber_cable() -> list:
    fiber_cable = []
    df = pd.read_excel(io="../FO.xlsx", sheet_name=1)
    for _, row in df.iterrows():
        fiber_cable.append(["Ağ İletişim & GSM-R",row["CORE"], row["MAKARA NO"], row["UZUNLUK (mt)"], row["KABLO CİNSİ"]])
    return fiber_cable

def _clean_km(km_val: Any) -> int:
    if pd.isna(km_val):
        raise ValueError("KM değeri NaN olamaz")

    s = str(km_val).strip().upper()
    if s.startswith("EK"):
        parts = s.split()
        if len(parts) >= 2:
            s = parts[1].strip()
        else:
            raise ValueError(f"Geçersiz EK km formatı: {km_val}")

    s = s.replace("+", "")
    if not s.isdigit():
        raise ValueError(f"Geçersiz km formatı: {km_val}")

    return int(s)


def _clean_splice_km(km_val: Any) -> Optional[int]:
    if pd.isna(km_val):
        return None

    s = str(km_val).strip()
    if not s:
        return None

    s = s.upper()
    if s.startswith("EK"):
        parts = s.split()
        if len(parts) >= 2:
            s = parts[1].strip()
        else:
            return None
        
    s = s.replace("+", "")
    if not s.isdigit():
        return None

    return int(s)

def read_deployment_241() -> list:
    deployment_plan = []
    df = pd.read_excel(io="../FO.xlsx", sheet_name=2)
    for _, row in df.iterrows():
        date = row["Tarih"]
        building = row["Bina"]
        start_building = row["Nereden"]
        end_building = row["Nereye"]
        deployment_length = int(row["Serim(m)"])
        line_number = int(row["Hat 1 / Hat 2"])
        pulley_number = row["Makara Numarası"]

        start_km = _clean_km(row["Başlangıç Km"])
        end_km = _clean_km(row["Bitiş Km"])
        splice_km = _clean_splice_km(row["Ek Km"])

        deployment_plan.append([
            date,
            building,
            start_building,
            end_building,
            deployment_length,
            line_number,
            pulley_number,
            start_km,
            end_km,
            splice_km,
        ])

    return deployment_plan

def find_correct_valley(k: str, valley_list:list[FiberCable]):
    selected_cable = None
    for fiber in valley_list:
        if fiber.cable_number == k:
            selected_cable = fiber
    return selected_cable