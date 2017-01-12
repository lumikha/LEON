from django.conf.urls import url
from appLEON import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajax/ini_scrape/$', views.ini_scrape, name='ini_scrape'),
]
