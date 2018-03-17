# Creates cuisine coordinates JSON file based on dictionary of all possible Yelp 
# cuisines, by mapping each cuisine to a country.

from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from . import apis
import json


def create_cuisine_coordinates_dict(cuisine_country_dict):

    cuisine_coordinates = {}
    for cuisine, country in cuisine_country_dict.items(): 
        coordinates = apis.get_coordinates(country, country=True)
        cuisine_coordinates[cuisine] = coordinates

    with open('cuisine_coordinates.json', 'w') as f:
        json.dump(cuisine_coordinates, f, indent=1)


# List of yelp restaurant categories: Restaurants (restaurants)
cuisine_to_country = {
"Afghan": "AF",
"African": "CF",
"Senegalese": "SN",
"South African": "ZA",
"American (New)": "US",
"American (Traditional)": "US",
"Arabian": "SA",
"Argentine": "AR",
"Armenian": "AM", 
"Asian Fusion": "CN",
"Australian": "AU", 
"Austrian": "AT", 
"Bangladeshi": "BD", 
# "Barbeque" 
"Basque": "ES",
"Belgian": "BE", 
"Brasseries": "FR", 
"Brazilian": "BR", 
# "Breakfast & Brunch"
"British": "GB",
# "Buffets" 
"Bulgarian": "BG", 
"Burgers": "US", 
"Burmese": "MM", 
# "Cafes" 
# "Themed Cafes"
# "Cafeteria"
"Cajun/Creole": "US",
"Cambodian": "KH",
"Caribbean": "DO", # Dominican Republic, geographic middle
"Dominican": "DO", 
"Haitian": "HT", 
"Puerto Rican": "PR", 
"Trinidadian": "TT", 
"Catalan": "ES", 
"Cheesesteaks": "US", 
# "Chicken Shop" 
"Chicken Wings": "US", 
"Chinese": "CN", 
"Cantonese": "CN", 
"Dim Sum": "HK", 
"Hainan": "CN", 
"Shanghainese": "CN",  
"Szechuan": "CN",
# "Comfort Food" 
"Creperies": "FR",
"Cuban": "CU", 
"Czech": "CZ", 
# "Delis" 
"Diners": "US",
# "Dinner Theater" 
"Ethiopian": "ET", 
"Fast Food": "US", 
"Filipino": "PH", 
"Fish & Chips": "GB", 
"Fondue": "CH",
# "Food Court" 
# "Food Stands" 
"French": "FR", 
"Mauritius": "MU", 
"Reunion": "RE", 
# "Game Meat" 
# "Gastropubs" 
"Georgian": "US", 
"German": "DE", 
# "Gluten-Free" 
"Greek": "GR", 
"Guamanian": "GU", 
"Halal": "SA", 
"Hawaiian": "US",
"Himalayan/Nepalese": "NP",
"Honduran": "HN",
"Hong Kong Style Cafe": "HK",
"Hot Dogs": "US",
"Hot Pot": "CN",
"Hungarian": "HU", 
"Iberian": "ES",
"Indian": "IN", 
"Indonesian": "ID", 
"Irish": "IE", 
"Italian": "IT", 
"Calabrian": "IT", 
"Sardinian": "IT", 
"Sicilian": "IT", 
"Tuscan": "IT", 
"Japanese": "JP",
"Conveyor Belt Sushi": "JP", 
"Izakaya": "JP", 
"Japanese Curry": "JP", 
"Ramen": "JP",
"Teppanyaki": "JP", 
"Kebab": "SA", 
"Korean": "KR", 
# "Kosher"
"Laotian": "LA",
"Latin American": "BR", 
"Colombian": "CO", 
"Salvadoran": "SV", 
"Venezuelan": "VE",
# "Live/Raw Food" 
"Malaysian": "MY", 
"Mediterranean": "IT",
"Falafel": "EG", 
"Mexican": "MX", 
"Tacos": "MX", 
"Middle Eastern": "SA",
"Egyptian": "EG", 
"Lebanese": "LB", 
#"Modern European" 
"Mongolian": "MN", 
"Moroccan": "MA", 
"New Mexican Cuisine": "US", 
"Nicaraguan": "NI",
"Noodles": "CN",
"Pakistani": "PK", 
"Pan Asian": "CN",
"Persian/Iranian": "IR", 
"Peruvian": "PE", 
"Pizza": "IT",
"Polish": "PL", 
"Polynesian": "US", 
# "Pop-Up Restaurants" 
"Portuguese": "PT", 
"Poutineries": "CA", 
"Russian": "RU", 
# "Salad"
# "Sandwiches" 
"Scandinavian": "SE",
"Scottish": "GB", 
# "Seafood" 
"Singaporean": "SG", 
"Slovakian": "SK", 
"Soul Food": "US", 
# "Soup"
"Southern": "US",
"Spanish": "ES", 
"Sri Lankan": "LK", 
"Steakhouses": "US", 
# "Supper Clubs" 
"Sushi Bars": "JP", 
"Syrian": "SY", 
"Taiwanese": "TW", 
"Tapas Bars": "ES",
"Tapas/Small Plates": "ES", 
"Tex-Mex": "MX", 
"Thai": "TH", 
"Turkish": "TR", 
"Ukrainian": "UA", 
"Uzbek": "UZ", 
# "Vegan" 
# "Vegetarian" 
"Vietnamese": "VN", 
"Waffles": "US", 
# "Wraps" 
}



