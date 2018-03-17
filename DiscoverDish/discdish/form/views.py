from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from io import BytesIO
import base64
from form.forms import InputForm
from form.forms import RandInputForm

# files
from . import main

def get_list(request):
    # If this is a POST request we need to process the form data
    if request.method == 'GET':
        # Create a form instance and populate it with data from the request:
        form = InputForm(request.GET) 

        if 'rand_form' in request.GET:
            return HttpResponseRedirect(reverse('rand_form'))

        # Check whether it's valid:
        if form.is_valid():
            restaurant = form.cleaned_data['restaurant']
            cuisine = form.cleaned_data['cuisine']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            adventure = form.cleaned_data['adventure']
            price = form.cleaned_data['price_min_max']
            if price:   
                price_min = price[0]
                price_max = price[1]
            else:
                price_min = 1.0
                price_max = 4.0
            open_now = form.cleaned_data['open_now']

            business_id = main.get_fav_id(restaurant, city, state)
            top_restaurants = main.get_recommendations(business_id, city, \
                state, cuisine, adventure, price_min, price_max, open_now)
            
            if top_restaurants == "yelp_block":
                return HttpResponseNotFound\
                    ('<h4>Your server is currently being blocked by Yelp.'\
                    ' Try again in a few hours.</h4>')

            elif top_restaurants == "empty_error":
                return HttpResponseNotFound\
                    ('<h4>Sorry! We couldn\'t find any recommendations for you'\
                        ' based on your inputs. Try adjusting your filters or'\
                        ' entering a different favorite restaurant.</h4>')

            else:
                c = {'results': top_restaurants}
                return render(request, 'form/results.html', c)

        return render(request,'form/index.html', {'form': form})

    # If a POST (or any other method) we'll create a blank form
    else:
        form = InputForm()

    return render(request,'form/index.html', {'form': form})


def rand_form(request):
    # If this is a POST request we need to process the form data
    if request.method == 'GET':
        # Create a form instance and populate it with data from the request:
        form = RandInputForm(request.GET) 

        if form.is_valid():
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']

            details = main.randomizer(city, state)

            # Store to session
            request.session['business_id'] = details['id']
            request.session['city'] = details['location']['city']
            request.session['state'] = details['location']['state']
            request.session['rand'] = [details['id']]

            # Check specifically that hours are provided
            if details['hours'] != []:
                hours = details['hours'][0]['is_open_now']
            else:
                hours = 'No hours info provided'

            c = {'name': details['name'], \
                'cuisine': details['categories'][0]['title'], \
                'location': ' '.join(details['location']['display_address']), \
                'rating': details.get('rating'), 'price': details.get('price'), \
                'open_now': hours}
            return render(request, 'form/rand.html', c)

        return render(request,'form/rand_form.html', {'form': form})

    # If a POST (or any other method) we'll create a blank form
    else:
        form = RandInputForm()

    return render(request,'form/rand_form.html', {'form': form})

        
def rand(request):
    if request.method == 'GET':
        # Extract from session
        business_id = request.session['business_id']
        city = request.session['city']
        state = request.session['state']
        ids = request.session['rand'] # keep track of all previous results

        response = 0
        if 'like' in request.GET:
            response = 1
        elif 'dislike' in request.GET:
            response = 2

        # If there is a response like or dislike
        if response > 0:
            details = main.response_to_randomizer(response, business_id, city,\
                state)

            if details == "yelp_block":
                return HttpResponseNotFound\
                    ('<h1>Your server is currently being blocked by Yelp.'\
                    ' Try again in a few hours.</h1>')

            else:
                while details['id'] in ids:
                    details = main.response_to_randomizer(response, business_id, \
                        city, state)
                else:
                    ids.append(details['id'])
                    request.session['rand'] = ids

                # Store to session
                request.session['business_id'] = details['id']
                request.session['city'] = details['location']['city']
                request.session['state'] = details['location']['state']

                if details.get('hours'):
                    hours = details['hours'][0]['is_open_now']
                else:
                    hours = 'No hours info provided'

                c = {'name': details['name'], \
                    'cuisine': details['categories'][0]['title'], \
                    'location': ' '.join(details['location']['display_address']), \
                    'rating': details.get('rating'), \
                    'price': details.get('price'), \
                    'open_now': hours}

            return render(request, 'form/rand.html', c)
        else:
            return HttpResponseRedirect(reverse('get_list'))

    # If a POST (or any other method), return to home page
    else:
        return render(request,'form/index.html', {'form': form})

