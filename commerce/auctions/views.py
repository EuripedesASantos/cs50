import logging

from django.template.defaultfilters import register

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.forms.utils import flatatt
from django.utils.html import escape
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import User, AuctionListing, Bid, Watchlist, Comment, Sale
from django import forms

from django.db.models import Max
from django.db.models import Count

# Required to import make_password
from django.contrib.auth.hashers import make_password


@register.simple_tag
def update_variable(listing, watching_list):
    """Allows to update existing variable in template"""
    value = True

    # Check if listing or watching_list is None
    if not watching_list:
        return True
    elif not listing:
        return False

    for item in watching_list:
        if listing == item.listing:
            value = False
            break

    return value

# Get id of the logged user
def get_user_id(request):
    if request.user.is_authenticated:
        return User.objects.filter(username=request.user.username).values()[0]["id"]
    else:
        logging.info("User not authenticated")
        return None

# Get all watching infos
def get_watching_info(request) -> tuple:
    watching_list = None
    watch_num = None

    if request.user.is_authenticated:
        watching_list = Watchlist.objects.filter(user=request.user, active=True)
        if watching_list:
            watch_num = len(watching_list)

    return watching_list, watch_num

# Get number of comments for each listing
def get_count_comment_by_listing(request):
    if request.user.is_authenticated:
        return Comment.objects.values('user').annotate(count=Count('listing'))
    else:
        logging.info("User not authenticated")
        return None

def index_id(request, listing_id):
    return HttpResponseRedirect(reverse('index'))

def get_active_listings() -> AuctionListing:
    return AuctionListing.objects.filter(sold=False)

def get_sold_list_(request):
    sold_list = []
    try:
        solds = AuctionListing.objects.filter(sold=True, seller=request.user)
        if solds:
            for sold in solds:
                sold_list.append({
                    'listing': sold,
                    'buyer'  : Sale.objects.get(listing=sold).buyer})
    except Exception as e:
        logging.info(f"<get_sold_list> raise exception: {e}")
        return None

    return sold_list

def get_sold_list(request):

    sold_list = None
    if request.user.is_authenticated:
        solds = AuctionListing.objects.filter(sold=True, seller=request.user)
        if solds:
            sold_list = []
            for sold in solds:
                sold_list.append({
                    'listing': sold,
                    'buyer'  : Sale.objects.get(listing=sold).buyer})

    return sold_list

def get_buys_list(request):
    if not request.user.is_authenticated:
        return None

    buys_list = None
    sales_list = Sale.objects.all()
    if sales_list:
        for sales_item in sales_list:
            if sales_item.buyer.user == request.user:
                if not buys_list:
                    buys_list = []
                buys_list.append(sales_item)

    return buys_list

def get_all_data(request):
    watching_list, watch_num = get_watching_info(request)
    active_listings = get_active_listings()
    return {
        'comments': Comment.objects.all(),
        'active_listings': active_listings,
        'watching_list': watching_list,
        'watch_num': watch_num,
        'bid_list': get_bid_info(active_listings),
        'sold_list': get_sold_list(request),
        'buys_list': get_buys_list(request)}

def index(request, **kwargs):
    all_info = get_all_data(request)
    return render(request, "auctions/index.html", {
        "title": "Auctions",
        "page_name": "Active Listings",
        "active_listings": all_info['active_listings'],
        "sold_list": all_info['sold_list'],
        "watching_list": all_info['watching_list'],
        "watch_num": all_info['watch_num'],
        "bid_list": all_info['bid_list'],
        "comments": all_info['comments'],
        "buys_list": all_info['buys_list']
    })


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/index.html", {
                "page_name": "Login",
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/index.html", {"page_name": "Login"})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

