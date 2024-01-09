import requests
# NOTE: must run `python main.py` before running `python test.py`
BASE_URL = "http://127.0.0.1:5000/"

headers = {
    'Content-type':'application/json', 
    'Accept':'application/json'
}

print("Users............................................................")
print()

print("POST Request (w/ bad data, 400 Bad Request Expected)")
response = requests.post(BASE_URL + "user/" + str(2), 
json={
    "id": 2,
    "firstName": "Jason",
    "lastName": "Bourne",
    "businessName": "Quentin LLC",
    "address": "123 Grover Rd",
    "customerType": "Non-profit",
    "isActive": True,
    "email": "jb@qllc.com"
},
headers=headers)
print("POST Response:")
print(response.status_code, response.content)
print()

print("POST Request")
response = requests.post(BASE_URL + "user/" + str(2), 
json={
    "id": 2,
    "firstName": "Jason",
    "lastName": "Bourne",
    "businessName": "Quentin LLC",
    "address": "123 Grover Rd",
    "customerType": "Business",
    "isActive": True,
    "email": "jb@qllc.com"
},
headers=headers)
print("POST Response:")
print(response.status_code, response.content)
print()

print("GET Request")
response = requests.get(BASE_URL + "user/" + str(2))
print("GET Response")
print(response.status_code, response.content)
print()

print("PUT Request")
response = requests.put(BASE_URL + "user/" + str(2), 
json={
    "id": 2,
    "firstName": "Mason",
    "lastName": "Mourne",
    "businessName": "Mentin LLC",
    "address": "123 Mover Rd",
    "customerType": "Business",
    "isActive": True,
    "email": "mm@mllc.com"
},
headers=headers)
print("PUT Response")
print(response.status_code, response.content)
print()

print("DELETE Request")
response = requests.delete(BASE_URL + "user/" + str(2))
print("DELETE Response")
print(response.status_code, response.content)
print()

print("GET Request (missing case, expecting 404)")
response = requests.get(BASE_URL + "user/" + str(2))
print("GET Response")
print(response.status_code, response.content)
print()

print("Pickups............................................................")
print("POST Request")
response = requests.post(BASE_URL + "pickup/" + str(2), 
json={
        "id": 2,
        "ownerId": 1,
        "pickUpAddress": "123 Gravy Ln",
        "createdAt": "2021-01-01 23:26:08.712542",
        "batteries": [
            {   "chemistry": "LiFePO4",
                "batteryType": "Home",
                "ownerId": 1,
                "brand": "Tesla",
                "model": "PowerWall123",
                "vehicleMake": None,
                "vehicleModel": None,
                "weightLbs": 35,
                "inputVoltage": 240,
                "outputVoltage": 120,
                "markedCapacitykWh": 150,
                "approxLengthUsedDays": 200,
                "dateOriginallyPurchased": "2021-01-01 23:26:08.712542",
                "isFunctioning": True,
                "conditionOriginallyPurchased": "New",
                "comments": "It's dusty but it works fine"
            },
            {   "chemistry": "Li-ion",
                "batteryType": "EV",
                "ownerId": 1,
                "brand": None,
                "model": None,
                "vehicleMake": None,
                "vehicleModel": None,
                "weightLbs": 35,
                "inputVoltage": 120,
                "outputVoltage": 120,
                "markedCapacitykWh": 67,
                "approxLengthUsedDays": 35,
                "dateOriginallyPurchased": "2021-01-01 23:26:08.712542",
                "isFunctioning": True,
                "conditionOriginallyPurchased": "New",
                "comments": "It's dusty but it works fine"
            }
        ],
        "addressType": "Residential",
        "requestedPickupDate": "2021-01-01 23:26:08.712542",
        "comments": "Moving out of town and no longer need this"
    },
headers=headers)
print("POST Response")
print(response.status_code, response.content)
print()

print("GET Request")
response = requests.get(BASE_URL + "pickup/" + str(2)) 
print("GET Response")
print(response.status_code, response.content)
print()

print("Quotes............................................................")

print("GET Request")
response = requests.get(BASE_URL + "quote/" + str(2))
print("GET Response")
print(response.status_code, response.content)
print()

print("Agreements............................................................")

print("POST Request")
response = requests.post(BASE_URL + "agreement/" + str(2), 
json={
        "associatedQuoteId": 2,
        "agreedDate": "2021-01-01 23:26:08.712542",
        "paymentMethod": "Cash",
        "comments": "please only big bills"
    },
headers=headers)
print("POST Response")
print(response.status_code, response.content)
print()

print("GET Request")
response = requests.get(BASE_URL + "agreement/" + str(2)) 
print("GET Response")
print(response.status_code, response.content)
print()

print("Quote Configs............................................................")

print("POST Request")
response = requests.post(BASE_URL + "quoteConfig/" + str(2), 
json={
        "id": 2,
        "batteryModelMSRPs": {
            "Tesla": {
                "PowerWall123": 10000,
                "Mode456": 10000,
            },
            "SunCo": {
                "ACBC222": 9600
            }
        },
        "batteryChemistryCostPerkWh": {
            "LiFePO4": 149.0,
            "NiMH": 50.7,
            "NiCd": 170.3,
            "Li-ion": 100.3
        },
        "batteryPropsWeights": {
            "chemistry": 1,
            "batteryType": 1,
            "weightLbs": 1,
            "inputVoltage": 1,
            "outputVoltage": 1,
            "markedCapacitykWh": 1,
            "approxLengthUsedDays": 1,
            "dateOriginallyPurchased": 1,
            "isFunctioning": 1,
            "conditionOriginallyPurchased": 1
        }
    },
headers=headers)
print("POST Response")
print(response.status_code, response.content)
print()

print("GET Request")
response = requests.get(BASE_URL + "quoteConfig/" + str(2)) 
print("GET Response")
print(response.status_code, response.content)
print()