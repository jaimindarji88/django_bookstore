from django.conf.urls import url
from views import store

urlpatterns = [
    url(r'^$', store, name='index'),
]