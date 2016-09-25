from django.conf.urls import url
from views import store, book_details, add_to_cart, remove_from_cart, cart

urlpatterns = [
    url(r'^$', store, name='index'),
    url(r'^book/(\d+)', book_details, name='book_details'),
    url(r'^add/(\d+)', add_to_cart, name='add_to_cart'),
    url(r'^remove/(\d+)', remove_from_cart, name='remove_from_cart'),
    url(r'^cart/', cart, name='cart'),
]