# Contains all Yelp queries.

import argparse
import json
import requests
import sys
import urllib

import re
import bs4
import random
import time

from . import apis

'''
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode
'''
YELP_KEY = apis.API_KEYS['yelp']
STAR_MIN = 4.0

def get_elites_restaurants(business_id, city, state, min_price=1.0, max_price=4.0):
    '''
    Get a master list (pre-filtered) of restaurants elites liked

    Inputs:
        business_id (str): business id
        cite (str): user's city
        state (str): user's state

    Return:
        (dict) pre-filtered restaurants
    '''
    if city.lower() == 'new york city':
        # corner case, since Yelp API uses New York instead of New York City
        city = 'new york'


    master_list = {}
    reviewers = find_elite(business_id, city, state)

    if reviewers == 'yelp_block':
        return 'yelp_block', None
    print (len(reviewers))

    elite_max = 0
    for reviewer_page in reviewers:
        restaurants = find_restaurants(reviewer_page, business_id, min_price, \
            max_price)
        for r in restaurants: 
            master_list[r] = master_list.get(r, 0) + 1
            if master_list[r] > elite_max:
                elite_max = master_list[r]
       #time.sleep(1) 
       #^attempt at getting around Yelp blocking, but blocking always came up
       # in the first query of the traversal. 

    return master_list, elite_max 


def find_restaurants(url, business_id, min_price, max_price):
    '''
    From the link to an elite reviewer page indexed by category="Restaurants",
    city=city inputted by user, and sorted by rating, return
    a list of the restaurants that are rated >= STAR_MIN and within the 
    specified price range.
    
    Input:
    url(str): link to elite reviewer's page with appropriate filters
    business_id(str): Yelp business id of user's favorite restaurant
    min_price(float): user's min price preference
    max_price(float): user's max price preference
    '''
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) \
    AppleWebKit/537.36(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}

    r = requests.get(url, headers=header)
    html = r.text
    soup = bs4.BeautifulSoup(html, "lxml")
    tag = soup.find_all("div", class_ = "review")
    
    if not tag:
        soup = try_new_header(url)
        if check_captcha(soup):
            return "yelp_block"
        tag = soup.find_all("div", class_ = "review")

    restaurants = filter_rest(tag, business_id, min_price, max_price)    
    return restaurants


def query_filter_restaurants(elite_rest, open_now=None):
    '''
    Given a dictionary of pre-filtered restaurants that elite reviewers liked,
    and the optional open_now preference, generates a dictionary of filtered
    restaurants

    Input:
        elite_rest (dict): dictionary of pre-filtered restaurants
        open_now (boolean): an optional argument if the user want the
        restaurants to be open onw

    Return:
        (dict) post-filter restaurants mapping business ID to 
         yelp restaurant dict
    '''

    filtered_list = {}

    for restaurant in elite_rest:
        rest_dict = get_business(restaurant)
        if open_now:
            if rest_dict.get('hours') is None or not rest_dict["hours"][0][
            "is_open_now"]:
                continue 

        rest_dict['elite_count'] = elite_rest[restaurant]
        filtered_list[restaurant] = rest_dict

    return filtered_list      


def request(path, url_params=None):
    '''
    Given your path, send a GET request to the API.
    Args:
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.

    Based on Yelp API example code. 
    '''

    url_params = url_params or {}
    api_host = 'https://api.yelp.com'
    url = '{0}{1}'.format(api_host, path)
    headers = {'Authorization': 'Bearer %s' % YELP_KEY,}

    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()


def yelp_search(term, city, state, search_limit=1, attributes=''):
    '''
    Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.

    Based on Yelp API example code. 
    '''

    url_params = {
        'term': term.replace(' ', '+'),
        'location': '+'.join((city,state)),
        'limit': search_limit,
        'attributes': attributes,
        'categories': 'restaurants'

    }
    search_path = '/v3/businesses/search'
    return request(search_path, url_params=url_params)


def get_business(business_id):
    '''
    Query the Yelp Business API by a business ID.
    Input:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.

    Based on Yelp API example code. 
    '''
    business_path = '/v3/businesses/'
    path = business_path + business_id
    rv = request(path)
    return rv


