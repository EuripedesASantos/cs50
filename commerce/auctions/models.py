from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils import timezone

class User(AbstractUser):
    # id = models.AutoField(primary_key=True, null=False, unique=True)
    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username

class AuctionListing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sellers")
    title = models.CharField(max_length=64, null=False)
    description = models.CharField(max_length=200, null=False)
    start_bid = models.FloatField(null=False, default=0)
    img_url = models.URLField(max_length=200, null=True)
    category = models.CharField(max_length=64, null=True)
    sold = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidders")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="listings")
    value = models.FloatField(null=False, default=0)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["listing", "date"]

    def __str__(self):
        return f"Bid ({self.user.username}: ${self.value} on {self.listing.title})"

class Sale(models.Model):
    buyer = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="buyers")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="solds")
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.listing.seller.username} sold to {self.buyer.user.username}: {self.listing.title}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenters")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=200)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.user.username} comment on {self.listing.title}: {self.comment}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchers")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="watching")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["user", "listing"]

    def __str__(self):
        return f"{self.user.username} watching {self.listing.title}"


