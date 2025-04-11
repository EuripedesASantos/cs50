# Courier System
(*Final project of CS50’s Web Programming with Python and JavaScript*)

This project implements a web-based courier system, via desktop or mobile, allowing users to create and track shipments, as well as manage their profiles. Delivery people can accept, pick up, and deliver orders. The project was structured iteratively using Django and JavaScript.

---
# Distinctiveness

According to the requirements, this project must be sufficiently distinct from the other work carried out throughout the course. And in compliance with this requirement is the fact that the other projects did not have a triangulated relationship between users, nor did they have multiple actions associated with each task. Because its have a user who requests a delivery to a second user who will receive the order. And in parallel, have the delivery person who collects the item from the user who dispatches the item, using a verification code, and delivers it to the receiving user, also using a second verification code. Everything is monitored and validated in a web interface of the application. 

---
# Complexity

The complexity of the project is associated with:
* Types of users, namely: sender, receiver and delivery person;
* Data required for each type of user: personal contact information; delivery and receiving addresses; and description of the item to be delivered.
* Tasks: decide on a delivery; pick up the delivery with validation; make the delivery to the recipient with validation; and monitor each task performed.
* Actions involved: creation of an order; allocation of a delivery person; pick up the item at the sender's address; validation of the pick up of the delivery item; delivery of the item to the recipient's delivery address; validation of the delivery of the item
---
# Specification:
* Users: all users must be registered with a username, email, first name, last name, contact phone number and address (GPS indication if applicable). They can edit, delete and insert a new phone number or address at any time.
  * Sender: the user who requests shipping.
     * Can create shipping requests;
     * Has access to the list of all items that have been requested to be shipped, indicating the status of each order (created, with delivery order, collected and delivered to the recipient). They can also cancel items that do not yet have a collection order;
     * Can see the list of all items that will be picked up by the delivery person with their respective verification codes; and
     * Access to the list of all their orders that have already been delivered.
  * Recipient: user to whom a delivery was requested
    * Access to the list of items that should be received with their respective verification codes.
  * Delivery person: user who indicated in their registration that they are a delivery person.
    * Access the list of all deliveries created but that do not yet have an associated delivery person, where you can order the order for delivery;
    * Access the list of all your delivery orders that you must pick up and the address of the requester, where you will also register the pick-up by entering the verification code provided by the order requester;
    * Access the list of all your delivery orders that you must deliver to the recipient and the delivery address, where you will also register the delivery by entering the verification code provided by the delivery recipient; and
    * Access the list of all your deliveries made.
* Delivery item:
  * Has a description;
  * A pick-up address and the details of the delivery requester;
  * A delivery address and the details of the recipient;
  * The details of the delivery person;
  * Has a verification code to be received upon pick-up at the address of the delivery requester;
  * Has a verification code to be received at the item's delivery address; and
  * A status of the item's shipping status, such as: delivery order created; shipping order created (delivery person assigned); picked up at the order address; and finally delivered to the recipient.
___

## File Structure and Descriptions of Application

### courier/models.py

Defines the database models:

* **PhoneNumber:** Stores user phone numbers.
* **Address:** Stores addresses with optional GPS coordinates.
* **GPSPosition:** Stores latitude and longitude.
* **User:** Extends Django's User model to include a `is_courier` flag.
* **Shipment:** Represents a shipment, linking sender, receiver, addresses, contents, status, and check codes.
* **make_code():** Generates check codes for shipments.

### courier/views.py

Contains the view functions:

* **Authentication:**
  * Login: `login_view()`
  * Logout: `logout_view()`
* **User registration:**`register_view()`
* **Profile Management:** 
  * Create Profile:`profile_view()`
  * Add new phone to profile: `phone_add()`
  * Update a profile phone: `phone_update()`
  * Remove phone from profile: `phone_remove()`
  * Add new address to profile: `address_add()`
  * Update a profile address: `address_update()`
  * Remove address from profile: `address_remove()`
* **API Endpoint to list all user's names:** `users_list()`
* **Shipment Management:**
  * List all shipments of the user: `index()`
  * Create a new shipment: `shipments_new()`
  * User cancel shipments: `shipments_cancel()`
  * List shipments to user recipt: `shipments_receipt()`
  * List shipments to user deliver: `shipments_deliver()`
  * List shipments under courier task: `courier_view()`
  * Courier order the shipment or list shipments for order: `courier_order()`
  * The courier records receipt of the shipment: `courier_receive()`
  * The courier records deliver of the shipment: `courier_deliver()`
  * List of shipments delivered by courier: `courier_delivered()`
* **Support Functions:**
  * Convert extends Django's User model to User's application:`get_user()`
  * List shipments under courier task:`get_shipments_courier()`
  * Indicates whether the user is a courier:`is_courier()`
  * Used in tests for create a new address:`create_address()`
  * Return a JSON response when a error occurs:`make_and_log_errors()`

### courier/templates/courier/*.html

HTML templates for the UI:

* **layout.html:** Base template for site layout.
* **index.html:** Main template extending `layout.html`.
* **login.html:** Login form.
* **register.html:** Registration form.
* **nav.html:** Navigation bar.
* **new_ship.html:** Form for creating new shipments.
* **profile.html:** User profile management.
* **shipments.html:** Displays shipments.

### courier/static/courier/*.js

JavaScript files:

* **profile.js:** Enhances profile page with dynamic phone/address adding, editing, and removal.
* **register.js:** Allows user to get their GPS position to the registration form
* **shipments.js:** Handles shipment data display in `shipments.html`.
* **new_ship.js:** Manages new shipment creation.
* **gps.js:** Handles GPS functionality.

### courier/static/courier/styles.css

Main stylesheet for the application.

### courier/tests.py

Unit tests for the application.


## How to Run the Application

1. **Clone the repository:**
```bash
git clone https://github.com/me50/EuripedesASantos.git
```
2. **Navigate to the project directory:**
```bash
cd EuripedesASantos/web50/projects/2020/x/final_proj
```
3. **Create a virtual environment:**
```bash
python3 -m venv .venv
```
4. **Activate the virtual environment:**
    * Windows:`.venv\Scripts\activate`
    * macOS/Linux:`source .venv/bin/activate`
5. **Install dependencies:**
```bash
pip install -r requirements.txt
```
6. **Apply database migrations:**
```bash
python manage.py migrate
```
7. **Create a superuser (for admin access):**
```bash
python manage.py createsuperuser
```
8. **Start the development server:**
```bash
python manage.py runserver
```
9. **Open your browser:**
```bash
http://127.0.0.1:8000/
```


## Additional Information

* **The initial user data can be loaded into the application using the command:**
```bash
python manage.py loaddata dumpdata_user.json
```
* **To populate the application completely, with the most varied data and delivery statuses, use:**
```bash
python manage.py loaddata dumpdata.json