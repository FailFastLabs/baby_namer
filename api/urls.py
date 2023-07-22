from django.urls import path
from .views import favorite_baby_name

urlpatterns = [
    path('favorite/', favorite_baby_name, name='favorite_baby_name'),
]
