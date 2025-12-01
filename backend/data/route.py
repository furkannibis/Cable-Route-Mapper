from fastapi import APIRouter, HTTPException
import pandas as pd

from data.functions import *

data_route = APIRouter(prefix="/data")

pulley_df: pd.DataFrame | None = None
spread_df: pd.DataFrame | None = None

line_1_288: pd.DataFrame | None = None
line_2_288: pd.DataFrame | None = None
line_1_24: pd.DataFrame | None = None
line_2_24: pd.DataFrame | None = None


@data_route.get("/pulley")
async def get_pulley():
    global pulley_df
    pulley_df = pulley(filename_or_buffer="./data/cable.xlsx")
    return pulley_df.to_dict(orient="records")

@data_route.post("/pulley")
async def post_pulley(pulley_number: str):
    global pulley_df, spread_df

    await get_attachments()

    if pulley_df is None or spread_df is None:
        raise HTTPException(status_code=500, detail="DataFrames not initialized")

    pulley_rows = pulley_df[pulley_df["pulley_number"] == pulley_number]
 
    if pulley_rows.empty:
        raise HTTPException(status_code=404, detail="Pulley not found")

    pulley_info = pulley_rows.iloc[0]
    usage_rows = spread_df[spread_df["pulley_number"] == pulley_number]
    used_length = float(usage_rows["spread_lenght"].fillna(0).sum())
    total_length = float(pulley_info["lenght"])
    remaining_calc = total_length - used_length

    if not usage_rows.empty:
        last_usage_row = usage_rows.iloc[-1]  # tablo sırasına göre son satır
        pulley_last_position = last_usage_row["end_element"]
        pulley_last_km = last_usage_row["end_km"]
    else:
        pulley_last_position = None
        pulley_last_km = None

    return {
        "pulley_number": pulley_number,
        "cable_type": pulley_info["cable_type"],
        "core": int(pulley_info["core"]),
        "total_length": total_length,
        "used_length": used_length,
        "remaining_length_calculated": remaining_calc,
        "pulley_last_position": pulley_last_position,
        "pulley_last_km": pulley_last_km
    }

@data_route.get("/spread")
async def get_spread():
    global spread_df
    spread_df = spread(filename_or_buffer="./data/cable.xlsx")
    return spread_df.to_dict(orient="records")


@data_route.get("/attachment")
async def get_attachments():
    """
    Bu endpoint sadece global df'leri ve line_x_y DataFrame'lerini hazırlıyor.
    """
    global spread_df, line_1_288, line_2_288, line_1_24, line_2_24

    await get_pulley()
    await get_spread()

    spread_df = attacments(spread_df)

    # 1. Hat 288
    line_1_288 = spread_df[(spread_df["line_number"] == 1) & (spread_df["cable_type"] == 288)]
    line_1_288_attachment_points = list(set(
        line_1_288["start_km"].tolist() + line_1_288["end_km"].tolist()
    ))
    line_1_288_attachment_points.sort()

    # 2. Hat 288
    line_2_288 = spread_df[(spread_df["line_number"] == 2) & (spread_df["cable_type"] == 288)]
    line_2_288_attachment_points = list(set(
        line_2_288["start_km"].tolist() + line_2_288["end_km"].tolist()
    ))
    line_2_288_attachment_points.sort()

    # 1. Hat 24
    line_1_24 = spread_df[(spread_df["line_number"] == 1) & (spread_df["cable_type"] == 24)]
    line_1_24_attachment_points = list(set(
        line_1_24["start_km"].tolist() + line_1_24["end_km"].tolist()
    ))
    line_1_24_attachment_points.sort()

    # 2. Hat 24
    line_2_24 = spread_df[(spread_df["line_number"] == 2) & (spread_df["cable_type"] == 24)]
    line_2_24_attachment_points = list(set(
        line_2_24["start_km"].tolist() + line_2_24["end_km"].tolist()
    ))
    line_2_24_attachment_points.sort()

    return {
        "line_1_288_points": line_1_288_attachment_points,
        "line_2_288_points": line_2_288_attachment_points,
        "line_1_24_points": line_1_24_attachment_points,
        "line_2_24_points": line_2_24_attachment_points,
    }


