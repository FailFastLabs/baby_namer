from django.urls import path
from . import views

urlpatterns = [
    # ... your other url patterns ...

    path('<str:baby_name>/', views.baby_name_detail, name='baby_name_detail'),
]