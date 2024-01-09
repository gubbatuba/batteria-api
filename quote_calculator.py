from dateutil import parser
import datetime

"""
Quote Calculator gives the estimated price for a pickup order given a quote configuration
"""
class QuoteCalculator:
    def __init__(self, config):
        self.battery_model_MSRPs = config["batteryModelMSRPs"]
        self.battery_chemistry_cost_per_kWh = config["batteryChemistryCostPerkWh"]
        self.battery_props_weights = config["batteryPropsWeights"]
        self.chemistry_scores = {
            "LiFePO4": 1,
            "Li-ion": 1,
            "NiCd": 0.85,
            "NiMH": 0.95
        }
        self.battery_type_scores = {
            "EV": 1,
            "Home": 1,
            "BatteryBackup": 0.65,
        }
        self.condition_originally_purchased_scores = {
            "New": 1,
            "LikeNew": 0.9,
            "Used": 0.55,
        }

    # scoring the quality of the battery using the config weights
    def calculate_battery_score(self, battery):
        score = 0
        divisor = sum(self.battery_props_weights.values())
        for k, v in self.battery_props_weights.items():
            adjusted_weight = v/divisor
            raw_score = 0
            match k:
                case "chemistry":
                    raw_score = self.chemistry_scores[battery[k]]
                case "batteryType":
                    raw_score = self.battery_type_scores[battery[k]]
                case "weightLbs":
                    raw_score = (0.9 if battery[k] > 50 else 0.5)
                case "inputVoltage":
                    raw_score= (0.9 if battery[k] > 110 else 0.5)
                case "outputVoltage":
                    raw_score = (0.9 if battery[k] > 110 else 0.5)
                case "markedCapacitykWh":
                    raw_score = (0.9 if battery[k] > 50 else 0.5)
                case "approxLengthUsedDays":
                    raw_score = (0.9 if battery[k] < 2000 else 0.5)
                case "dateOriginallyPurchased":
                    raw_score = (0.9 if (datetime.datetime.now() - parser.parse(battery[k])).days < 1000 else 0.5)
                case "isFunctioning":
                    raw_score = (0.9 if battery[k] else 0.2)
                case "conditionOriginallyPurchased":
                    raw_score = (self.condition_originally_purchased_scores[battery[k]])
            score += (raw_score * adjusted_weight)
        return score
    
    # assigning a base price for the battery, then scaling it by the score above
    def calculate_battery_price(self, battery):
        battery_base_price = 0
        battery_model = battery["model"] or battery["vehicleModel"]
        battery_brand = battery["brand"] or battery["vehicleMake"]
        if battery_brand in self.battery_model_MSRPs and battery_model in self.battery_model_MSRPs[battery_brand]:
            battery_base_price = self.battery_model_MSRPs[battery_brand][battery_model]
        else:
            battery_base_price = self.battery_chemistry_cost_per_kWh[battery["chemistry"]] * battery["markedCapacitykWh"]
        battery_score = self.calculate_battery_score(battery)
        return battery_score * battery_base_price

    # sum all the batteries' prices for the given pickup order
    def final_quote_price(self, pickup):
        return sum([self.calculate_battery_price(b) for b in pickup["batteries"]])