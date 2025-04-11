from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms

from courier.models import phone_max_length

from courier.models import (PhoneNumber,
                            Address,
                            GPSPosition,
                            User,
                            Shipment,
                            make_code)

from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
import json


def get_user(request):
    return User.objects.get(username=request.user.username)


def get_shipments_courier(request, status=None):
    print(f"get_shipments_courier status= {status} Shipment.CREATED={Shipment.CREATED} == {status == Shipment.CREATED}")
    if status == None:
        return [ship.serialize() for ship in get_user(request).couriers.all()]
    else:
        if status == Shipment.CREATED:
            print(True)
            print([ship.serialize() for ship in Shipment.objects.filter(status=status).exclude(user_sender=get_user(request))])
            return [ship.serialize() for ship in Shipment.objects.filter(status=status).exclude(user_sender=get_user(request))]
        else:
            print(False)
            return [ship.serialize() for ship in get_user(request).couriers.filter(status=status)]


def is_courier(request):
    try:
        return get_user(request).is_courier
    except:
        return False


class LoginForm(forms.Form):
    username = forms.CharField(label="", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "User name", "autofocus": ""}))
    password = forms.CharField(label="",
                               widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))


@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        # Receives the user registration data sent to register the user
        form = LoginForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Attempt to user login
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))

        return render(request, "courier/login.html", {
            "message": "Invalid username and/or password.",
            "form": form
        })
    else:
        return render(request, "courier/login.html", {
            "form": LoginForm})


@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


