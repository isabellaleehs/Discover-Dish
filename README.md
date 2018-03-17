# Discover Dish

Discover Dish is a web application that aims to make trying *new* cuisines less intimidating for users by providing more personalized restaurant recommendations using collaborative filtering. The app outputs recommendations that the user is likely to enjoy, while also ensuring a minimum cultural distance from the user's input restaurant
to allow the user to experience new cuisines.

Discover Dish also introduces users to new cuisines through popular restaurants through a fun, interactive recommendation randomizer. 

## --Installation--
Discover Dish requires:
* [pyglet 1.2.4](https://bitbucket.org/pyglet/pyglet/wiki/Download)
	**note:** in order for pyglet to work with ipython on Mac, version 1.2.4 or newer is needed
* [geoplotlib](https://github.com/andrea-cuttone/geoplotlib)
* [beautifulsoup4 4.4.0](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [django-crispy-forms](http://django-crispy-forms.readthedocs.io/en/latest/)

Just run ```python3 manage.py runserver``` to open Django on your browzer.

Note: If running on OS X, you might have to also install ```lxml``` by running ```pip3 install lxml```.

## --How it works--
Users input their preferences into a form, which then scrapes Yelp for the restaurant's elite reviewers, scrapes elite reviewer profiles, and ranks all the restaurants highly reviewed by elite reviewers according to an algorithm. Our application relies on collaborative filtering to make personalized recommendations for users; we look for elite reviewers who liked the user's favorite restaurant, and look at the other restaurants the elites liked to make recommendations to the user. 

The scoring algorithm takes into account your adventure level, cuisine dissimilarity (proxied by the distance between cuisine origins), number of elite reviewers who liked the restaurant, star rating, and review count to compute the top 3 restaurant recommendations, which are then given to the user, along with a map of where the cuisines originate from.

Our randomizer uses a similar algorithm, except you have different options. For a randomly picked Hot & New restaurant from Yelp, the user can choose to like it but want another recommendation. The algorithm will look at the list of restaurants that elite reviewers similarly liked, and find one restaurant whose cuisine type is the most similar to the initial one. Alternatively, if the user does not like the initial restaurant, the program will then randomly pick a cuisine type that is not similar to the initial restaurant, and query into Yelp to find a Hot & New restaurant of that cuisine type in the area the user specifies.

NOTE: if you run into an error trying to run the program, this is likely because
Yelp has blocked you. We have tried changing the User Agent in the request header,
adding time.sleep between calls, and different packages such as urllib and requests, but the problem still seems to occasionally persist.

NOTE: for the main submission page, it may take around a minute to run due to the amount of webscraping necessary. 

----------DESCRIPTION OF FILES----------

main.py:
	This file features the functions that put together the backend of the program.
	get_recommendations() is the main traversal route that takes in the user's inputs
	and returns the final recommendations to be displayed.
	get_calculate() is the helper function that ranks a list of restaurants and gives
	a score to each restaurant.
	visualize() allows for the map that shows the final recommended restaurants
	at their corresponding cuisine type to be displayed on Django. 
	The file also has the functions that make up our Randomization feature.

cuisines.py
	This file contains the code that creates cuisine_coordinates.json, which is the 
	dictionary that maps cuisine types to latitude and longitude coordinates.

apis.py
	This file contains the code for the Open Table API and Google Maps API.

yelp.py
	This file contains the code that scrapes Yelp for information regarding
	restaurant listings on search pages or elite reviewer pages. It
	also contains the code using the Yelp API, and recognizes if 
	Yelp throws us a captcha error.

api_keys.json:
	Contains the Yelp and Google Maps API keys.

cuisine_coordinates.json:
	Contains a dictionary mapping cuisine types to the longitude and latitude.


Team: Lilly Guo, Sunny Mei, Victoria Xie, Isabella Lee

## Copyright and License (Bootstrap CSS)

Copyright 2013-2017 Blackrock Digital LLC. Code released under the [MIT](https://github.com/BlackrockDigital/startbootstrap-round-about/blob/gh-pages/LICENSE) license.
