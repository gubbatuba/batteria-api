# batteria-api
Batteria: Redwood Materials Battery Buying Marketplace (Backend Service)


### Rationale

- to test, first run `python main.py` and then `python test.py`

- Didn't use a database because in-memory was enough, no need to persist data between app restart. In the future would be nice to implement a AWS cdk and link to a graph or relational database.

- Pickups had capability to have multiple batteries (list of batteries)

- Quote calculator configuration was a series of known supported battery brands and models with prices, and adjustable weights for battery price estimation. Hard rules were also coded into the calculator itself. In there future would be nice to make those configurable in the document as well

- Used flask and python so this project could be light weight and deployable as a microservice.

- everything is contained in 2 files, but in the future would be better to break it up into more classes and folders, "Models", "Validators", "Resources" for example

- it is easy to add props and more batteries, classes, types, etc.

### Draft Schema (changes were made during actual implementation)
User
    id: int
    firstName: string
    lastName: string
    createdAt: date
    updatedAt: date
    businessName: string
    address: string
    customerType: [residential/business]
    isActive: bool
    email: string

pickUp
    id: int
    ownerId: int
    address: string
    batteries: list[battery]
    addressType: [residential/business]
    requestedPickupDate: date
    comments: string


battery
    chemisty: [LiFePO4/Li-ion/NiCd/NiMH]
    batteryType: [EV/Home/BatteryBackup]
    ownerId: int
    brand: string
    model: string
    vehicleMake: string
    vehicleModel: string
    weightLbs: int
    inputVoltage: float
    outputVoltage: float
    markedCapacitykWh: float
    approxLengthUsedDays: int
    dateOriginallyPurchased: date
    isFunctioning: bool
    conditionOriginallyPurchased: [Used/New/LikeNew]
    comments: string

quote
    id: int
    quotePrice: float
    quoteIssuedDate: date
    quoteExpiryDate: date
    sellerId: int
    associatedPickupId: int
    isApproved: bool

agreements
    id: int
    associatedQuote: int
    agreedDate: date
    paymentMethod: [Check/GiftCard/Cash]
    comments: string

quotePricingConfig
    {
        "batteryModelMSRPs": {
            "Tesla": {
                "Model123": 10000,
                "Mode456": 10000,...
            }...
        }
        "batteryChemistryCostPerkWh": {
            "LiFePO4": 10.0,
            "NiMH": 9.7,
            "NiCd": 4.3,...
        }
        "batteryPropsWeights": {
            "inputVoltage": 1,
            "outputVoltage": 1,
            "markedCapacitykWh": 1,
            "approxLengthUsedDays": 1,
            "dateOriginallyPurchased": 1,
            "isFunctioning": 1,
            "conditionOriginallyPurchased": 1
        }
    }