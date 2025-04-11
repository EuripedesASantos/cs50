from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:any>", views.index_any, name="index_any"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("categories/", views.all_categories, name="categories"),
    path("categories/<str:categ>", views.categories, name="categories"),
    path("bid/", views.bid, name="bid"),
    path("listing/new", views.listing_new, name="new_listing"),
    path("sell/", views.sell, name="sell"),
    path("sold/", views.sold, name="sold"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("watchlist/add", views.watch_add, name="watch_add"),
    path("comment/", views.comment, name="comment"),
    path("buys/", views.buys, name="buys")
]
