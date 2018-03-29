# Note: Depending on Python environment, some packages may need to be installed such as requests and grequests (ex. pip install <package_name>)

import json, requests, urllib, grequests, pprint, time

start_time = time.time()

# Get random dataSetID
def getDataSetID():
    dataSetIDurl = "http://vautointerview.azurewebsites.net/api/datasetId"
    dataSetIDResponse = requests.get(dataSetIDurl) # Send request and get response
    dataSetIDJSON = dataSetIDResponse.json() # Store reponse in json object
    dataSetID = dataSetIDJSON['datasetId'] # Extract value and assign to variable
    # print "DataSetID is: " + dataSetID
    return dataSetID

# Get Vehicle IDs associated with dataSetID
def getVehicleIDs(ID):
    dataSetID = ID
    vehicleIDurl = "http://vautointerview.azurewebsites.net/api/" + dataSetID + "/vehicles"
    vehicleIDResponse = requests.get(vehicleIDurl) # Send request and get response
    vehicleIDJSON = vehicleIDResponse.json() # Store reponse in json object
    vehicleIDList = json.loads(json.dumps(vehicleIDJSON)) #Convert JSON object to Python list
    return vehicleIDList

def getResponse(vehicleIDs,dataSetID):

    # Get Vehicle Information
    vehicleINFOurls=[]  
    for id in vehicleIDs['vehicleIds']:        
        vehicleINFOurl = "http://vautointerview.azurewebsites.net/api/" + dataSetID +"/vehicles/" + str(id)
        vehicleINFOurls.append(vehicleINFOurl) # Build URL list to send simultaneous requests
    vehicleINFORequests = (grequests.get(u) for u in vehicleINFOurls) # Send URL requests simultaneously
    vehicleINFOResponses = grequests.map(vehicleINFORequests) # Build responses returned
    vehicleINFOjson = [vehicleINFOResponse.json() for vehicleINFOResponse in vehicleINFOResponses] # Store responses in JSON format
    vehicleINFOList = json.loads(json.dumps(vehicleINFOjson)) # Convert JSON responses to Python list

    # Get Dealer IDs
    dealerIDs=[]
    for vehicleINFO in vehicleINFOList:    # Iterate through vehicle information list     
        dealerID = vehicleINFO["dealerId"] # Extract Dealer ID and assign to variable
        dealerIDs.append(dealerID) # Build list of dealer ids
    dealerIDs = set(dealerIDs)  # Create unique list to avoid duplicates

    # Get Dealer information based on Dealer IDs
    dealerINFOurls=[]
    for dealerID in dealerIDs:
        dealerINFOurl = "http://vautointerview.azurewebsites.net/api/" + dataSetID + "/dealers/" + str(dealerID)
        dealerINFOurls.append(dealerINFOurl) # Build URL list to send simultaneous requests
    dealerINFORequests = (grequests.get(u) for u in dealerINFOurls) # Send url requests simultaneously
    dealerINFOResponses = grequests.map(dealerINFORequests) # Build responses returned
    dealerINFOjson = [dealerINFOResponse.json() for dealerINFOResponse in dealerINFOResponses ] # Store json response
    dealerINFOList = json.loads(json.dumps(dealerINFOjson)) # Convert JSON responses to Python list

    # Assign number of dealers to integer for looping
    dealers_count = len(dealerINFOList)       
    
    # Build JSON answer
    json_message = "{\"dealers\":["
    for dealerINFO in dealerINFOList: # Iterate through Dealer information
        vehicles_count = 0 # Set/reset vehicles counter
        json_message += "{\"dealerId\":\"" + str(dealerINFO["dealerId"]) + "\",\"name\":\"" + str(dealerINFO["name"]) + "\", \"vehicles\":["
        for vehicleINFO in vehicleINFOList: # Iterate through Vehicle information for each dealer
            if vehicleINFO["dealerId"] == dealerINFO["dealerId"]:
                vehicles_count += 1 # Add to Dealer vehicles count if dealerIDs match
                #print "vehicles counter: " , vehicles_count
        for vehicleINFO in vehicleINFOList: # Again iterate through Vehicle information for each dealer with vehicle count set
            if vehicleINFO["dealerId"] == dealerINFO["dealerId"] and vehicles_count > 1: # Add this string to JSON if dealerIDs match and not the last vehicle
                #print "vehicles counter inside match loop: " , vehicles_count
                json_message += "{\"vehicleId\":" + str(vehicleINFO["vehicleId"]) + ",\"year\":" + str(vehicleINFO["year"]) + ",\"make\":\"" + vehicleINFO["make"] + "\",\"model\":\"" + vehicleINFO["model"] + "\"},"
                vehicles_count -= 1 # Subtract vehicle count by one for next iteration
            elif vehicleINFO["dealerId"] == dealerINFO["dealerId"] and vehicles_count == 1: # BUT add this string to JSON if dealerIDs match and we're at the last vehicle
                json_message += "{\"vehicleId\":" + str(vehicleINFO["vehicleId"]) + ",\"year\":" + str(vehicleINFO["year"]) + ",\"make\":\"" + vehicleINFO["make"] + "\",\"model\":\"" + vehicleINFO["model"] + "\"}]"
        if dealers_count > 1: # Unless last dealer iteration, use this string
            json_message += "},"
        else: # Last dealer iteration, so use this string
            json_message += "}]"
        #print "dealers counter: " , dealers_count        
        dealers_count -= 1               
                
    json_message += "}" # JSON fully built
    #print json_message
    json_answer = json.loads(json_message) # Prep the JSON
    answer_url = "http://vautointerview.azurewebsites.net/api/" + dataSetID + "/answer" # Set answer URL
    #print answer_url
    answer_response = requests.post(answer_url, json=json_answer) # POST the answer and return the response
    print answer_response.text # Response printed to the user

def main():
    dataSetID = getDataSetID() # Pull a random dataSetID
    vehicleIDs = getVehicleIDs(dataSetID) # Get list of vehicle IDs based on the random dataSetID and assign to a variable
    getResponse(vehicleIDs,dataSetID) # Pass and use the vehicle IDs and datasetID to build a request and get a response

main()
print("--- %s seconds ---" % (time.time() - start_time))


