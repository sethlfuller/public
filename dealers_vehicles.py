import json, requests, urllib, grequests,pprint, time

start_time = time.time()

def getDataSetID():
    dataSetIDurl = "http://vautointerview.azurewebsites.net/api/datasetId"
    dataSetIDResponse = requests.get(dataSetIDurl)
    dataSetIDJSON = dataSetIDResponse.json()
    dataSetID = dataSetIDJSON['datasetId']
    print "DataSetID is: " + dataSetID + ". Retrieving associated vehicle IDs..."
    return dataSetID

def getVehicleIDs(ID):
    dataSetID = ID
    vehicleIDurl = "http://vautointerview.azurewebsites.net/api/" + dataSetID + "/vehicles"
    vehicleIDResponse = requests.get(vehicleIDurl)
    vehicleIDJSON = vehicleIDResponse.json()
    vehicleIDList = json.loads(json.dumps(vehicleIDJSON)) #Convert JSON object to Python object
    #print vehicleIDList
    return vehicleIDList

#def getDealerName(dealerID, dataSetID):
#    dealerNameurl = "http://vautointerview.azurewebsites.net/api/" + dataSetID + "/dealers/" + str(dealerID)
#    dealerNameResponse = requests.get(dealerNameurl)
#    dealerNameJSON = dealerNameResponse.json()
#    dealerName = dealerNameJSON['name']
#    return dealerName

def getDealerInfo(vehicleIDs,dataSetID):
    #dealer_ids, dealer_id_names, vehicle_years, vehicle_makes, vehicle_models = [],[],[],[],[]    
    vehicleINFOurls=[]
    dealerINFOurls=[]
    dealerIDs=[]
    vehicleslist=[]
    for id in vehicleIDs['vehicleIds']:        
        #dealerNameurl = "http://vautointerview.azurewebsites.net/api/" + dataSetID + "/dealers/" + dealer_id
        vehicleINFOurl = "http://vautointerview.azurewebsites.net/api/" + dataSetID +"/vehicles/" + str(id)
        vehicleINFOurls.append(vehicleINFOurl) # Build url list to send simultaneous requests
        #vehicleINFOResponse = requests.get(vehicleINFOurl)
        #vehicleINFOJSON = vehicleINFOResponse.json()
        #vehicleINFOList = json.loads(json.dumps(vehicleINFOJSON))
        #dealerID = vehicleINFOJSON['dealerId']
        #dealerName = getDealerName(dealerID,dataSetID)
    vehicleINFORequests = (grequests.get(u) for u in vehicleINFOurls) # Send url requests simultaneously
    vehicleINFOResponses = grequests.map(vehicleINFORequests) # Build responses returned
    vehicleINFOjson = [vehicleINFOResponse.json() for vehicleINFOResponse in vehicleINFOResponses ] # Store json response
    #pprint.pprint(vehicleINFOjson)
    vehicleINFOList = json.loads(json.dumps(vehicleINFOjson))

    for vehicleINFO in vehicleINFOList:    #get unique list of dealer ids and names    
        dealerID = vehicleINFO["dealerId"]
        dealerIDs.append(dealerID)       

    dealerIDs = set(dealerIDs)

    for dealerID in dealerIDs:
        dealerINFOurl = "http://vautointerview.azurewebsites.net/api/" + dataSetID + "/dealers/" + str(dealerID)
        dealerINFOurls.append(dealerINFOurl)
    dealerINFORequests = (grequests.get(u) for u in dealerINFOurls) # Send url requests simultaneously
    dealerINFOResponses = grequests.map(dealerINFORequests) # Build responses returned
    dealerINFOjson = [dealerINFOResponse.json() for dealerINFOResponse in dealerINFOResponses ] # Store json response
    dealerINFOList = json.loads(json.dumps(dealerINFOjson))
    #print dealerINFOList

    dealers = []
    vehicles = []
    #print "starting list test"
    #dealer_dictionary = [dealerINFOList[dealerId],dealerINFOList["name"]]
    #dealerset = { dealerINFO["dealerId"] : dealerINFO["name"] for dealerINFO  in dealerINFOList }
    #print dealerset
    #print "end list test"

    json_message = "{\"dealers\":[{"
    for dealerINFO in dealerINFOList:
        json_message += "\"dealerId\":\"" + str(dealerINFO["dealerId"]) + "\",\"name\":\"" + str(dealerINFO["name"]) + "\""
        #dealerset = { "dealers" : { "dealerId": dealerINFO["dealerId"], "name": dealerINFO["name"]}}         
        #newDealerID = dealerINFO["dealerId"]
        #dealerList = {'dealerId': dealerINFO["dealerId"], 'name': dealerINFO["name"]}
        dealersCount=0
        for vehicleINFO in vehicleINFOList:        
            if vehicleINFO["dealerId"] == dealerINFO["dealerId"]:
                #"Dealer ID is " , dealerINFO["dealerId"] , " and vehicle ID is " , vehicleINFO["vehicleId"]
                #dealerset[dealerid][veicles][year] = 
                vehicles = { 'vehicleId': vehicleINFO["vehicleId"],'year': vehicleINFO["year"],'make': vehicleINFO["make"],'model': vehicleINFO["model"]}                
                vehicleslist.append(vehicles)                
                #print vehicleINFO["vehicleId"]        
        #pprint.pprint(vehicleslist)
        #dealers.append(dealerset)        
        #print "+++++++++++++++"
    json_message += "]}"
    pprint.pprint(json_message)
    #pprint.pprint(dealers)
    #print complete
    #pprint.pprint(vehicleslist)
    
    

    #print vehicleslist


def main():
    dataSetID = getDataSetID()   
    vehicleIDs = getVehicleIDs(dataSetID)
    getDealerInfo(vehicleIDs,dataSetID)

main()
print("--- %s seconds ---" % (time.time() - start_time))


