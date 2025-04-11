from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Users
    path("users/", views.users_list, name="users-list"),
    # Profile
    path("profile/", views.profile_view, name="profile"),
    path("profile/address/add/", views.address_add, name="add-address"),
    path("profile/address/update/", views.address_update, name="update-address"),
    path("profile/address/remove/", views.address_remove, name="remove-address"),
    path("profile/phone/add/", views.phone_add, name="add-phone"),
    path("profile/phone/update/", views.phone_update, name="update-phone"),
    path("profile/phone/remove/", views.phone_remove, name="remove-phone"),
    # Shipments
    path("shipments/new", views.shipments_new, name="new-shipment"),
    path("shipments/cancel", views.shipments_cancel, name="cancel-shipment"),
    path("shipments/receipt", views.shipments_receipt, name="receipt-shipment"),
    path("shipments/deliver", views.shipments_deliver, name="deliver-shipment"),
    # Courier
    path("courier/", views.courier_view, name="courier-view"),
    path("courier/order", views.courier_order, name="courier-order"),
    path("courier/receive", views.courier_receive, name="courier-receive"),
    path("courier/deliver", views.courier_deliver, name="courier-deliver"),
    path("courier/delivered", views.courier_delivered, name="courier-delivered"),
]
