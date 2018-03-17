from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_list, name='get_list'),
    path('form/results.html', views.get_list, name='get_list_1'),
    path('form/rand.html', views.rand, name='rand'),
    path('form/rand_form.html', views.rand_form, name='rand_form')
]