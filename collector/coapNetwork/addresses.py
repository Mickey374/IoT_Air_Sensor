class Addresses:
    ad_Filters = []

    def insertNewAddress(source, val):
        if val == "filters":
            Addresses.ad_Filters.append(source)
    
    def constructAddress():
        if Addresses.address is not None:
            return Addresses.address
        else:
            return None