from src.stateserver.DistributedObject import DistributedObject

class DoInterestManager:
    
    def __init__(self):
        self.doId2do = {}
        self.zonesByParentId = {}
        self.doIdByZoneId = {}
        self.doIdByConnection = {}
        self._DoInterestManager__interest = {}
        self.parentIds = []
        self.zoneIds = []
    
    def allocateNewDoId(self, parentId):
        """ TODO: allocate a new doId """
        pass
    
    def handleAddInterest(self, contextId, handle, location):
        (parentId, zoneId) = location
        
        if not parentId or zoneId:
            return
        
        if parentId in self.zonesByParentId:
            return
        
        if parentId:
            self.parentIds.append(parentId)
        
        if zoneId:
            self.zoneIds.append(zoneId)
        
        self.zonesByParentId[parentId] = self.zonesIds
        
        if contextId != handle: # can this even happen?
            self._DoInterestManager__interest[handle] = contextId
    
    def handleRemoveInterest(self, contextId, handle):
        if handle in self._DoInterestManager__interest:
            self.oldContextId = self.contextId
            self.oldHandle = self.handle
            
            # TODO: Assign the location to the contextId, we must do this because
            # if a shard disconnects it must be removed to prevent any avatars fr
            # om entering that shards doId. Same goes for zones, but for zones th
            # at would be more uncommon cases.
            del self._DoInterestManager__interest[handle]
            self.contextId = None
            self.handle = None
        
        return
    
    def handleGenerateWithRequired(self, connection, location, dclass):
        (parentId, zoneId) = location
        
        if not parentId or zoneId:
            return
        
        doId = int(self.allocateNewDoId(parentId))

        if doId not in self.doId2do:
            print ("Tried to handle update on an un-existant object: %d" % doId)
            return
        
        distributedObj = DistributedObject(connection, doId, parentId, zoneId, dclass)
        
        if parentId in self.zonesByParentId:
            if doId != self.doIdByZoneId:
                self.doIdByZoneId[doId] = zoneId
                
                # For use later, keep track of which client owns which object.
                if connection == distributedObj.connection:
                    self.doIdByConnection[distributedObj.connection] = distributedObj.doId
                else:
                    print ("Tried to assign the wrong object to the wrong owner.")
                    return
            else:
                print ("Tried to generate do: %d, in an invalid zoneId!" % distributedObj.doId)
                return
        else:
            print ("Tried to generate do: %d, in an invalid parentId!" % distributedObj.doId)
            return
        
        self.doId2do[distributedObj] = distributedObj.doId
    
    def handleGenerateWithRequiredAndId(self, connection, doId, location, dclass):
        (parentId, zoneId) = location
        
        if not parentId or zoneId:
            return
        
        if not doId:
            return

        if doId not in self.doId2do:
            print ("Tried to handle update on an un-existant object: %d" % doId)
            return
        
        distributedObj = DistributedObject(connection, doId, parentId, zoneId, dclass)
        
        # TODO: i really don't think well need this but, i can find a use for it later.
        # Store this discovery!
        if distributedObj.doId in self.doIdByConnection:
            if distributed.getOwnersView() != True:
                distributed.setOwnersView(True)
            else:
                pass
        
        if parentId in self.zonesByParentId:
            if doId != self.doIdByZoneId:
                self.doIdByZoneId[doId] = zoneId

                # For use later, keep track of which client owns which object.
                if connection == distributedObj.connection:
                    self.doIdByConnection[distributedObj.connection] = distributedObj.doId
                else:
                    print ("Tried to assign the wrong object to the wrong owner.")
                    return
            else:
                print ("Tried to generate do: %d, in an invalid zoneId!" % distributedObj.doId)
                return
        else:
            print ("Tried to generate do: %d, in an invalid parentId!" % distributedObj.doId)
            return
        
        self.doId2do[distributedObj] = distributedObj.doId
    
    def handleUpdateLocation(self, doId, location):
        (parentId, zoneId) = location

        if not parentId or zoneId:
            return
        
        if not doId:
            return

        if doId not in self.doId2do:
            print ("Tried to handle update on an un-existant object: %d" % doId)
            return
        
        distributedObj = self.doId2do[doId]
        
        if parentId in self.zonesByParentId:
            if doId in self.doIdByZoneId:
                del self.doIdByZoneId[doId]
            
                self.doIdByZoneId[doId] = zoneId
                distributedObj.changeLocation(parentId, zoneId)
            else:
                print ("Tried to update location of a non-generated object: %d" % doId)
                return
        else:
            print ("Tried to update location, but got an invalid parentId: %d" % parentId)
            return
    
    def handleUpdateField(self, doId, fieldId, remainingBytes):
        if not doId:
            return
        
        if fieldId == 0:
            return
        
        if doId not in self.doId2do:
            print ("Tried to handle update on an un-existant object: %d" % doId)
            return
        
        distributedObj = doId2do[doId]
        
        if doId in self.doIdByZoneId:
            pass # TODO: update this objects fields with the new values, store the old values.
            
            # TODO: Check the fields and send to the correct clients.
        else:
            print ("Tried to update an object with doId: %d that hasn't been generated yet!" % distributedObj.doId)
            return
    
    def handleObjectDisable(self, doId):
        if not doId:
            return

        if doId not in self.doId2do:
            print ("Tried to handle update on an un-existant object: %d" % doId)
            return
        
        distributedObj = doId2do[doId]
        
        if doId in self.doIdByZoneId:
            distributedObj.parentId = distributedObj.zoneId = None
        else:
            print ("Tried to disable do with doId: %d that hasn't been generated yet!" % distributedObj.doId)
            return
    
    def handleObjectDelete(self, doId):
        if not doId:
            return

        if doId not in self.doId2do:
            print ("Tried to handle update on an un-existant object: %d" % doId)
            return

        distributedObj = doId2do[doId]
        
        parentId = distributedObj.parentId
        zoneId = distributedObj.zoneId
        
        if doId in self.doIdByZoneId:
            if parentId != None:
                if zoneId != None:
                    distributedObj.doId = distributedObj.dclass = None
                    distributedObj.parentId = distributedObj.zoneId = None
                    
                    del self.doId2do[doId]
                    del self.doIdByZoneId[doId]
                    del distributedObj
