from typing import Optional, Union

class Cable:
    def __init__(self, valley_number: str, shealt_type: str, valley_lenght: int) -> None:
        self.valley_number = valley_number
        self.shealt_type = shealt_type
        self.valley_lenght = valley_lenght

        self.location = "Kullanılmadı"
        self.used_lenght = 0
        self.remain_lenght = valley_lenght

        self.error_detection = str()

    def use(self, lenght: int, location: str) -> int:
        """
        Docstring for use
        Kablonun kullanılmasını sağlamak ve lokasyonları belirlemek.
        :param self: Description
        :param lenght: Kablo ne kadar kullanılacak
        :type lenght: int
        :param location: Kablonun yeni son noktası nerede
        :type location: str
        :return: Kablonun kalan uzunluğu return olarak verilir.
        :rtype: int
        """

        # TODO: Kablonun kullanılacak olan uzunluk için yeterli mi onu kontrol etmen gerekiyor.
        self.used_lenght += lenght
        self.location = location
        self.remain_lenght = self.valley_lenght - self.used_lenght

        if self.remain_lenght < 0:
            self.error_detection = f"{self.valley_number} Makara numarası {self.remain_lenght*-1} Metre fazla kullanıldı."

        return self.remain_lenght

    def __str__(self) -> str:
        return f"Makara Numarası: {self.valley_number}\nKablo Tipi: {self.shealt_type}\nMakara Uzunluğu: {self.valley_lenght}\nMakara Lokasyonu: {self.location}\nKalan Makara Uzunluğu: {self.remain_lenght}"

class Fiber(Cable):
    def __init__(self, valley_number: str, core: int, shealt_type: str, valley_lenght: int) -> None:
        super().__init__(valley_number, shealt_type, valley_lenght)
        self.core = core
    

    def __str__(self) -> str:
        return f"Makara Numarası: {self.valley_number}\nKablo Tipi: {self.shealt_type}\nKıl Sayısı: {self.core}\nMakara Uzunluğu: {self.valley_lenght}\nMakara Lokasyonu: {self.location}\nKalan Makara Uzunluğu: {self.remain_lenght}"

class Energy(Cable):
    def __init__(self, valley_number: str, shealt_type: str, valley_lenght: int) -> None:
        super().__init__(valley_number, shealt_type, valley_lenght)


class CableArea:
    def __init__(self) -> None:
        self.cable_list : list[Cable | Fiber | Energy] = []
    
    def add_cable(self, cable: Cable | Fiber | Energy):
        #
        self.cable_list.append(cable)

    def find_cable(self, valley_number: str) -> int | None:
        """
        Docstring for find_cable

        :param self: Description
        :param valley_number: Aranacak olan makara numarası
        :type valley_number: str
        :return: Cablo listesi içerisindeki verilen makara numarasının indexi
        :rtype: int
        """
        for inx in range(len(self.cable_list)):
            if self.cable_list[inx].valley_number == valley_number:
                return inx
        return None
    
    def __getitem__(self, inx: int | None) -> Fiber | Cable | Energy | str:
        if isinstance(inx, int):
            return self.cable_list[inx]
        else:
            return "Kablo bulunamadı"
        
    def __setitem__(self, idx: int, value: Union[Cable, Fiber, Energy]) -> None:
        self.cable_list[idx] = value