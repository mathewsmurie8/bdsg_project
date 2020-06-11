from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='donations'),
    path('register_donation_center', views.register_donation_center, name='register_donation_center'),
    path('centers', views.centers, name='centers'),
]