class RegisterForm(forms.Form):
    username = forms.CharField(label="", widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Username", "autofocus":""}))
    first_name = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"First name"}))
    last_name = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Last name"}))
    email = forms.EmailField(label="", required=False, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Email address"}))
    password = forms.CharField(label="", widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Password"}))
    confirmation = forms.CharField(label="", widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Confirm Password"}))



def register(request):
    # Check if method is POST
    if request.method == "POST":
        # Receives the user registration data sent to register the user
        form = RegisterForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            username = request.POST["username"]
            email = request.POST["email"]
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]

            # Ensure password matches confirmation
            password = request.POST["password"]
            confirmation = request.POST["confirmation"]
            if password != confirmation:
                return render(request, "auctions/index.html", {
                    "page_name": "Register",
                    "message": "Passwords must match.",
                    "form": form
                })

            # Attempt to create new user
            try:
                user = User(username=username, email=email, password=make_password(password), first_name=first_name, last_name=last_name)
                user.save()
            except IntegrityError:
                return render(request, "auctions/index.html", {
                    "page_name": "Register",
                    "message": f"<{username}> Username already taken.",
                    "form": form
                })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/index.html", {
                "page_name": "Register",
                "message": "Invalid data",
                "form": form
            })
    else:
        return render(request, "auctions/index.html",{
            "page_name": "Register",
            "form": RegisterForm})

class InputMy(forms.TextInput):
    def __init__(self, attrs={}, message=""):
        super().__init__()
        self.attrs = attrs
        self.message = message

    def render(self, name, value, attrs, **kwargs):
        attrs.update(self.attrs)
        attrs = self.build_attrs(attrs)
        if not value:
            text = '<input %s name="%s">' % (flatatt(attrs), name)
        else:
            text = '<input %s value="%s" name="%s">' % (flatatt(attrs), escape(value), name)
        return mark_safe(f'{text}<label class="label_rigth">{self.message}</label>')

class TextareaMy(forms.Textarea):
    def __init__(self, attrs={}, message=""):
        super().__init__()
        self.attrs = attrs
        self.message = message

    def render(self, name, value, attrs, **kwargs):
        attrs.update(self.attrs)
        attrs = self.build_attrs(attrs)
        if not value:
            text = '<textarea %s name="%s"></textarea>' % (flatatt(attrs), name)
        else:
            text = '<textarea %s name="%s">%s</textarea>' % (flatatt(attrs), escape(value), name)
        return mark_safe(f'{text}<label class="label_rigth">{self.message}</label>')

class ListingForm(forms.Form):
    title = forms.CharField(widget=InputMy(message="Title for the listing.", attrs={"type": "text"}))

    description = forms.CharField(widget=TextareaMy(message="Description for the listing.", attrs={'rows': 3}))
    start_bid = forms.FloatField(widget=InputMy(message="Starting bid"))
    img_url = forms.URLField(label="URL to image*:", required=False, widget=InputMy(message="OPTIONAL: a URL for an image for the listing."))
    category = forms.CharField(label="Category*:", required=False, widget=InputMy(message="OPTIONAL: a category (e.g. Fashion, Toys, Electronics, Home, etc)."))

def listing_new(request):
    if not request.user.is_authenticated:
        return render(request, "auctions/login.html",
                      {"message":mark_safe("<p>Login needed for create new listing!</p>")})
    if request.method == "POST":
        form = ListingForm(request.POST)

        if form.is_valid():
            new_isting = AuctionListing(
                seller=request.user,
                title = form.cleaned_data["title"],
                description = form.cleaned_data["description"],
                start_bid = float(form.cleaned_data["start_bid"]),
                img_url = form.cleaned_data["img_url"],
                category = form.cleaned_data["category"]
                )
            new_isting.save()
            return HttpResponseRedirect(reverse("index"))
        else:

            all_info = get_all_data(request)
            return render(request, "auctions/index.html", {
                "page_name": "Create listing",
                "action_url": reverse("new_listing"),
                "message": "Error creating a new listing: invalida data!",
                "form": form,
                "button_text": "Save new listing",
                "active_listings": all_info['active_listings'],
                "sold_list": all_info['sold_list'],
                "watching_list": all_info['watching_list'],
                "watch_num": all_info['watch_num'],
                "bid_list": all_info['bid_list'],
                "comments": all_info['comments'],
                "buys_list": all_info['buys_list']
            })
    else:
        all_info = get_all_data(request)
        return render(request, "auctions/index.html", {
                    "page_name": "Create listing",
                    "action_url": reverse("new_listing"),
                    "message": "Creating a new listing!",
                    "form": ListingForm(),
                    "button_text": "Save new listing",
                    "active_listings": all_info['active_listings'],
                    "sold_list": all_info['sold_list'],
                    "watching_list": all_info['watching_list'],
                    "watch_num": all_info['watch_num'],
                    "bid_list": all_info['bid_list'],
                    "comments": all_info['comments'],
                    "buys_list": all_info['buys_list']
                })


