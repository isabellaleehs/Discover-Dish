# Contains main computations to get top 3 recommendations, and randomizer computations.

#sudo pip3 install geoplotlib
#sudo pip3 install pyglet==1.2.4
#sudo pip3 install beautifulsoup4

import csv
import json
import geoplotlib
import bs4
import re
import random
import requests
import time

from . import yelp
from . import apis


HALF_EARTH_CIRCUMF = 12451

def get_fav_id(favorite, city, state):
    '''
    favorite(str): user's text input for their favorite restaurant 
    city(str): user's input for city
    state(str): 2 letter code for user's state
    
    returns: business id from result of Yelp Search API
    '''

    search = yelp.yelp_search(favorite, city, state)

    if search['businesses'] != []:
        return search['businesses'][0]['id']
    return None


def get_recommendations(business_id, city, state, cuisine_1, adventure, 
    min_price=1.0, max_price=4.0, open_now=None):
    '''
    Returns sorted list of recommendations for a user given a fav restaurant,
    location, cuisine type, and adventure level, with optional filters for
    price and open now. 

    Inputs:
    business_id(str): yelp business id for user's favorite restaurant
    city(str)
    state(str): two letter state code
    cuisine_1(str): cuisine type of favorite restaurant
    adventure(str): how much weight will be put on cuisine distance for
      calculating rankings
    min_price / max_price(float)
    open_now(bool)

    '''    

    print ('Getting elites restaurants')
    elite_rest, elite_max = yelp.get_elites_restaurants(business_id, city, 
        state, min_price, max_price)

    if elite_rest == "yelp_block":
        return "yelp_block"
    print ('num elite rest:', len(elite_rest))

    if elite_rest == {}:
        return "empty_error" # throws error if user's inputs are too narrow

    print ('querying yelp and filtering')

    filtered = yelp.query_filter_restaurants(elite_rest, open_now=open_now)
    print ('num post filter:', len(filtered))
    if filtered == {}:
        return "empty_error"
    
    print ('calculating')
    recs = calculate(adventure, business_id, filtered, elite_max, cuisine_1)
    visualize(recs)
    return recs


def calculate(adventure, business_id, filtered, elite_max, cuisine_1):
    '''
    Given the adventurous level the user wants, and the list of
    restaurants generated from the elite reviewers, the function
    calculates and ranks the recommendations.

    Inputs: 
    adventurous: (string) "low", "medium", "high"
    business_id: (string) the user's favorite restaurant (id)
    filtered (dict): a dictionary of post-filter recommendations
    elite_max (integer): the maximum number of elite reviewers who 
        likes the restaurant in elite_rest list
    min_price: (integer)(optional) from 1 to 4
    max_price: (integer)(optional) from 1 to 4

    Return:
    (list) a sorted list of up to 3 dictionaries with attributes from yelp
    
    '''
    if adventure == "high":
        a = 50
    elif adventure == "medium":
        a = 40
    else:
        a = 30
    b = (100 - a - 40) * 2 / 3
    c = (100 - a - 40) / 3

    rv = {}

    for key in filtered:
        d = filtered[key]
        if "categories" in d.keys() and d["categories"] is not None:
            cuisine_2 = d["categories"][0]["title"]
        else:
            continue 

        dist = apis.get_distance(cuisine_1, cuisine_2)
        if dist is None or dist == 0:
            continue

        rating = d.get('rating')
        review_count = d.get('review_count')
        if review_count <= 49:
            review_score = 1 / 3
        elif review_count >= 200:
            review_score = 1
        else:
            review_score = 2 / 3

        score = (a * dist / HALF_EARTH_CIRCUMF) + \
            (40 * d['elite_count'] / elite_max) + \
            (b * rating / 5) + (c * review_score)

        open_now = d.get('hours', "No hours info provided")
        if type(open_now) is not str:
            open_now = open_now[0].get('is_open_now')
        coordinates2 = apis.CUISINE_COORDINATES[cuisine_2]
        address = ', '.join(d['location']['display_address'])
        address_coordinates = (d['coordinates']['latitude'], \
                                            d['coordinates']['longitude'])
        open_table = apis.find_opentable_link(d['location']['zip_code'], \
            d['phone'], address, address_coordinates)

        rv[key] = {'cuisine': cuisine_2, 'name': d.get('name'), 'dist': dist, \
        'rating': rating, 'review_count': review_count, 'open_now': open_now,\
          'price': d.get('price'), 'elite_count': d['elite_count'],\
           'coordinates': coordinates2, 'address': address, \
            'open_table_link': open_table, 'score': score} 

    if len(rv.keys()) == 1:
        key = list(rv.keys())[0]
        rv[key]['score'] = 100
        return rv

    rv_sorted = sorted(rv.items(), key=lambda t: t[1]['score'], reverse=True)
    final_rv = get_top_three(rv_sorted)
    
    return final_rv


def get_top_three(rv_sorted):
    '''
    Pick the top three recommendations from different areas
    from the sorted list of restaurants
    '''

    count = 0
    loc_unique = []
    final_rv = []

    for tup in rv_sorted:
        c = tup[1]['coordinates']
        if c not in loc_unique:
            loc_unique.append(c)
            final_rv.append(tup)
            count += 1
        if count == 3:
            break

    return final_rv 