def star_count(tag):
    '''
    From a tag, return the star count for the review.

    Inputs:
        tag(tag object)
    Outputs:
        count(float)
    '''

    star = tag.find("div", class_ = "biz-rating biz-rating-large clearfix")
    star = star.find("div").find("div")
    star_count = star["title"]
    count = re.search(r"([\d.]+)", star_count)
    count = count.groups()[0]
    return float(count)


def find_elite(business_id, city, state):
    '''
    Take link of favorite restaurant inputted and
    find all elite reviewers that gave 4+ stars.

    Returns a set with the reviewers' respective user page link
    '''

    reviewers = set()
    url = 'http://www.yelp.com/biz/' + business_id + "?sort_by=elites_desc"
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) \
    AppleWebKit/537.36(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    request = requests.get(url, headers=header)
    html = request.text
    soup = bs4.BeautifulSoup(html, "lxml")
    tag_main = soup.find_all("div", class_ = "review review--with-sidebar")

    if not tag_main:
        soup = try_new_header(url)
        if check_captcha(soup):
            return "yelp_block"
        tag_main = soup.find_all("div", class_ = "review review--with-sidebar")    

    for tag in tag_main:
        if is_elite(tag):
            if star_count(tag) >= STAR_MIN:
                user_id, user_link = get_user(tag, city, state)
                reviewers.add(user_link)
    return reviewers


def get_restaurant_id(tag):
    '''
    Given a tag for a restaurant review on the page
    of an elite reviewer, find the restaurant id
    '''

    url = tag.find("a")['href']
    business_id = url.split('/biz/')[1]
    return business_id


def is_elite(tag):
    '''
    from a tag, return True if the user is elite
    '''

    elite = tag.find("a", href = "/elite")
    return elite


def get_user(tag, city, state):
    '''
    from a tag and user's city and state, return the user id and link to his page
    '''

    user = tag.find("a", class_ = "user-display-name js-analytics-click")
    user_id = re.search(r"=([\w\-]+)", user["href"])
    user_id = user_id.groups()[0]
    filter_str = "&review_sort=rating&review_filter=category&category_filter" +\
                    "=restaurants&review_filter=location" +\
                    "&location_filter_city={}&location_filter_state={}".format(\
                    city, state)
    user_link_head = "https://www.yelp.com/user_details_reviews_self?userid=" 
    user_link = user_link_head + user_id + filter_str

    return(user_id, user_link)


def filter_price(tag, min_price=1.0, max_price=4.0):
    '''
    Check if price falls between the user's price range
    '''

    price = tag.find("span", class_="business-attribute price-range")
    if not price:
        return True
    elif price:
        price = price.text
        if len(price) <= max_price and len(price) >= min_price:
            return True
    else:
        return False


def filter_rest(tag, business_id, min_price=1.0, max_price=4.0):
    '''
    Given a tag, business_id, and price range, return restaurants that are above
    4 stars and fall between the price range
    '''

    restaurants = set()
    for t in tag:
        restaurant_id = get_restaurant_id(t)
        if restaurant_id == business_id:
            continue
            
        stars = star_count(t)
        if stars >= STAR_MIN:
            price = filter_price(t, min_price, max_price)
            if not price:
                continue
            restaurants.add(restaurant_id)

    return restaurants


def check_captcha(soup):
    '''
    Checks to see if Yelp has thrown a captcha verification, and if
    so, returns True.

    Inputs:
        soup (bs4 object)
    Outputs:
        Boolean
    '''
    tag_main = soup.find_all("div", id = "content")
    for tag in tag_main:
        if "Hey there! Before you continue, we just need \
                    to check that you're not a robot." in tag.text:
            return True
    else:
        return False


def try_new_header(url):
    '''
    If a request is blocked by Yelp, then tries a new User Agent
    header to make the request with. This solution attempt is based off a
    suggestion on Piazza. 

    Inputs:
    url(str): url of blocked request

    Returns:
    Soup of html of second request attempt
    '''
    header = {'User-Agent': 
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'}
    request = requests.get(url, headers=header)
    html = request.text
    soup = bs4.BeautifulSoup(html, "lxml")

    return soup

