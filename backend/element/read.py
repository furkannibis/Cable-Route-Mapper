import pandas as pd
import numpy as np
import re

from typing import Optional

def clear_value(value: str) -> Optional[str]:
        if pd.isna(value):
            return None

        try:
            text = str(value).upper()
        except Exception:
            return None

        text = re.sub(r"\s+", " ", text.replace("\t", " ").replace("\n", " ")).strip()
        if text.startswith("TUR"):
            text = text.replace(" ", "")
        return text

def clear_km(km: str):
    if pd.isna(km):
        return None

    text = str(km)

    text = re.sub(r"\s+", " ", text)
    match = re.search(r"(\d+)\s*\+\s*(\d+)", text)
    if not match:
        return None

    km, m = match.groups()
    return int(int(km) * 1000 + int(m))

def read_deployment(cable_type: str, io="./data/deployment/deployment.xlsx"):
    df = pd.read_excel(io=io, sheet_name=0)
    df = df.rename(columns={
        "TB": "technical_building",
        "Tarih": "date",
        "Kablo Etiketi": "valley_ticket",
        "Nereden": "start_location",
        "Nereye": "end_location",
        "Kablo Tipi": "cable_type",
        "Makara Numarası": "valley_number",
        "Makara Uzunluğu": "valley_lenght",
        "Makara Başlangıç": "valley_start_lenght",
        "Makara Bitiş": "valley_end_lenght",
        "Başlangıç Elemanı": "start_building",
        "Başlangıç Km": "start_km",
        "Bitiş Elemanı": "end_building",
        "Bitiş Km": "end_km",
        "Hat 1 / Hat 2": "line_number",
        "Ek Km": "splice_km",
        "Makara Kalan Uzunluk": "valley_remain_lenght",
        "Serim(m)": "deployment_lenght"
    })
    df = df.sort_values(by="date", ascending=True)

    df["start_km"] = df["start_km"].apply(clear_km)
    df["end_km"] = df["end_km"].apply(clear_km)
    df["splice_km"] = df["splice_km"].apply(clear_km)

    df["technical_building"] = df["technical_building"].apply(clear_value)
    df["valley_ticket"] = df["valley_ticket"].apply(clear_value)
    df["start_location"] = df["start_location"].apply(clear_value)
    df["end_location"] = df["end_location"].apply(clear_value)
    df["valley_number"] = df["valley_number"].apply(clear_value)
    df["start_building"] = df["start_building"].apply(clear_value)
    df["end_building"] = df["end_building"].apply(clear_value)

    df = df.fillna('')
    
    df_filtered = df[
        (df["cable_type"].isin([cable_type, f"{cable_type}(H)"]))
    ]

    return df_filtered.to_dict(orient="records")

def read_cable(type: str = "fiber") -> list[dict]:
    if type == "fiber":
        df = pd.read_excel(io=f"./data/cable/{type}.xlsx", sheet_name=0)
        df = df.rename(columns={
            "KABLO CİNSİ": "shealt_type",
            "CORE": "core",
            "MAKARA NO": "valley_number",
            "UZUNLUK (mt)": "valley_lenght"
        })
        df = df.replace("A-DF", "PE")
        df = df.replace("A-DQ", "LSZH")
        return df.to_dict(orient="records")
    elif type == "energy":
        df = pd.read_excel(io=f"./data/cable/{type}.xlsx", sheet_name=0)
        df = df.rename(columns={
            "Kablo Cinsi": "shealt_type",
            "MAKARA NO": "valley_number",
            "UZUNLUK (mt)": "valley_lenght"
        })
        df = df[["valley_number", "shealt_type", "valley_lenght"]]
        return df.to_dict(orient="records")
    return []

