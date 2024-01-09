from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse, abort
import datetime
from jsonschema import validate, ValidationError
from quote_calculator import QuoteCalculator

app = Flask(__name__)
api = Api(app)

# Validation
users_create_args = reqparse.RequestParser()
users_create_args.add_argument("firstName", type=str, required=True, help="First name of User")
users_create_args.add_argument("lastName", type=str, required=True, help="Last name of User")
users_create_args.add_argument("businessName", type=str, help="Name of Associated Business")
users_create_args.add_argument("address", type=str, required=True, help="Address of User/Business")
users_create_args.add_argument("customerType", type=str, required=True, choices=('Residential', 'Business'), help="Residential or Business Customer")
users_create_args.add_argument("email", type=str, required=True, help="Email of User for contact or logging in")

pickups_create_args = reqparse.RequestParser()
pickups_create_args.add_argument("ownerId", type=int, required=True, help="Battery Owner Id (User Id)")
pickups_create_args.add_argument("pickUpAddress", type=str, required=True, help="Address of User/Business")
pickups_create_args.add_argument("batteries", type=list, location="json", required=True, help="List of batteries for pickup")
pickups_create_args.add_argument("addressType", type=str, required=True, choices=('Residential', 'Business'), help="Residential or Business Address")
pickups_create_args.add_argument("requestedPickupDate", type=str, required=True, help="Date requested by user for pickup")
pickups_create_args.add_argument("comments", type=str, required=False, help="Optional additional comments")

batterySchema = {
    "type": "object",
    "properties": {
        "chemistry": {"enum" : ["LiFePO4", "Li-ion", "NiCd", "NiMH"]},
        "batteryType": {"enum" : ["EV", "Home", "BatteryBackup"]},
        "ownerId": {"type": "integer"},
        "brand": {"type": ["string", "null"]},
        "model": {"type": ["string", "null"]},
        "vehicleMake": {"type": ["string", "null"]},
        "vehicleModel": {"type": ["string", "null"]},
        "weightLbs": {"type": "number"},
        "inputVoltage": {"type": "integer"},
        "outputVoltage": {"type": "integer"},
        "markedCapacitykWh": {"type": "number"},
        "approxLengthUsedDays": {"type": "integer"},
        "dateOriginallyPurchased": {"type": "string"},
        "isFunctioning": {"type": "boolean"},
        "conditionOriginallyPurchased": {"enum" : ["New", "LikeNew", "Used"]},
        "comments": {"type": "string"},
    },
    "required": ["chemistry",
        "batteryType",
        "ownerId",
        "brand",
        "model",
        "vehicleMake",
        "vehicleModel",
        "weightLbs",
        "inputVoltage",
        "outputVoltage",
        "markedCapacitykWh",
        "approxLengthUsedDays",
        "dateOriginallyPurchased",
        "isFunctioning",
        "conditionOriginallyPurchased"
        ],
    "additionalProperties": False
}

agreements_create_args = reqparse.RequestParser()
agreements_create_args.add_argument("associatedQuoteId", type=int, required=True, help="Id of Quote associated with this agreement")
agreements_create_args.add_argument("agreedDate", type=str, required=True, help="Date user agreed to this quote")
agreements_create_args.add_argument("paymentMethod", type=str, required=True, choices=('Check', 'GiftCard', 'Cash', "Crypto"), help="How the user would like to be paid (Cash, Check, Crypto, or Gift Card)")
agreements_create_args.add_argument("comments", type=str, required=False, help="Optional additional comments")

quote_config_create_args = reqparse.RequestParser()
quote_config_create_args.add_argument("batteryModelMSRPs", type=dict, required=True, help="MSRP values for known battery makes and models")
quote_config_create_args.add_argument("batteryChemistryCostPerkWh", type=dict, required=True, help="Costs per kilowatt-hour for given battery chemistries")
quote_config_create_args.add_argument("batteryPropsWeights", type=dict, required=True, help="Weighting for calculating quality score of a battery")

