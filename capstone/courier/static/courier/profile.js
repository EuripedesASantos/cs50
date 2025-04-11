// Initiate after page load
document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#add-phone').addEventListener('click', addPhone);
    document.querySelector('#add-address').addEventListener('click', addAddress);
});

function addPhone() {
    document.querySelector('#add-phone').style.display = 'none';
    document.querySelector('#register-phone').style.display = 'block';

    let new_phone = document.createElement('input');
        new_phone.type = 'text';
        new_phone.name = 'phone_number';
        new_phone.className = 'form-control';
        new_phone.placeholder = 'Phone number';
        new_phone.maxLength = '20';
        new_phone.required = true;
        new_phone.id = 'id_phone_number';
    document.querySelector('#new-phone').appendChild(new_phone);
}

function make_input(type, name, className, placeholder, required, id) {
    let new_city = document.createElement('input');
        new_city.type = type;
        new_city.name = name;
        new_city.className = className;
        new_city.placeholder = placeholder;
        new_city.required = required;
        new_city.id = id;
   return new_city;
}

function addAddress(address) {
    document.querySelector('#add-address').style.display = 'none';
    document.querySelector('#new-address').className = 'form-register';

    // id of the address to be updated
    if (address.id) {
    let hide_input = document.createElement('input');
        hide_input.name = 'id';
        hide_input.id = 'id_id';
        hide_input.type = 'hidden';
        hide_input.value = address.id;
    document.querySelector('#new-address').append(hide_input);
    }

    let new_address = document.createElement('textarea');
        new_address.name = 'address';
        new_address.cols = 40;
        new_address.rows = 3;
        new_address.className = 'form-control';
        new_address.placeholder = 'Address';
        new_address.required = true;
        new_address.id = 'id_address';
        if (address.address) { new_address.value = address.address; }
    document.querySelector('#new-address').appendChild(new_address);

    document.querySelector('#new-address').appendChild(
        make_input('text', 'complement', 'form-control', 'Address complement', false, 'id_complement')
    );

    let new_input = make_input('text', 'city', 'form-control', 'City', true, 'id_city');
    if (address.city) { new_input.value = address.city; }
    document.querySelector('#new-address').appendChild(new_input);

    let new_div = document.createElement('div');
        new_div.style.display = "inline-flex"

        new_input = make_input('text', 'gps_latitude', 'form-control', 'Latitude', false, 'id_gps_latitude');
        if (address.gps) { new_input.value = address.gps.latitude; }
        new_div.appendChild(new_input);

        new_input = make_input('text', 'gps_longitude', 'form-control', 'Longitude', false, 'id_gps_longitude')
        if (address.gps) { new_input.value = address.gps.longitude; }
        new_div.appendChild(new_input);

        let new_button = document.createElement('button');
            new_button.type = 'button';
            new_button.className = 'btn btn-sm btn-outline-info';
            new_button.id = 'get_gps_pos';
            new_button.innerText = 'GPS';
         new_div.appendChild(new_button);

    document.querySelector('#new-address').appendChild(new_div);

    if (address.address) {
        document.querySelector('#register-address').innerText = 'Update address';
        document.querySelector('#new-address').action = '/profile/address/update/';
    } else {
        document.querySelector('#register-address').innerText = 'Register new address';
        document.querySelector('#new-address').action = '/profile/address/add/'
    }

    GPS_for_Register()
}

function GPS_for_Register() {
    // Checks if the browser has the HTML Geolocation API
    // Else hide button to get GPS position
    // if (('geolocation' in navigator) {
    if (navigator.geolocation) {
      // Use button to get GPS position
      if (document.querySelector('#get_gps_pos')) {
        // Prevent a submit event when button is clicked
        document.querySelector('#get_gps_pos').addEventListener('submit', function(e) {e.preventDefault();});
        document.querySelector('#get_gps_pos').addEventListener('click', () => getGPS(fillRegister));
      }
    } else {
        if (document.querySelector('#get_gps_pos')) {
            document.querySelector('#get_gps_pos').style.display = 'none';
        }
      }
}

function fillRegister(curr_coords) {
    document.querySelector('#id_gps_latitude').value = curr_coords.coords.latitude;
    document.querySelector('#id_gps_longitude').value = curr_coords.coords.longitude;
}

function RemoveInfo(url, id, to_delete) {
    const csrf = getCookie('csrftoken');

    fetch(url, {
      method: 'PUT',
      body: JSON.stringify({ id: id}),
      headers: { "X-CSRFToken": csrf }
    })
    .then(response => {
        switch (response.status) {
            case 400:
            case 404:
                return response.json().then(data => {
                    window.alert(data.error);
                    return;
                });
            case 204:
                document.querySelector(to_delete + id).remove();
                return;
            default:
                window.alert(`Unknown status ${response.status} from fetch to remove phone number.`);
                return;
            }
    });
}

// The following function are copying from
// https://docs.djangoproject.com/en/dev/ref/csrf/#ajax
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function EditPhone(button, url, phone_id, phone_input) {
    document.querySelector(phone_input).disabled = false;
    button.innerText = 'Update';
    button.addEventListener('click', () => UpdatePhone(button, url, phone_id, phone_input));
}

function UpdatePhone(button, url, phone_id, phone_input) {
    const csrf = getCookie('csrftoken');

    fetch(url, {
      method: 'PUT',
      body: JSON.stringify({
        id: phone_id,
        phone_number: document.querySelector(phone_input).value
      }),
      headers: { "X-CSRFToken": csrf }
    })
    .then(response => {
        switch (response.status) {
            case 400:
            case 404:
                return response.json().then(data => {
                    window.alert(data.error);
                    return;
                });
            case 204:
                document.querySelector(phone_input).disabled = true;
                button.innerText = 'Edit';
                button.addEventListener('click', () => EditPhone(button, url, phone_id, phone_input));
                return;
            default:
                window.alert(`Unknown status ${response.status} from fetch to update phone number.`);
                return;
            }
    });
}

function EditAddress(button, address, url, address_div) {
    while( document.querySelector(address_div).childNodes[0].tagName !== 'BUTTON') {
        document.querySelector(address_div).childNodes[0].remove();
    }

    button.innerText = 'Update';

    addAddress(address);
}