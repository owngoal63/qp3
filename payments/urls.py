from django.urls import path

from . import views

urlpatterns = [
    path('charge/', views.charge, name='charge'),
    path('stripecheckout', views.HomePageView.as_view(), name='stripe_checkout'),
]