class UserForm(forms.Form):
    username = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "User name", "autofocus": ""}))
    firstname = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "First name", "autofocus": ""}))
    lastname = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Last name", "autofocus": ""}))
    email = forms.EmailField(required=True, label="", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Email"}))
    password = forms.CharField(required=True, label="", widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Password"}))
    confirmation = forms.CharField(required=True, label="", widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": "Confirm Password"}))
    is_courier = forms.BooleanField(required=False, widget=forms.CheckboxInput())


class PhoneForm(forms.Form):
    phone_number = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Phone number"}),
                                   max_length=phone_max_length)


class AddressForm(forms.Form):
    address = forms.CharField(required=True, label="", widget=forms.Textarea(
        attrs={"class": "form-control", "rows": 3, "placeholder": "Address"}))
    complement = forms.CharField(required=False, label="", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Address complement"}))
    city = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "City"}))
    gps_latitude = forms.FloatField(required=False, label="", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Latitude"}))
    gps_longitude = forms.FloatField(required=False, label="", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Longitude"}))


class RegisterForm(AddressForm, PhoneForm, UserForm):
    pass


def create_address(user, address, complement, city, gps):
    try:
        if complement and gps:
            Address(user=user, address=address, complement=complement, city=city, gps=gps).save()
        elif complement:
            Address(user=user, address=address, complement=complement, city=city).save()
        elif gps:
            Address(user=user, address=address, city=city, gps=gps).save()
        else:
            Address(user=user, address=address, city=city).save()
    except Exception as e:
        return f"Error creating new address: {e}"
    else:
        return None


@csrf_protect
def register_view(request):
    if request.method == "POST":
        # Receives the user registration data sent to register the user
        form = RegisterForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Ensure password matches confirmation
            password = form.cleaned_data["password"]
            confirmation = form.cleaned_data["confirmation"]
            if password != confirmation:
                form.add_error('confirmation', 'Passwords must match.')
                return render(request, "courier/index.html", {
                    "title": "New Profile",
                    "form": form,
                    "message": "Passwords must match."
                }, status=400)

            latitude = form.cleaned_data['gps_latitude']
            longitude = form.cleaned_data['gps_longitude']
            gps = None
            if latitude and longitude:
                gps = GPSPosition(latitude=latitude, longitude=longitude)
                gps.save()
            elif latitude:
                form.add_error('gps_longitude', 'Longitude error!')
                return render(request, "courier/index.html", {
                    "title": "New Profile",
                    "message": "<p>Invalid register information:</p>" + str(form.errors),
                    "form": form}, status=400)
            elif longitude:
                form.add_error('gps_latitude', 'Latidude error!')
                return render(request, "courier/index.html", {
                    "title": "New Profile",
                    "message": "<p>Invalid register information:</p>" + str(form.errors),
                    "form": form}, status=400)
            # Attempt to create new user
            try:
                username = form.cleaned_data['username']
                firstname = form.cleaned_data['firstname']
                lastname = form.cleaned_data['lastname']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                is_courierl = form.cleaned_data['is_courier']
                user = User.objects.create_user(username=username, email=email,
                                                password=password, is_courier=is_courierl,
                                                first_name=firstname, last_name=lastname)
                user.save()
            except Exception as e:
                return render(request, "courier/index.html", {
                    "title": "New Profile",
                    "form": form,
                    "message": f"Error creating new user: {e}"
                }, status=400)

            PhoneNumber(user=user, phone_number=form.cleaned_data['phone_number']).save()

            # Create a new address
            msg = create_address(user=user,
                                 address=form.cleaned_data['address'],
                                 complement=form.cleaned_data['complement'],
                                 city=form.cleaned_data['city'],
                                 gps=gps)
            if msg:
                return render(request, "courier/index.html", {
                    "title": "New Profile",
                    "form": form,
                    "message": msg
                }, status=400)
            else:
                return redirect("login")

        else:
            return render(request, "courier/index.html", {
                "title": "New Profile",
                "message": "<p>Invalid register information:</p>" + str(form.errors),
                "form": form
            }, status=400)

    return render(request, "courier/index.html", {
        "title": "New Profile",
        "form": RegisterForm()
    })


class NewShipmentForm(forms.Form):
    user_receiver_id = forms.ChoiceField(required=True, label="Select recipient:",
                                         widget=forms.Select(
                                             attrs={"class": "form-control", "placeholder": "User name to select"}))
    contents = forms.CharField(required=True, label="", widget=forms.Textarea(
        attrs={"class": "form-control", "rows": 3, "placeholder": "Content description"}))
    address_sender_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    address_deliver_id = forms.IntegerField(required=True, widget=forms.HiddenInput())


@login_required(login_url='/login/')
def profile_view(request, message=None, form=None):
    return render(request, "courier/index.html", {
        "title": "User Profile",
        "user_profile": get_user(request).serialize(),
        "is_courier": is_courier(request),
        "message": message,
        "form": form
    })


@csrf_protect
@login_required(login_url='/login/')
def phone_add(request):
    msg = None
    if request.method == "POST":
        # Receives the user registration data sent to register the user
        form = PhoneForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():
            try:
                PhoneNumber(user=get_user(request),
                            phone_number=form.cleaned_data['phone_number']).save()
            except Exception as e:
                msg = f"Error occurs saving new phone number {form.cleaned_data['phone_number']}: {e}"
        else:
            msg = 'Error: Invalide information provided insert new phone number!'

    return profile_view(request, msg)


@csrf_protect
@login_required(login_url='/login/')
def address_add(request):
    msg = None
    if request.method == "POST":
        # Receives the user registration data sent to register the user
        form = AddressForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():
            # Create a new GPS position
            latitude = form.cleaned_data['gps_latitude']
            longitude = form.cleaned_data['gps_longitude']
            gps = None
            if latitude and longitude:
                try:
                    gps = GPSPosition(latitude=latitude, longitude=longitude)
                    gps.save()
                except Exception as e:
                    return profile_view(request, f"Error creating new GPS postion: {e}", form)
            elif latitude:
                return profile_view(request, "Invalid longitude information!", form)
            elif longitude:
                return profile_view(request, "Invalid latitude information!", form)

            # Create a new address
            msg = create_address(user=get_user(request),
                                 address=form.cleaned_data['address'],
                                 complement=form.cleaned_data['complement'],
                                 city=form.cleaned_data['city'],
                                 gps=gps)
        else:
            msg = 'Form information invalid!'

    return profile_view(request, msg)


def make_and_log_errors(message: str, status=404):
    return JsonResponse({"error": message}, status=status)


@csrf_protect
@login_required(login_url='/login/')
def phone_remove(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        phone_id = data["id"]
        if phone_id and phone_id != '':
            try:
                PhoneNumber.objects.get(id=phone_id).delete()
            except Exception as e:
                return make_and_log_errors(f"Error removing phone: ({e}).")
            else:
                # Operation successful but returns no content
                return JsonResponse(data={}, status=204)
        else:
            return make_and_log_errors('PUT request without id of phone number to be removed!')
    else:
        return JsonResponse({"error": "Try remove phone number without PUT request!"}, status=400)


@csrf_protect
@login_required(login_url='/login/')
def phone_update(request):
    if request.method == "PUT":
        if request.body == b'':
            return make_and_log_errors('PUT request without with empty form!')
        data = json.loads(request.body)
        if 'id' in data.keys():
            phone_id = data["id"]
        else:
            phone_id = None
        # Chech id and phone_number exists in PUT request
        if not phone_id or phone_id == '':
            return make_and_log_errors('PUT request without id of phone number to be updated!')

        if 'phone_number' in data.keys():
            phone_number = data["phone_number"]
        else:
            phone_number = None
        if not phone_number or phone_number == '':
            return make_and_log_errors('PUT request without new value of phone number to be updated!')

        try:
            phone = PhoneNumber.objects.get(id=phone_id)
        except Exception as e:
            return make_and_log_errors(f"Error getting phone number: ({e}).")
        else:
            try:
                phone.phone_number = phone_number
                phone.save()
            except Exception as e:
                return make_and_log_errors(f"Error updating phone number: ({e}).")
            else:
                # Operation successful but returns no content
                return JsonResponse(data={}, status=204)
    else:
        return JsonResponse({"error": "Try update phone number without PUT request!"}, status=400)


@csrf_protect
@login_required(login_url='/login/')
def address_remove(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        address_id = data["id"]
        if address_id and address_id != '':
            try:
                Address.objects.get(id=address_id).delete()
            except Exception as e:
                return make_and_log_errors(f"Error removing address: ({e}).")
            else:
                # Operation successful but returns no content
                return JsonResponse(data={}, status=204)
        else:
            return make_and_log_errors('PUT request without id of address to be removed!')
    else:
        return JsonResponse({"error": "Try remove address without PUT request!"}, status=400)


@csrf_protect
@login_required(login_url='/login/')
def address_update(request):
    if request.method == "POST":
        # Receives the user registration data sent to register the user
        if 'id' in request.POST.keys():
            address_id = request.POST["id"]
        else:
            address_id = None
        if not address_id or address_id == '':
            return make_and_log_errors('PUT request without id of address to be updated!')

        form = AddressForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            try:
                address_old = Address.objects.get(id=address_id)
            except Exception as e:
                return profile_view(request, f"Error update address: {e}")
            else:
                # Get GPS position
                latitude = form.cleaned_data['gps_latitude']
                longitude = form.cleaned_data['gps_longitude']

                save_gps = False
                if address_old.gps:
                    if address_old.gps.longitude != longitude:
                        address_old.gps.longitude = longitude
                        save_gps = True

                    if address_old.gps.latitude != latitude:
                        address_old.gps.latitude = latitude
                        save_gps = True
                else:
                    if latitude and longitude:
                        try:
                            address_old.gps = GPSPosition(latitude=latitude, longitude=longitude)
                        except Exception as e:
                            return profile_view(request, f"Error creating new GPS position to be updated address: {e}")
                        else:
                            save_gps = True

                if save_gps:
                    try:
                        address_old.gps.save()
                    except Exception as e:
                        return profile_view(request, f"Error update GPS position of updated address: {e}")

                # Get the last of address data
                address = form.cleaned_data['address']
                complement = form.cleaned_data['complement']
                city = form.cleaned_data['city']

                save_address = False
                if address_old.address != address:
                    address_old.address = address
                    save_address = True

                if address_old.complement != complement:
                    address_old.complement = complement
                    save_address = True

                if address_old.city != city:
                    address_old.city = city
                    save_address = True

                if save_address:
                    try:
                        address_old.save()
                    except Exception as e:
                        return profile_view(request, f"Error update address: {e}")
        else:
            return profile_view(request, f"Form information invalid!")
    # Operation successful but returns no content
    return HttpResponseRedirect(reverse('profile'))


@login_required(login_url='/login/')
def users_list(request):
    # Get list of users with each information
    try:
        users = User.objects.all()
    except Exception as e:
        return make_and_log_errors(f"Error getting users list and informations: {e}.")

    # Return list of followed users
    return JsonResponse([user.serialize() for user in users], safe=False, status=200)


@csrf_protect
@login_required(login_url='/login/')
def shipments_new(request):
    if request.method == "POST":
        form = NewShipmentForm(request.POST)
        form.fields['user_receiver_id'].choices = [('-1', 'Select user')] + [(user.id, user.username) for user in
                                                                             User.objects.all()]

        if not form.is_valid():
            return render(request, "courier/index.html", {
                "title": "New Shipment",
                "form": form,
                "is_courier": is_courier(request),
                "message": "Form is invalid!"})

        # Create a New Shipment
        address_sender_id = form.cleaned_data['address_sender_id']
        address_deliver_id = form.cleaned_data['address_deliver_id']
        contents = form.cleaned_data['contents']
        user_receiver_id = form.cleaned_data['user_receiver_id']

        try:
            new_ship = Shipment(contents=contents,
                                user_sender=get_user(request),
                                address_sender=Address.objects.get(id=address_sender_id),
                                user_receiver=User.objects.get(id=user_receiver_id),
                                address_receiver=Address.objects.get(id=address_deliver_id))
            new_ship.save()
        except Exception as e:
            return render(request, "courier/index.html", {
                "title": "New Shipment",
                "form": form,
                "is_courier": is_courier(request),
                "message": f"Error creating shipment: ({e})."})
        else:
            # Create check codes
            try:
                new_ship.check_code_get = make_code(new_ship.user_sender, new_ship.user_receiver, new_ship)
                new_ship.check_code_put = make_code(new_ship.user_receiver, new_ship.user_sender, new_ship)
                new_ship.save()
            except Exception as e:
                return render(request, "courier/index.html", {
                    "title": "New Shipment",
                    "form": form,
                    "is_courier": is_courier(request),
                    "message": f"Erro inserting check codes in Shipment id={new_ship.id}: {e}"})
            else:
                return HttpResponseRedirect(reverse('index'))

    form = NewShipmentForm()
    form.fields['user_receiver_id'].choices = [('-1', 'Select user')] + [(user.id, user.username) for user in
                                                                         User.objects.all()]
    return render(request, "courier/index.html", {
        "title": "New Shipment",
        "form": form,
        "is_courier": is_courier(request)})


@login_required(login_url='/login/')
def index(request):
    return render(request, "courier/index.html", {
        "title": "Courier System",
        "shipments": [ship.serialize() for ship in get_user(request).senders.all()],
        "is_courier": is_courier(request)})


class ShipIdForm(forms.Form):
    shipment_id = forms.IntegerField(required=True, widget=forms.HiddenInput())


@csrf_protect
@login_required(login_url='/login/')
def courier_order(request):
    if request.method == "POST":
        form = ShipIdForm(request.POST)

        if form.is_valid():
            shipment_id = form.cleaned_data['shipment_id']
            try:
                ship = Shipment.objects.get(id=shipment_id)
                if ship.status != Shipment.CREATED:
                    raise RuntimeError('Data inconsistence detected!')
                ship.status = Shipment.ORDERED
                ship.user_courier = get_user(request)
                ship.save()
            except Exception as e:
                return render(request, "courier/index.html", {
                    "title": "Shipments to order",
                    "shipments": [ship.serialize() for ship in get_user(request).senders.filter(status__gte=0)],
                    "is_courier": is_courier(request),
                    "message": f"Error ordering shipment: {e}!"})
        else:
            return render(request, "courier/index.html", {
                "title": "Shipments to order",
                "shipments": get_shipments_courier(request, Shipment.CREATED),
                "is_courier": is_courier(request),
                "message": "Form is invalid!"})

    return render(request, "courier/index.html", {
        "title": "Shipments to order",
        "shipments": get_shipments_courier(request, Shipment.CREATED),
        "is_courier": is_courier(request)})


@login_required(login_url='/login/')
def courier_delivered(request):
    return render(request, "courier/index.html", {
        "title": "Delivered Orders",
        "shipments": get_shipments_courier(request, Shipment.DELIVERED),
        "is_courier": is_courier(request)})


@login_required(login_url='/login/')
def courier_view(request):
    return render(request, "courier/index.html", {
        "title": "All Shipments",
        "shipments": [ship.serialize() for ship in get_user(request).couriers.all()] +
                     [ship.serialize() for ship in Shipment.objects.filter(status=Shipment.CREATED).exclude(user_sender=get_user(request))],
        "is_courier": is_courier(request)})


@csrf_protect
@login_required(login_url='/login/')
def shipments_cancel(request):
    if request.method == "POST":
        form = ShipIdForm(request.POST)

        if form.is_valid():
            shipment_id = form.cleaned_data['shipment_id']
            try:
                ship = Shipment.objects.get(id=shipment_id)
                ship.status = Shipment.CANCELED
                ship.save()
            except Exception as e:
                return render(request, "courier/index.html", {
                    "title": "Courier System",
                    "shipments": [ship.serialize() for ship in get_user(request).senders.filter(status__gte=0)],
                    "is_courier": is_courier(request),
                    "message": f"Error canceling shipment: {e}!",
                    "form": form})
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "courier/index.html", {
                "title": "Courier System",
                "shipments": [ship.serialize() for ship in get_user(request).senders.filter(status__gte=0)],
                "is_courier": is_courier(request),
                "message": "Unable to cancel shipment!",
                "form": form})

    return render(request, "courier/index.html", {
        "title": "Courier System",
        "shipments": [ship.serialize() for ship in get_user(request).senders.filter(status__gte=0)],
        "is_courier": is_courier(request),
        "message": "Use POST form to cancel shipment!",
        "form": ShipIdForm()})


class CheckGetForm(ShipIdForm):
    check_code_get = forms.CharField(required=True, max_length=4)


@csrf_protect
@login_required(login_url='/login/')
def courier_receive(request):
    funtion_title = 'Order to receive'
    if request.method == "POST":
        form = CheckGetForm(request.POST)

        if form.is_valid():
            shipment_id = form.cleaned_data['shipment_id']
            check_code_get = form.cleaned_data['check_code_get']
            try:
                ship = Shipment.objects.get(id=shipment_id)
                # Check consistence into operations
                if ship.status != Shipment.ORDERED:
                    raise RuntimeError('Data inconsistence detected!')

                # Check code
                if ship.check_code_get != check_code_get:
                    raise RuntimeError('Check code incorrect!')

                ship.status = Shipment.PICK_UP
                ship.save()
            except Exception as e:
                return render(request, "courier/index.html", {
                    "title": funtion_title,
                    "shipments": get_shipments_courier(request, Shipment.ORDERED),
                    "is_courier": is_courier(request),
                    "message": f"Error receiving shipment: {e}"})
        else:
            return render(request, "courier/index.html", {
                "title": funtion_title,
                "shipments": get_shipments_courier(request, Shipment.ORDERED),
                "is_courier": is_courier(request),
                "message": "Form is invalid!"})

    return render(request, "courier/index.html", {
        "title": funtion_title,
        "shipments": get_shipments_courier(request, Shipment.ORDERED),
        "is_courier": is_courier(request)})


class CheckPutForm(ShipIdForm):
    check_code_put = forms.CharField(required=True, max_length=4)


@csrf_protect
@login_required(login_url='/login/')
def courier_deliver(request):
    funtion_title = 'Order to deliver'
    if request.method == "POST":
        form = CheckPutForm(request.POST)

        if form.is_valid():
            shipment_id = form.cleaned_data['shipment_id']
            check_code_put = form.cleaned_data['check_code_put']
            try:
                ship = Shipment.objects.get(id=shipment_id)
                # Check consistence into operations
                if ship.status != Shipment.PICK_UP:
                    raise RuntimeError('Data inconsistence detected!')

                # Check code
                if ship.check_code_put != check_code_put:
                    raise RuntimeError('Check code incorrect!')

                ship.status = Shipment.DELIVERED
                ship.save()
            except Exception as e:
                return render(request, "courier/index.html", {
                    "title": funtion_title,
                    "shipments": get_shipments_courier(request, Shipment.PICK_UP),
                    "is_courier": is_courier(request),
                    "message": f"Error delivering shipment: {e}"})
        else:
            return render(request, "courier/index.html", {
                "title": funtion_title,
                "shipments": get_shipments_courier(request, Shipment.PICK_UP),
                "is_courier": is_courier(request),
                "message": "Form is invalid!"})

    return render(request, "courier/index.html", {
        "title": "Order to deliver",
        "shipments": get_shipments_courier(request, Shipment.PICK_UP),
        "is_courier": is_courier(request)})


@csrf_protect
@login_required(login_url='/login/')
def shipments_receipt(request):
    return render(request, "courier/index.html", {
        "title": "Shipment to Receipt",
        "shipments": [ship.serialize() for ship in get_user(request).receivers.filter(status__lt=Shipment.CANCELED)],
        "is_courier": is_courier(request)})


@csrf_protect
@login_required(login_url='/login/')
def shipments_deliver(request):
    return render(request, "courier/index.html", {
        "title": "Shipment to Deliver",
        "shipments": [ship.serialize() for ship in get_user(request).senders.filter(status=Shipment.PICK_UP)],
        "is_courier": is_courier(request)})
