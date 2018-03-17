# sudo pip3 install --upgrade django-crispy-forms
import os
import csv

from django import forms
from django.core.validators import EMPTY_VALUES
from . import main

RES_DIR = os.path.join(os.path.dirname(__file__), 'csv')
RANGE_WIDGET = forms.widgets.MultiWidget(widgets=(forms.widgets.NumberInput,
                                                  forms.widgets.NumberInput))

# Drop down functions modified from PA3 code
class IntegerRange(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (forms.IntegerField(),
                  forms.IntegerField())
        super(IntegerRange, self).__init__(fields=fields,
                                           *args, **kwargs)

    def compress(self, data_list):
        if data_list and (data_list[0] is None or data_list[1] is None):
            raise forms.ValidationError('Must specify both lower and upper '
                                        'bound, or leave both blank.')
        return data_list


def _load_column(filename, col=0):
    """Load single column from csv file."""
    with open(filename) as f:
        col = sorted(list(zip(*csv.reader(f)))[0])
        return list(col)


def _load_res_column(filename, col=0):
    """Load column from resource directory."""
    return _load_column(os.path.join(RES_DIR, filename), col=col)


def _build_dropdown(options):
    """Convert a list to (value, caption) tuples."""
    return [(x, x) for x in options]


STATE_CHOICES = _build_dropdown(_load_res_column('states.csv'))
CUISINE_CHOICES = _build_dropdown(_load_res_column('cuisines.csv'))


class PriceRange(IntegerRange):
    def compress(self, data_list):
        super(PriceRange, self).compress(data_list)
        for v in data_list:
            if not 1 <= v <= 4:
                raise forms.ValidationError(
                    'Bounds must be in the range 1 to 4.')
        if data_list and (data_list[1] < data_list[0]):
            raise forms.ValidationError(
                'Lower bound must not exceed upper bound.')
        return data_list


class InputForm(forms.Form):
    ad_choices=[("high","Extremely!"), ("medium", "Pretty adventurous"), \
        ("low", "Kind of...")]

    # random = forms.BooleanField(label='Give me something random!', \
    #     required=False)
    restaurant = forms.CharField\
        (label='What is your favorite restaurant? (e.g. MingHin)', \
        max_length=100, required=True)
    cuisine = forms.CharField\
        (label='What is this restaurant\'s cuisine? (e.g. Chinese)', \
        widget=forms.Select(choices=CUISINE_CHOICES), required=True)
    city = forms.CharField(label='What is your city?', max_length=100, required=True)
    state = forms.CharField(label='What is your state?', \
        widget=forms.Select(choices=STATE_CHOICES), required=True)
    adventure = forms.ChoiceField(label='How adventurous are you feeling today?', \
        choices=ad_choices, widget=forms.RadioSelect(), required=True)
    price_min_max = PriceRange(
        label='Price Range - No. of $ signs (lower/upper, 1-4)',
        help_text='e.g. 1 and 4',
        widget=RANGE_WIDGET,
        required=False)
    open_now = forms.BooleanField(label='Open Now', required=False)

    def clean(self):
        random = self.cleaned_data.get('random', False)
        restaurant = self.cleaned_data.get("restaurant", None)
        cuisine = self.cleaned_data.get("cuisine", None)
        city = self.cleaned_data.get("city", None)
        state = self.cleaned_data.get("state", None)
        adventure = self.cleaned_data.get("adventure", None)

        if restaurant and city and state:
            business_id = main.get_fav_id(restaurant, city, state)

            if business_id is None:
                raise forms.ValidationError(
                    "No such restaurant - try making your input more specific, or" \
                    " try another name."
                )

        return self.cleaned_data

class RandInputForm(forms.Form):
    city = forms.CharField(label='City', max_length=100, required=True)
    state = forms.CharField(label='State', \
        widget=forms.Select(choices=STATE_CHOICES), required=True)




