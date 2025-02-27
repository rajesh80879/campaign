from django.urls import path
from .views import campaign_wizard, campaign_dashboard, campaign_redirect
from django.shortcuts import redirect

urlpatterns = [
    path("campaign/", campaign_redirect, name="my_campaign"),
    path("campaign/step/<int:step>/", campaign_wizard, name="campaign_wizard"),
    path("campaign/dashboard/", campaign_dashboard, name="campaign_dashboard"),
]


