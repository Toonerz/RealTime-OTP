class DistributedObject():
    
    def __init__(self, connection, doId, parentId, zoneId, dclass, hasOwnersView = False):
        self.connection = connection
        self.doId = doId
        self.parentId = parentId
        self.zoneId = zoneId
        self.dclass = dclass
        self.hasOwnersView = hasOwnersView
    
    def changeLocation(self, parentId, zoneId):
        self.oldParentId = parentId
        self.oldZoneId = zoneId
        
        self.parentId = parentId
        self.zoneId = zoneId
    
    def setOwnersView(self, hasOwnersView):
        self.hasOwnersView = hasOwnersView
    
    def getOwnersView(self):
        return self.hasOwnersView
