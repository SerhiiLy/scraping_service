from django.urls import path
from .views import home_view

app_name = 'scraping'

urlpatterns = [
    path('home/', home_view,)
]