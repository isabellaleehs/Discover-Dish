# Functions using the googlemaps api to search for locations, and opentable.

import sys
import urllib
import json
from difflib import SequenceMatcher

import re
import geopy
from geopy.distance import vincenty

API_KEYS = json.load(open('form/api_keys.json'))
CUISINE_COORDINATES = json.load(open('form/cuisine_coordinates.json'))


'''
Google
'''

def get_coordinates(address, country=False):
    '''
    Given an address (can be a country), return its geographical coordinates.
    If input is a country, then must be the country's two-letter code. 

    Input:
        address (str): address
        country (boolean): an optional argument if the address is a country
    Return:
        tuple: the latitude and longitude of the address
    '''

    address_url = address.replace(" ", "+")

    if country:
        country_url = "&components=country:" + address
        address_url += country_url

    endpoint = 'https://maps.googleapis.com/maps/api/geocode/json?address='

    url = endpoint + address_url + "&key=" + API_KEYS['google_maps']
    html = urllib.request.urlopen(url).read()

    d = json.loads(html.decode("utf-8"))

    coordinates = d['results'][0]['geometry']['location']
    lat = coordinates['lat']
    lng = coordinates['lng']

    return (lat, lng)


def get_distance(cuisine_1, cuisine_2):
    '''
    Computes geographic Earth distance between the country of origins of 
    two cuisines.

    Inputs:
    cuisine_1: (str) cuisine of a restaurant (must be in Yelp cuisine dict)
    cuisine_2: (str) cuisine of a restaurant (must be in Yelp cuisine dict) 

    Outputs:
    (int) geographic distance between countries of two cuisines or
    None if cuisine type is not valid.
    '''
    coordinates1 = CUISINE_COORDINATES.get(cuisine_1)
    if coordinates1 is None:
        return None
    coordinates2 = CUISINE_COORDINATES.get(cuisine_2)
    if coordinates2 is None:
        return None
    distance = vincenty(coordinates1, coordinates2).miles
    return round(distance)

'''
Open table
'''

def find_opentable_link(zip, phone, address, coordinates):
    '''
    Given a restaurant's location and phone information, this function finds 
    the link to the restaurant's Open Table page if such a page exists. Uses 
    an unofficial open Open Table API. Restaurant info for these parameters
    are taken from the Yelp API. 

    Inputs:
    zip(str): zip code of restaurant
    phone(str): phone number of restaurant
    address(str): display address of restaurant 
    coordinates(tuple of floats): coordinates of restaurant address

    Output:
    (str) link to restaurant's Open Table, or None if an Open Table does
    not exist. 
    '''
    lat, lng = coordinates
    main_phone = re.sub("[^0-9]", "", phone)[-10:]
    endpoint = 'http://opentable.herokuapp.com/api'

    # while loop checks all pages of OpenTable API if necessary
    page = 1
    entries = 1
    link = None

    while link is None and entries > 100 * (page - 1):
        url = endpoint + '/restaurants?per_page=100&page={}&zip={}&'.\
        format(page, zip)
        html = urllib.request.urlopen(url).read()
        s = str(html).strip("\\'")[2:]
        d = json.loads(html.decode("utf-8"))
        link = check_opentable_restaurants(d, main_phone, address, lat, lng)
        entries = d['total_entries']
        page += 1

    return link
    

def check_opentable_restaurants(opentable_d, phone, address, lat, lng):
    '''
    Checks the dictionary of restaurants that match the restaurant of 
    interest's zip code given by Open Table to find the restaurant of interest's
    Open Table link. First checks the restaurant of interest's phone number w/
    Open Table, and then the restaurant's location in case the phone numbers
    in Yelp or Open Table are not updated. To minimize calls of the Google Maps
    API, we first check if the address strings in Yelp and Open Table approx.
    match, and then we check if the coordinates of the addresses match to a 
    certain degree.

    Input:
    opentable_d(dict): dictionary of OpenTable restaurants whose zip codes match
      that of the restaurant of interest. 
    phone(str): 10 digit phone number (only numerical characters) of restaurant
      of interest
    address(str): display address of restaurant
    lat(float): latitude of restaurant of interest
    lng(float): longitude of restaurant of interest

    Returns:
    (str) link to restaurant's OpenTable page or None if page does not exist.
    '''
    for restaurant in opentable_d['restaurants']:
        r_phone = restaurant['phone']
        c_phone = re.sub("[^0-9]", "", r_phone)

        if c_phone == phone:
            return restaurant['reserve_url']

        r_address = restaurant['address']
        ratio = SequenceMatcher(None, address, r_address).ratio()

        if ratio < 0.9:
            continue

        c_lat, c_lng = get_coordinates(r_address + ", " + zip)

        if abs(c_lat - lat) < 0.0005 and abs(c_lng - lng) < 0.0005:
            return restaurant['reserve_url']

    return None

