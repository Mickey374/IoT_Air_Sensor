class Addresses:
    ad_Windows = []
    ad_Fans = []

    def insertNewAddress(source, val):
        if val == "filters":
            Addresses.ad_Fans.append(source)
        elif val == "windows":
            Addresses.ad_Windows.append(source)

    
    def constructAddress():
        if Addresses.address is not None:
            return Addresses.address
        else:
            return None