batteryPropsWeightsSchema = {
    "type": "object",
    "properties": {
        "chemistry": {"type": "number"},
        "batteryType": {"type": "number"},
        "weightLbs": {"type": "number"},
        "inputVoltage": {"type": "number"},
        "outputVoltage": {"type": "number"},
        "markedCapacitykWh": {"type": "number"},
        "approxLengthUsedDays": {"type": "number"},
        "dateOriginallyPurchased": {"type": "number"},
        "isFunctioning": {"type": "number"},
        "conditionOriginallyPurchased": {"type": "number"}
    },
    "required": ["chemistry",
        "batteryType",
        "weightLbs",
        "inputVoltage",
        "outputVoltage",
        "markedCapacitykWh",
        "approxLengthUsedDays",
        "dateOriginallyPurchased",
        "isFunctioning",
        "conditionOriginallyPurchased"
        ],
    "additionalProperties": False
}

# Repositories (in lieu of Databases)

users = {
    1: {
            "id": 1,
            "firstName": "John",
            "lastName": "Doe",
            "createdAt": "2021-01-01 23:26:08.712542",
            "updatedAt": "2021-01-01 23:26:08.712542",
            "businessName": None,
            "address": "123 Gravy Ln",
            "customerType": "Residential",
            "isActive": True,
            "email": "johndoe@gmail.com"
    }
}

pickups = {
    1: {
        "id": 1,
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
            }
        ],
        "addressType": "Residential",
        "requestedPickupDate": "2021-01-01 23:26:08.712542",
        "comments": "Moving out of town and no longer need this"
    }
}
quotes = {
    1: {
        "id": 1,
        "quotePrice": 10000,
        "quoteIssuedDate": "2021-01-01 23:26:08.712542",
        "quoteExpiryDate": "2021-02-01 23:26:08.712542",
        "sellerId": 1,
        "associatedPickupId": 1,
        "isApproved": True
    }
}

agreements = {
    1: {
        "id": 1,
        "associatedQuoteId": 1,
        "agreedDate": "2021-01-01 23:26:08.712542",
        "paymentMethod": "Cash",
        "comments": "please only big bills",
        "createdAt": "2021-01-01 23:26:08.712542",
        "updatedAt": "2021-01-01 23:26:08.712542"
    }
}