def categories(request, categ: str):
    if categ == "":

        all_info = get_all_data(request)
        return render(request, "auctions/index.html", {
            "title": "Category",
            "page_name": "Category List",
            "category_list": AuctionListing.objects.order_by().values("category").distinct(),
            "active_listings": all_info['active_listings'],
            "sold_list": all_info['sold_list'],
            "watching_list": all_info['watching_list'],
            "watch_num": all_info['watch_num'],
            "bid_list": all_info['bid_list'],
            "comments": all_info['comments'],
            "buys_list": all_info['buys_list']
        })
    else:
        all_info = get_all_data(request)
        return render(request, "auctions/index.html", {
            "title": "Category",
            "page_name": "Category List",
            "category": categ,
            "active_listings": AuctionListing.objects.filter(category=categ),
            "sold_list": all_info['sold_list'],
            "watching_list": all_info['watching_list'],
            "watch_num": all_info['watch_num'],
            "bid_list": all_info['bid_list'],
            "comments": all_info['comments'],
            "buys_list": all_info['buys_list']
        })


class WatchlistForm(forms.Form):
    watchlist_id = forms.IntegerField(widget=forms.HiddenInput())

def watchlist(request):
    message = ""
    # Get number of Whatchlist
    watch_num = 0
    if not request.user.is_authenticated:
        logging.info("User not authenticated")
        return HttpResponseRedirect(reverse("index"))

    # Check if method is POST
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = WatchlistForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():
            # Identify Watchlist item to remove
            watchlist_id = form.cleaned_data["watchlist_id"]

            # Get Watchlist item to remove
            watch = Watchlist.objects.get(id=watchlist_id)
            watch.active = False
            watch.save()
            logging.info(f"Removed id <{watchlist_id}> from Watchlist")
        else:
            message = "Error: Watchlist item not found!"

    all_info = get_all_data(request)
    return render(request, "auctions/index.html", {
        "title": "Watching",
        "page_name": "Watching List",
        "active_listings": all_info['active_listings'],
        "watching_list": all_info['watching_list'],
        "watch_num": all_info['watch_num'],
        "watching": True,
        "sold_list": all_info['sold_list'],
        "bid_list": all_info['bid_list'],
        "comments": all_info['comments'],
        "buys_list": all_info['buys_list'],
        "message": message
    })

class BidForm(forms.Form):
    listing_id = forms.IntegerField(widget=forms.HiddenInput())
    new_bid = forms.FloatField()

# get max bid value maked by users and min value for bids
def get_bid_info(auction_listing: list) -> tuple:
    bid_list = None
    ret_unic = False

    if auction_listing:
        if isinstance(auction_listing,AuctionListing):
            auction_listing = [auction_listing]
            ret_unic =True
        for listing in auction_listing:
            bids = Bid.objects.filter(listing=listing)
            if bids:
                max_bid_value = bids.aggregate(Max('value'))['value__max']
                bid_max = Bid.objects.filter(listing=listing, value=max_bid_value).first()

                if not bid_list:
                    bid_list = []

                bid_list.append({
                    "listing": listing,
                    "bid_max": bid_max,
                    "num_of_bids": len(bid_list)})
            else:
                if not bid_list:
                    bid_list = []
                bid_list.append({
                    "listing": listing,
                    "bid_max": None,
                    "num_of_bids": None})

        if ret_unic:
            return bid_list[0]
        else:
            return bid_list

def bid(request):
    if not request.user.is_authenticated:
        logging.info("User not authenticated")
        return HttpResponseRedirect(reverse("index"))

    # Check if method is POST
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = BidForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the bid from the 'cleaned' version of form data
            new_bid = Bid( user=request.user,
                           value=form.cleaned_data["new_bid"],
                           listing_id=form.cleaned_data["listing_id"])
            new_bid.save()

    return HttpResponseRedirect(reverse("index"))