def read_splice(cable_type: str, line_number: int, io="./data/deployment/deployment.xlsx") -> list[dict]:
    df = pd.read_excel(io=io, sheet_name=0)
    df = df.rename(columns={
        "TB": "technical_building",
        "Tarih": "date",
        "Kablo Etiketi": "valley_ticket",
        "Nereden": "start_location",
        "Nereye": "end_location",
        "Kablo Tipi": "cable_type",
        "Makara Numarası": "valley_number",
        "Makara Uzunluğu": "valley_lenght",
        "Makara Başlangıç": "valley_start_lenght",
        "Makara Bitiş": "valley_end_lenght",
        "Başlangıç Elemanı": "start_building",
        "Başlangıç Km": "start_km",
        "Bitiş Elemanı": "end_building",
        "Bitiş Km": "end_km",
        "Hat 1 / Hat 2": "line_number",
        "Ek Km": "splice_km",
        "Makara Kalan Uzunluk": "valley_remain_lenght",
        "Serim(m)": "deployment_lenght"
    })
    df = df.sort_values(by="date", ascending=True)

    df["start_km"] = df["start_km"].apply(clear_km)
    df["end_km"] = df["end_km"].apply(clear_km)
    df["splice_km"] = df["splice_km"].apply(clear_km)

    df["technical_building"] = df["technical_building"].apply(clear_value)
    df["valley_ticket"] = df["valley_ticket"].apply(clear_value)
    df["start_location"] = df["start_location"].apply(clear_value)
    df["end_location"] = df["end_location"].apply(clear_value)
    df["valley_number"] = df["valley_number"].apply(clear_value)
    df["start_building"] = df["start_building"].apply(clear_value)
    df["end_building"] = df["end_building"].apply(clear_value)

    df = df.fillna('')
    
    df_filtered = df[
        (df["line_number"] == line_number) &
        (df["cable_type"].isin([cable_type, f"{cable_type}(H)"]))
    ]

    df_filtered.sort_values(by="start_km")

    return df_filtered.to_dict(orient="records")


def splice_neighbors(cable_type: str, line_number: int, io="./data/deployment/deployment.xlsx"):
    """
    Docstring for find_splice_points
    Kısaca deployment'e göre ek noktalarını hesap edecek bir fonksiyon kendileri

    :param cable_type: kablonun tipi gelecek kısaca
    :type cable_type: str
    :param line_number: hangi hatta bakıyorsun onu işaretlemek gerekiyor
    :type line_number: int
    :param io: Deployment dosyasının path'i
    """
    records = read_splice(cable_type=cable_type, line_number=line_number, io=io)

    segs: list[dict] = []
    points: set[int] = set()

    for r in records:
        rr = dict(r)

        sk = rr.get("start_km")
        ek = rr.get("end_km")
        sp = rr.get("splice_km")

        rr["_km_min"] = min(sk, ek) if isinstance(sk, int) and isinstance(ek, int) else (sk if isinstance(sk, int) else ek)
        rr["_km_max"] = max(sk, ek) if isinstance(sk, int) and isinstance(ek, int) else (ek if isinstance(ek, int) else sk)

        segs.append(rr)

        if isinstance(sp, int):
            points.add(sp)
        if isinstance(rr["_km_min"], int):
            points.add(rr["_km_min"])
        if isinstance(rr["_km_max"], int):
            points.add(rr["_km_max"])

    sorted_points = sorted(points)

    def pack(seg: dict) -> dict:
        return {
            "valley_number": seg.get("valley_number"),
            "cable_type": seg.get("cable_type"),
            "start_location": seg.get("start_location"),
            "end_location": seg.get("end_location"),
            "start_km": seg.get("start_km"),
            "end_km": seg.get("end_km"),
            "deployment_lenght": seg.get("deployment_lenght"),
        }

    out: list[dict] = []


    for p in sorted_points:
        print(p)
        before = [pack(s) for s in segs if s.get("_km_max") == p]
        after  = [pack(s) for s in segs if s.get("_km_min") == p]


        if not before and not after:
            continue

        out.append({
            "splice_km": p,
            "before": before,
            "after": after,
        })

    return out
