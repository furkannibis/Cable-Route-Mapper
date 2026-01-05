class Building:
    # TODO: Bu noktada tipe göre bir svg ayarlaman gerekiyor. Bu frontend de belirlenecek.
    def __init__(self, building_name: str, building_start_km: int, building_eng_km: int, line_number: int) -> None:
        self.building_name = building_name
        self.building_start_km = building_start_km
        self.building_end_km = building_eng_km
        self.line_number = line_number