def all_categories(request):
    return categories(request, "")

class SellForm(forms.Form):
    listing_id = forms.IntegerField(widget=forms.HiddenInput())

def sell(request):
    if request.user.is_authenticated:
        # Check if method is POST
        if request.method == "POST":
            # Take in the data the user submitted and save it as form
            form = SellForm(request.POST)

            # Check if form data is valid (server-side)
            if form.is_valid():
                listing_id = form.cleaned_data['listing_id']
                # Validade listing_id
                listing = AuctionListing.objects.get(id=listing_id)
                if not listing:
                    logging.info(f"User: {request.user.username} tried to sell item id={listing_id}.")
                    return HttpResponseRedirect(reverse("index"))
                elif listing.sold:
                    logging.info(f"ERROR: {listing.title} already sold")
                elif listing.seller.username != request.user.username :
                    logging.info(f"ERROR: {listing.title} does not belong to {request.user.username}")
                else:
                    # Register the sale at auction
                    listing.sold = True
                    listing.save()

                    # Indicates sale in watchlist
                    watch = Watchlist.objects.filter(listing=listing)
                    for item in watch:
                        item.active = False
                        item.save()

                    # Get max bid
                    bid_list = get_bid_info(listing)

                    # Inserts the sale into the sales table
                    sale = Sale(buyer=bid_list['bid_max'], listing=listing)
                    sale.save()
            else:
                logging.info(f"{request.user.username} try to sell an item with a invalid form")
        else:
            logging.info(f"{request.user.username} attempted to sell an item without posting a form")
    else:
        logging.info(f"Unregistred user try to sell item.")

    return HttpResponseRedirect(reverse("index"))



class WatchForm(forms.Form):
    listing_id = forms.IntegerField(widget=forms.HiddenInput())

def watch_add(request):
    if not request.user.is_authenticated:
        logging.info("User not authenticated")
        return HttpResponseRedirect(reverse("index"))

    # Check if method is POST
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = WatchForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the task from the 'cleaned' version of form data
            watch = Watchlist( user=request.user,
                               listing_id=form.cleaned_data["listing_id"])
            watch.save()
            return HttpResponseRedirect(reverse("index"))

    return HttpResponseRedirect(reverse("index"))


def index_any(request, any: str):
    return HttpResponseRedirect(reverse('index'))

class CommentForm(forms.Form):
    listing_id = forms.IntegerField()
    comment = forms.CharField()

def comment(request):
    if not request.user.is_authenticated:
        logging.info("User not authenticated")
        return HttpResponseRedirect(reverse("index"))
    # Check if method is POST
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = CommentForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the comment from the 'cleaned' version of form data
            new_comment = Comment(
                user=request.user,
                comment=form.cleaned_data["comment"],
                listing_id=form.cleaned_data["listing_id"])
            new_comment.save()
            return HttpResponseRedirect(reverse("index"))

    return HttpResponseRedirect(reverse('index'))


def buys(request):
    all_info = get_all_data(request)
    return render(request, "auctions/index.html", {
        "title": "Buys",
        "page_name": "Buys List",
        "active_listings": all_info['active_listings'],
        "sold_list": all_info['sold_list'],
        "watching_list": all_info['watching_list'],
        "watch_num": all_info['watch_num'],
        "bid_list": all_info['bid_list'],
        "comments": all_info['comments'],
        "buys_list": all_info['buys_list']
    })

def sold(request):
    all_info = get_all_data(request)
    if all_info['sold_list']:
        watching_list, watch_num = get_watching_info(request)
        return render(request, "auctions/index.html", {
            "title": "Solds",
            "page_name": "Sold List",
            "sold_list": all_info['sold_list'],
            "watching_list": all_info['watching_list'],
            "watch_num": all_info['watch_num'],
            "comments": all_info['comments'],
            "active_listings": all_info['active_listings'],
            "bid_list": all_info['bid_list'],
            "comments": all_info['comments'],
            "buys_list": all_info['buys_list']
        })

    return HttpResponseRedirect(reverse("index"))

