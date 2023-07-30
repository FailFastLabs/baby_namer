from . import views

from django.urls import path

from django.views.generic.base import TemplateView

urlpatterns = [
    path('', views.popular_names_view, name='index'),
    path('girls.html', views.popular_names_view, {'gender': 'girls'}, name='girls'),
    path('boys.html', views.popular_names_view, {'gender': 'boys'}, name='boys'),
    path('bot.html', views.popular_names_view, name='bot'),
    path('search/', views.search, name='search'),
    path('stats/', views.stats, name='stats'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('copyright/', TemplateView.as_view(template_name="app/copyright.html"), name='copyright'),
    path('<str:baby_name>/', views.baby_name_detail, name='baby_name_detail'),

]
