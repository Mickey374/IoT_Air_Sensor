class Addresses:
    ad_Filters = []
    ad_Fans = []

    def insertNewAddress(source, val):
        if val == "extractors":
            Addresses.ad_Filters.append(source)
        elif val == "fans":
            Addresses.ad_Fans.append(source)

    
    def constructAddress():
        if Addresses.address is not None:
            return Addresses.address
        else:
            return None