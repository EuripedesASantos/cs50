import random

from django.db import models

from django.utils import timezone

from django.contrib.auth.models import User as auth_User

phone_max_length = 20


class User(auth_User):
    is_courier = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phones_num": self.phones.count(),
            "addresses_num": self.addresses.count(),
            "phones": [phone.serialize() for phone in self.phones.all()],
            "addresses": [address.serialize() for address in self.addresses.all()],
        }

    def list_for_shipment(self):
        return [address.user for address in self.addresses.all()]


class PhoneNumber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="phones")
    phone_number = models.CharField(max_length=phone_max_length)

    def serialize(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number
        }


class GPSPosition(models.Model):
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    date_time = models.DateTimeField(default=timezone.now)

    def serialize(self):
        return {'latitude': self.latitude, 'longitude': self.longitude}


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address = models.CharField(max_length=200)
    complement = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    gps = models.ForeignKey(GPSPosition, null=True, on_delete=models.CASCADE, related_name="address_positions")

    def serialize(self):
        if self.gps:
            return {
                "id": self.id,
                "address": self.address,
                "complement": self.complement,
                "city": self.city,
                "gps": self.gps.serialize()
            }
        else:
            return {
                "id": self.id,
                "address": self.address,
                "complement": self.complement,
                "city": self.city
            }


class Shipment(models.Model):
    CREATED = 0
    ORDERED = 1
    PICK_UP = 2
    DELIVERED = 3
    CANCELED = 4

    SHIPMENT_STATUS = (
        (CREATED, 'Created'),
        (ORDERED, 'Ordered'),
        (PICK_UP, 'Pick up order'),
        (DELIVERED, 'Delivered'),
        (CANCELED, 'Canceled'))

    contents = models.CharField(max_length=200)
    check_code_get = models.CharField(max_length=10, null=True)
    check_code_put = models.CharField(max_length=10, null=True)
    user_courier = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="couriers")
    user_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="senders")
    address_sender = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="get_place")
    user_receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receivers")
    address_receiver = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="put_place")
    chat_id = models.CharField(max_length=10, null=True)
    datetime_create = models.DateTimeField(default=timezone.now)
    status = models.IntegerField(default=0,
                                 choices=SHIPMENT_STATUS)

    def serialize(self):
        result = {
            "id": self.id,
            "contents": self.contents,
            "check_code_get": self.check_code_get,
            "check_code_put": self.check_code_put,
            "user_sender": self.user_sender.serialize(),
            "user_receiver": self.user_receiver.serialize(),
            "address_sender": self.address_sender.serialize(),
            "address_receiver": self.address_receiver.serialize()}
        if self.user_courier:
            result["courier"] = self.user_courier.serialize()

        result["status"] = self.SHIPMENT_STATUS[self.status][1]
        result["status_id"] = self.SHIPMENT_STATUS[self.status][0]

        return result


class Deliver(models.Model):
    shipment = models.ForeignKey(Shipment, null=False, on_delete=models.CASCADE, related_name="deliver_shipments")
    datetime_create = models.DateTimeField(default=timezone.now)
    gps = models.ForeignKey(GPSPosition, null=True, on_delete=models.CASCADE, related_name="deliver_positions")


def make_code(user1: User, user2: User, ship: Shipment) -> str:
    random.seed(user1.id * ship.id + user2.id)

    code = ''
    for digit in range(4):
        code += str(random.randint(0, 9))
    return code
