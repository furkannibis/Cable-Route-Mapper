import pandas as pd

def _clean_km(val) -> str | None:
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s.upper().startswith("EK"):
        s = s[2:].strip()
    return s

def km_to_int(x: str) -> int | None:
    """
    '58+913' -> 58913
    '53+00'  -> 53000
    Hatalı format varsa None döner.
    """
    if x is None or pd.isna(x):
        return None
    s = str(x).strip()
    s = s.replace("EK", "").strip()
    if "+" not in s:
        return None
    km, m = s.split("+", 1)
    km = km.strip()
    m = m.strip()
    if not (km.isdigit() and m.isdigit()):
        return None
    m = m.zfill(3)
    return int(km) * 1000 + int(m)

def get_exist_pulley(filename_or_buffer: str):
    df = pd.read_excel(io=filename_or_buffer, sheet_name=1)

    df = df.rename(columns={
        "KABLO CİNSİ": "cable_type",
        "CORE": "core",
        "MAKARA NO": "pulley_number",
        "UZUNLUK (mt)": "lenght"
    })

    df = df.drop('KALAN (mt)', axis=1)

    df["cable_type"] = df["cable_type"].replace({
        "A-DQ": "LSZH",
        "A-DF": "PE"
    })
    return df


def get_spread_table(filename_or_buffer: str):
    df = pd.read_excel(io=filename_or_buffer, sheet_name=2)
    df = df.drop(["Makara Uzunluğu", "Metraj Hatası", "Core Hatası", "Kılıf Hatası"], axis=1)
    df = df.rename(columns={
        "Tarih": "date",
        "Bina": "building",
        "Kablo Etiketi": "pulley_label", 
        "Nereden": "from",
        "Nereye": "to",
        "Kablo Tipi": "cable_type",
        "Makara Numarası": "pulley_number",
        "Makara Başlangıç": "pulley_start",
        "Makara Bitiş": "pulley_end",
        "Başlangıç Elemanı": "starting_object",
        "Başlangıç Km": "starting_km",
        "Bitiş Elemanı": "ending_object",
        "Bitiş Km": "ending_km",
        "Hat 1 / Hat 2": "line_number",
        "Ek Km": "supply_km",
        "Makara Kalan Uzunluk": "remained_pulley",
        "Serim(m)": "spread_meter"
    })

    df["starting_km"] = df["starting_km"].apply(_clean_km)
    df["ending_km"]   = df["ending_km"].apply(_clean_km)

    df["starting_km_int"] = df["starting_km"].apply(km_to_int)
    df["ending_km_int"]   = df["ending_km"].apply(km_to_int)

    df = df.dropna(subset=["starting_km_int", "ending_km_int"])

    return df



def build_splice_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Her km noktası için:
      - down_pulleys: bu noktadan daha küçük km'ye giden kablolar
      - up_pulleys  : bu noktadan daha büyük km'ye giden kablolar
    """
    all_points = set(df["starting_km_int"]).union(set(df["ending_km_int"]))
    points_sorted = sorted(all_points)

    rows = []

    for p in points_sorted:

        touch_mask = (df["starting_km_int"] == p) | (df["ending_km_int"] == p)


        down_mask = touch_mask & (
            ((df["starting_km_int"] == p) & (df["ending_km_int"] < p)) |
            ((df["ending_km_int"] == p) & (df["starting_km_int"] < p))
        )
        down_pulleys = (
            df.loc[down_mask, "pulley_number"]
            .astype(str)
            .unique()
            .tolist()
        )


        up_mask = touch_mask & (
            ((df["starting_km_int"] == p) & (df["ending_km_int"] > p)) |
            ((df["ending_km_int"] == p) & (df["starting_km_int"] > p))
        )
        up_pulleys = (
            df.loc[up_mask, "pulley_number"]
            .astype(str)
            .unique()
            .tolist()
        )


        km_str_candidates = df.loc[
            touch_mask,
            ["starting_km", "ending_km"]
        ].values.ravel().tolist()
        km_str_candidates = [x for x in km_str_candidates if isinstance(x, str)]
        km_str = km_str_candidates[0] if km_str_candidates else None

        rows.append({
            "km_int": p,
            "km": km_str,
            "down_pulleys": ", ".join(down_pulleys) if down_pulleys else None,
            "up_pulleys": ", ".join(up_pulleys) if up_pulleys else None,
        })
    return pd.DataFrame(rows)