from django.conf.urls import url
from views import store, book_details

urlpatterns = [
    url(r'^$', store, name='index'),
    url(r'^book/(\d+)', book_details, name='book_details')
]