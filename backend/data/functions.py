import pandas as pd
import numpy as np


def pulley(filename_or_buffer: str):
    """
    Main purpose of this function to get all pulley with pulley_number, lenght and type
    """
    df = pd.read_excel(io=filename_or_buffer, sheet_name=1)
    df = df.drop("KALAN (mt)", axis=1)
    df = df.rename(columns={
        "KABLO CİNSİ": "cable_type",
        "CORE": "core",
        "MAKARA NO": "pulley_number",
        "UZUNLUK (mt)": "lenght"
    })
    df = df.replace("A-DQ", "LSZH")
    df = df.replace("A-DF", "PE")
    return df


def spread(filename_or_buffer: str):
    """
    Main purpose of this function is get spreaded cable information systematicly
    """
    df = pd.read_excel(io=filename_or_buffer, sheet_name=2)

    df = df.drop(["Metraj Hatası", "Core Hatası", "Kılıf Hatası"], axis=1)
    df = df.rename(columns={
        "Tarih": "date",
        "Bina": "building",
        "Kablo Etiketi": "cable_ticket",
        "Nereden": "from",
        "Nereye": "to",
        "Kablo Tipi": "cable_type",
        "Makara Numarası": "pulley_number",
        "Makara Uzunluğu": "pulley_lenght",
        "Makara Başlangıç": "pulley_start_lenght",
        "Makara Bitiş": "pulley_end_lenght",
        "Başlangıç Elemanı": "start_element",
        "Başlangıç Km": "start_km",
        "Bitiş Elemanı": "end_element",
        "Bitiş Km": "end_km",
        "Hat 1 / Hat 2": "line_number",
        "Ek Km": "attachment_km",
        "Makara Kalan Uzunluk": "pulley_remain_lenght",
        "Serim(m)": "spread_lenght"
    })
    # NaN -> None (JSON uyumu için iyi)
    df = df.replace({np.nan: None})
    return df


def attacments(df: pd.DataFrame) -> pd.DataFrame:
    # start_km temizliği
    cleaned_start = []
    for km in df["start_km"]:
        if km is None:
            cleaned_start.append(None)
            continue

        s = str(km).strip()
        s_lower = s.lower()

        if "ek" in s_lower:          # "EK 56+990" -> "56+990"
            parts = s.split()
            s = parts[-1].strip()

        if "+" in s:                 # "56+990" -> "56990"
            s = s.replace("+", "")

        cleaned_start.append(s)

    df["start_km"] = cleaned_start

    # end_km temizliği
    cleaned_end = []
    for km in df["end_km"]:
        if km is None:
            cleaned_end.append(None)
            continue

        s = str(km).strip()
        s_lower = s.lower()

        if "ek" in s_lower:
            parts = s.split()
            s = parts[-1].strip()

        if "+" in s:
            s = s.replace("+", "")

        cleaned_end.append(s)

    df["end_km"] = cleaned_end

    for idx in df.index:
        sk = df.at[idx, "start_km"]
        ek = df.at[idx, "end_km"]

        if sk is None or ek is None:
            continue

        sk_str = str(sk)
        ek_str = str(ek)

        if sk_str.isdigit() and ek_str.isdigit():
            sk_int = int(sk_str)
            ek_int = int(ek_str)

            if sk_int > ek_int:
                df.at[idx, "start_km"], df.at[idx, "end_km"] = ek_str, sk_str

    df["cable_type_raw"] = df["cable_type"]
    df["jacket_type"] = df["cable_type_raw"].astype(str).str.contains(r"\(H\)").map({
        True: "LSZH",
        False: "PE"
    })

    df["cable_type"] = (
        df["cable_type"]
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype("Int64")
    )

    return df

# functions.py

def build_attachment_map(df: pd.DataFrame) -> pd.DataFrame:
    """
    Her satır:
      line_number, cable_type (core), jacket_type (LSZH/PE), km_int, km
    Hem başlangıç hem bitiş km'lerini nokta olarak ekler.
    """
    rows: list[dict] = []

    for _, row in df.iterrows():
        line = int(row["line_number"])
        core = int(row["cable_type"])
        jacket = row.get("jacket_type", None)

        for col in ("start_km", "end_km"):
            km_val = row[col]
            if km_val is None:
                continue

            s = str(km_val)
            if not s.isdigit():
                continue

            km_int = int(s)
            km_km = km_int // 1000
            km_m = km_int % 1000
            km_label = f"{km_km}+{str(km_m).zfill(3)}"

            rows.append(
                {
                    "line_number": line,
                    "cable_type": core,
                    "jacket_type": jacket,
                    "km_int": km_int,
                    "km": km_label,
                }
            )

    map_df = (
        pd.DataFrame(rows)
        .drop_duplicates(
            subset=["line_number", "cable_type", "jacket_type", "km_int"]
        )
        .sort_values(["line_number", "cable_type", "km_int"])
        .reset_index(drop=True)
    )
    return map_df
