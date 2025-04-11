from django.contrib import admin
from .models import User, AuctionListing, Bid, Comment, Sale, Watchlist

class UserAdmin(admin.ModelAdmin):
    # fields: make simple layout changes in the forms on the “add” and “change” pages
    list_display = ("username", "first_name", "last_name", "email")
    list_display_links = ["username"]
    fields = ["username", "first_name", "last_name", "email", "password"]


class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ("seller", "title", "description", "start_bid", "category", "sold")
    # list_select_related = ("title")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "comment")

class BidAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "value")

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "active")

class SaleAdmin(admin.ModelAdmin):
    list_display = ( "buyer", "listing")

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Watchlist, WatchlistAdmin)

