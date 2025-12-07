class Cable():
    def __init__(self, cable_number: str, cable_type: str, cable_sheat: str, cable_lenght: int) -> None:
        self.cable_number = cable_number
        self.cable_type = cable_type
        self.cable_lenght = cable_lenght

        if cable_sheat == "A-DQ":
            self.cable_sheat = "LSZH"
        elif cable_sheat == "A-DF":
            self.cable_sheat = "PE"
        else:
            self.cable_sheat = cable_sheat
        
        self.used_lenght = 0
        self.last_location = "Kullanılmadı"

    def use_cable(self, lenght: int) -> None:
        self.used_lenght += lenght

    def find_remain_lenght(self) -> int:
        return self.cable_lenght - self.used_lenght

    def change_last_locagion(self, location: str) -> None:
        self.last_location = location

    def find_last_location(self) -> str:
        return self.last_location

class FiberCable(Cable):
    def __init__(self, cable_number: str, cable_type: str, cable_sheat: str, cable_lenght: int, cable_core_number: int) -> None:
        super().__init__(cable_number, cable_type, cable_sheat, cable_lenght)
        self.cable_core_number = cable_core_number
        
    def __str__(self) -> str:
        return f"""
                "Cable Type": {self.cable_type},
                "Cable Number": {self.cable_number},
                "Cable Sheat": {self.cable_sheat},
                "Cable Lenght": {self.cable_lenght},
                "Cable Core Number": {self.cable_core_number}
                "Cable Remain Lenght": {self.find_remain_lenght()}
                "Cable Last Location": {self.last_location}
                """

class EnergyCable(Cable):
    def __init__(self, cable_number: str, cable_type: str, cable_sheat: str, cable_lenght: int) -> None:
        super().__init__(cable_number, cable_type, cable_sheat, cable_lenght)
        self.used_lenght = 0

    def use_cable(self, lenght):
        self.used_lenght += lenght
        
    def __str__(self) -> str:
        return f"""
            "Cable Type": {self.cable_type},
            "Cable Number": {self.cable_number},
            "Cable Sheat": {self.cable_sheat},
            "Cable Lenght": {self.cable_lenght},
            "Cable Remain Lenght": {self.find_remain_lenght()}
            """

# class SignalCable():
# Burası da elbet gelecek