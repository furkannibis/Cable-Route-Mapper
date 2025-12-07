class Building():
    def __init__(self, building_type: str, building_name: str, building_location: str) -> None:
        self.building_type = building_type
        self.building_name = building_name
        self.building_location = building_location
    
    def select_building_type(self, building_end_location: int = 0):
        # Viyadük, Köprü, Alt geçit, Üst geçit vs
        # Tipleri belirlemek gerekiyor.
        if self.building_type.lower() == "viyadük":
            self.building_end_location = building_end_location
        
        # if self.building_type.lower() == ""