quote_configs = {
    1: {
        "id": 1,
        "batteryModelMSRPs": {
            "Tesla": {
                "PowerWall123": 10000,
                "Mode456": 10000,
            }
        },
        "batteryChemistryCostPerkWh": {
            "LiFePO4": 170.0,
            "NiMH": 90.7,
            "NiCd": 140.3,
            "Li-ion": 57.3
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
    }
}

# helper functions

def abort_if_entity_not_found(id, repository, entity_name):
    if id not in repository:
        abort(404, message=f"{entity_name} id not found")

def abort_if_entity_exists(id, repository, entity_name):
    if id in repository:
        abort(409, message=f"{entity_name} with that id already exists")

def generate_quote(pickup):
    now = datetime.datetime.now().isoformat()
    new_quote = {
        "id": next_id(quotes),
        "quotePrice": QuoteCalculator(quote_configs[max(quote_configs.keys())]).final_quote_price(pickup),
        "quoteIssuedDate": now,
        "quoteExpiryDate": now,
        "sellerId": pickup["ownerId"],
        "associatedPickupId": pickup["id"],
        "isApproved": False
    }
    return new_quote

def next_id(repository):
    return max(repository.keys()) + 1

'''
Pickup resource defines details of the battery pickup
'''    
class Pickup(Resource):
    entity_name = "Pickup"

    def get(self, pickup_id):
        abort_if_entity_not_found(pickup_id, pickups, self.entity_name)
        return pickups[pickup_id]
    
    # batteries are separately validated due to limitations with reqparse
    def post(self, pickup_id):
        abort_if_entity_exists(pickup_id, pickups, self.entity_name)
        args = pickups_create_args.parse_args()
        for i in args["batteries"]:
            try:
                validate(i, batterySchema)
            except ValidationError as e:
                return f"One or more batteries had validation errors: {e}", 400
        
        new_pickup = args.copy()
        now = datetime.datetime.now().isoformat()
        new_pickup["id"] = next_id(pickups)
        new_pickup["createdAt"] = now
        new_pickup["updatedAt"] = now

        pickups[pickup_id] = new_pickup

        new_quote = generate_quote(new_pickup)
        quotes[new_quote["id"]] = new_quote
        return pickups[pickup_id], 201

'''
User resource defines the seller/owner of the battery who is requesting a quote
'''    
class User(Resource):
    entity_name = "User"

    # user is created if it does not exist, or updated if it does using PUT
    def create(self, user_id):
        args = users_create_args.parse_args()
        now = datetime.datetime.now().isoformat()
        new_user = args.copy()
        new_user["id"] = next_id(users)
        new_user["createdAt"] = now
        new_user["updatedAt"] = now
        new_user["isActive"] = True

        users[user_id] = new_user
        return users[user_id], 201

    def get(self, user_id):
        abort_if_entity_not_found(user_id, users, self.entity_name)
        user = users[user_id]
        if user["isActive"]:
            return users[user_id]
        else:
            return 'User is deactived', 404
    
    def post(self, user_id):
        abort_if_entity_exists(user_id, users, self.entity_name)
        return self.create(user_id)

    def put(self, user_id):
        if user_id not in users:
            self.create(self, user_id)
        else:
            args = users_create_args.parse_args()
            now = datetime.datetime.now().isoformat()
            update_user = args.copy()
            old_user = users[user_id]
            old_user["updatedAt"] = now
            old_user["firstName"] = update_user["firstName"]
            old_user["lastName"] = update_user["lastName"]
            old_user["businessName"] = update_user["businessName"]
            old_user["address"] = update_user["address"]
            old_user["customerType"] = update_user["customerType"]
            old_user["email"] = update_user["email"]
            users[user_id] = old_user
            return users[user_id], 201
    
    # soft deleting only, in case user deletion was done by mistake
    def delete(self, user_id):
        abort_if_entity_not_found(user_id, users, self.entity_name)
        users[user_id]["isActive"] = False
        return '', 204

'''
Quote resource defines the quote calculated for the customer based on the pickup details
'''    
class Quote(Resource):
    entity_name = "Quote"

    # quotes can only be read via this resource, they are automatically generated
    # on the server side when a pickup order is POSTed
    def get(self, quote_id):
        abort_if_entity_not_found(quote_id, quotes, self.entity_name)
        return quotes[quote_id]

'''
Agreement resource defines acceptance of the provided quote for the user
'''    
class Agreement(Resource):
    entity_name = "Agreement"

    def get(self, agreement_id):
        abort_if_entity_not_found(agreement_id, agreements, self.entity_name)
        agreement = agreements[agreement_id]
        agreement["associatedQuote"] = quotes[agreement["associatedQuoteId"]]
        return agreement
    
    def post(self, agreement_id):
        abort_if_entity_exists(agreement_id, agreements, self.entity_name)
        args = agreements_create_args.parse_args()

        new_agreement = args.copy()
        now = datetime.datetime.now().isoformat()
        new_agreement["id"] = next_id(agreements)
        new_agreement["createdAt"] = now
        new_agreement["updatedAt"] = now

        agreements[agreement_id] = new_agreement

        # we mark the associated quote as approved
        quotes[new_agreement["associatedQuoteId"]]["isApproved"] = True

        return agreements[agreement_id], 201


class QuoteConfig(Resource):
    entity_name = "QuoteConfig"

    def get(self, config_id):
        abort_if_entity_not_found(config_id, quote_configs, self.entity_name)
        return quote_configs[config_id]
    
    # battery weights are separately validated due to limitations with reqparse
    def post(self, config_id):
        abort_if_entity_exists(config_id, quote_configs, self.entity_name)
        args = quote_config_create_args.parse_args()

        try:
            validate(args["batteryPropsWeights"], batteryPropsWeightsSchema)
        except ValidationError as e:
            return f"One or more batteries had validation errors: {e}", 400

        new_config = args.copy()
        now = datetime.datetime.now().isoformat()
        new_config["id"] = next_id(quote_configs)
        new_config["createdAt"] = now
        new_config["updatedAt"] = now

        quote_configs[config_id] = new_config
        return quote_configs[config_id], 201

api.add_resource(Pickup, "/pickup/<int:pickup_id>")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(Quote, "/quote/<int:quote_id>")
api.add_resource(Agreement, "/agreement/<int:agreement_id>")
api.add_resource(QuoteConfig, "/quoteConfig/<int:config_id>")

if __name__ == "__main__":
    app.run(debug=True)