def visualize(recs):
    '''
    Takes the direct output from calculation, maps the 3 recommendations
    based on their cuisine locations
    '''

    if recs != []:
        rv = []
        for idx, tup in enumerate(recs):
            lat, lon = tup[1]['coordinates']
            rv.append(["#" + str(idx + 1) + ". " + tup[1]['name'] + \
                            " (" + tup[1]['cuisine'] + ")", lat, lon])
    
        header = ['name', 'lat', 'lon']
        with open("form/static_files/img/visualization.csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([h for h in header])
            writer.writerows(rv)

        data = geoplotlib.utils.read_csv("form/static_files/img/visualization.csv")
        geoplotlib.dot(data)
        geoplotlib.labels(data, 'name', color=[0, 0, 255, 255], font_size=10, \
                                                         anchor_x='center')
        geoplotlib.savefig("form/static_files/img/visualization")


'''
Randomizer
'''

def randomizer(city, state): 
    '''
    First using the user's location, find a highly search ranked
    Hot and New restaurant using the Yelp API.

    Inputs:
        city(str)
        state(str)

    Outputs:
        rest_dict(Yelp API dict)

    '''
    hot_rest = yelp.yelp_search('', city, state, search_limit=50, 
        attributes='hot_and_new')['businesses']
    random.shuffle(hot_rest)

    index = 0
    flag = True

    while flag:
        business_id = hot_rest[index]['id']
        rest_dict = yelp.get_business(business_id)
        if 'categories' not in rest_dict.keys():
            continue

        if rest_dict['categories'][0]['title'] in apis.CUISINE_COORDINATES.keys():
            flag = False
        index += 1

    return rest_dict


def take_random_listing(url):
    '''
    Takes a query into yelp and gets business id of one of the first 
    listing shown on the page.

    Inputs:
        url(str)

    Outputs:
        business_id(str)
    '''
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) \
    AppleWebKit/537.36(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    
    r = requests.get(url, headers=header)
    html = r.text
    soup = bs4.BeautifulSoup(html, "lxml")
    tag_main = soup.find_all("a", class_ = "biz-name js-analytics-click")

    if not tag_main:
        soup = yelp.try_new_header(url)
        if yelp.check_captcha(soup):
            return "yelp_block"
        tag_main = soup.find_all("a", class_ = "biz-name js-analytics-click")

    if not tag_main:
        # possible if specified cuisine has no hot&new restaurants
        return None

    random.shuffle(tag_main)
    for tag in tag_main:
        url = tag["href"]
        if "adredir" not in url:
            business_id = re.search(r"/biz/([\w-]+)", url)
            business_id = business_id.groups()[0]
            rest_dict = yelp.get_business(business_id)
            if rest_dict['categories'] is not None:
                cuisine = rest_dict['categories'][0]['title']
                if cuisine in apis.CUISINE_COORDINATES.keys():
                    return business_id


def response_to_randomizer(response, business_id, city, state):
    '''
    Given the user's randomizer option (1,2,or 3), business name and id, 
    user's city and state, return recommendations.

    Inputs:
        response(int)
        business_id(str)
        city(str)
        state(str)

    Outputs:
        rest_2_dict, return_rest (dict)
    '''  
    rest_dict = yelp.get_business(business_id)
    cat_dict = rest_dict["categories"][0]
    cuisine_1 = cat_dict["title"]
    cuisines_list = list(apis.CUISINE_COORDINATES.keys())

    if response == 1:   
        '''
        "I like it but I want something else." 
        Inserts initially shown restaurant into the main traversal route. 
        From the list of restaurants that elite reviewers similarly liked, 
        find the one that is least distance (ethnically) from the initial.
        ''' 
        elite_rest, elite_max =  yelp.get_elites_restaurants(business_id, 
            city, state)

        if elite_rest == {}:
            # If input restaurant has not been reviewed by elites, then 
            # will return another random restaurant.
            return randomizer(city, state)

        if elite_rest == "yelp_block":
            return "yelp_block"

        restaurants = yelp.query_filter_restaurants(elite_rest)
        least_dist = float("inf")
        return_rest = None

        for rest, rest_2_dict in restaurants.items():
            if rest == business_id or rest_2_dict.get('categories') is None:        
                continue 

            cuisine_2 = rest_2_dict["categories"][0]["title"]
            if cuisine_2 in cuisines_list:
                if cuisine_1 == cuisine_2:
                    return rest_2_dict
                else:                
                    dist = apis.get_distance(cuisine_1, cuisine_2)
                    if rest_2_dict.get('location') is not None:
                        if dist < least_dist:
                            least_dist = dist
                            return_rest = rest_2_dict

        return return_rest

    if response == 2:
        cuisines_list = list(apis.CUISINE_COORDINATES.keys())
        '''
        "I don't like this, give me something else." 
        Pick a random cuisine type from a list and check to see if it is
        far away enough distance-wise from the cuisine type of the initial
        restaurant. Then, use that cuisine type to query into Yelp to find
        a Hot and New Business of that cuisine type in the user's area.
        '''
        random.shuffle(cuisines_list)
        index_max = len(apis.CUISINE_COORDINATES) - 1 
        city_url = city.replace(" ", "+")

        for cuisine_2 in cuisines_list:    
            if cuisine_1 == cuisine_2:
                continue

            if apis.get_distance(cuisine_1, cuisine_2) > 2680: #Width of North America
                cuisine_2 = cuisine_2.replace("/","%2F").replace(" ", "+")   
                query = "https://www.yelp.com/search?" + \
                        "find_desc={}&find_loc={}+{}&attrs=NewBusiness".format(
                            cuisine_2, city_url, state) 
                business_id = take_random_listing(query)
                time.sleep(0.5)
                if not business_id:
                    continue
                rest_2_dict = yelp.get_business(business_id)
                return rest_2_dict