@data_route.post("/attachment")
async def post_attachment(line_number: int, cable_type: int, km: int):
    global spread_df, line_1_288, line_2_288, line_1_24, line_2_24

    await get_attachments()
    km_str = str(km)

    if line_number == 1 and cable_type == 24:
        decreasing_series = line_1_24[line_1_24["start_km"] == km_str]["pulley_number"]
        increasing_series = line_1_24[line_1_24["end_km"] == km_str]["pulley_number"]

        decreasing = decreasing_series.iloc[0] if not decreasing_series.empty else None
        increasing = increasing_series.iloc[0] if not increasing_series.empty else None

        return {
            "line_number": line_number,
            "km": km,
            "decreasing_pulley_number": decreasing,
            "increasing_pulley_number": increasing
        }
    
    elif line_number == 2 and cable_type == 24:
        decreasing_series = line_2_24[line_2_24["start_km"] == km_str]["pulley_number"]
        increasing_series = line_2_24[line_2_24["end_km"] == km_str]["pulley_number"]

        decreasing = decreasing_series.iloc[0] if not decreasing_series.empty else None
        increasing = increasing_series.iloc[0] if not increasing_series.empty else None

        return {
            "line_number": line_number,
            "km": km,
            "decreasing_pulley_number": decreasing,
            "increasing_pulley_number": increasing
        }

    elif line_number == 1 and cable_type == 288:
        decreasing_series = line_1_288[line_1_288["start_km"] == km_str]["pulley_number"]
        increasing_series = line_1_288[line_1_288["end_km"] == km_str]["pulley_number"]

        decreasing = decreasing_series.iloc[0] if not decreasing_series.empty else None
        increasing = increasing_series.iloc[0] if not increasing_series.empty else None

        return {
            "line_number": line_number,
            "km": km,
            "decreasing_pulley_number": decreasing,
            "increasing_pulley_number": increasing
        }
    
    elif line_number == 2 and cable_type == 288:
        decreasing_series = line_2_288[line_2_288["start_km"] == km_str]["pulley_number"]
        increasing_series = line_2_288[line_2_288["end_km"] == km_str]["pulley_number"]

        decreasing = decreasing_series.iloc[0] if not decreasing_series.empty else None
        increasing = increasing_series.iloc[0] if not increasing_series.empty else None

        return {
            "line_number": line_number,
            "km": km,
            "decreasing_pulley_number": decreasing,
            "increasing_pulley_number": increasing
        }

@data_route.get("/map")
async def get_map():
    """
    Tüm hatlar ve core tipleri için ek noktalarının harita verisi.
    """
    global spread_df

    await get_attachments()  # içinde spread + attacments zaten çağrılıyor

    map_df = build_attachment_map(spread_df)
    return map_df.to_dict(orient="records")

@data_route.post("/segment")
async def post_segment(
    line_number: int,
    cable_type: int,
    start_km: int,
    end_km: int,
):
    """
    İki ek noktası arasındaki segmentte hangi makara(lar) ve satırlar var?
    start_km ve end_km integer (ör: 56990 -> 56+990)
    """
    global spread_df

    # spread_df ve attacments hazır olsun
    await get_attachments()   # senin mevcut fonksiyonun, spread_df'yi dolduruyor varsayıyorum

    if spread_df is None:
        return {"error": "spread_df not initialized"}

    # km'leri sıralı hale getir
    if start_km > end_km:
        start_km, end_km = end_km, start_km

    df = spread_df.copy()

    # km kolonları int olsun
    df["start_km_int"] = df["start_km"].astype(int)
    df["end_km_int"] = df["end_km"].astype(int)

    # İlgili line & core içinden, bu aralığı kapsayan satırlar
    seg_rows = df[
        (df["line_number"] == line_number)
        & (df["cable_type"] == cable_type)
        & (df["start_km_int"] <= start_km)
        & (df["end_km_int"] >= end_km)
    ]

    pulleys = seg_rows["pulley_number"].dropna().astype(str).unique().tolist()

    return {
        "line_number": line_number,
        "cable_type": cable_type,
        "start_km": start_km,
        "end_km": end_km,
        "pulleys": pulleys,  # aradaki makara(lar)
        "rows": seg_rows.drop(
            columns=["start_km_int", "end_km_int"], errors="ignore"
        ).to_dict(orient="records"),
    }