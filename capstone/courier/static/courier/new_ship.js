// Function to get cookies
import { getCookie } from './cookies.js';

// Initiate after page load
var old_address_deliver = null;
var old_address_sender = null;
var users_list = null;
document.addEventListener('DOMContentLoaded', function() {

     loadUsersInfo()
    .then( result =>  {
        users_list=result;
        return;})
    .then( result => {

        if (document.querySelector('#id_user_receiver_id').selectedIndex > 0) {
            renderSelectDestintionAddress();
        }

        removeUserFromChoices();
        document.querySelector('#new-shipment_form').addEventListener('submit', function(event) {event.preventDefault(); sendNewShipment();});
        document.querySelector('#id_user_receiver_id').addEventListener('change',  () => renderSelectDestintionAddress());
        document.querySelector('#search-user').addEventListener('input',  () => hideOptions());
        document.querySelector('#id_user_receiver_id').addEventListener('focus',  () => hideOptions());

    });

});

function hideOptions() {
let text = document.querySelector('#search-user').value.toUpperCase();
let options = document.querySelector('#id_user_receiver_id').options;

    if (text !== '') {
        for (let r=1; r<options.length; r++) {
            options[r].style.display = "";
            if (options[r].text.toUpperCase().indexOf(text) > -1) {
                options[r].style.display = "";
            } else {
                options[r].style.display = "none";
            }
        }
    } else {
        for (let r=1; r<options.length; r++) {
            options[r].style.display = "";
        }
    }
}

function  removeUserFromChoices() {
    const username = document.getElementById('user-name').innerText;
    const options = document.getElementById('id_user_receiver_id').getElementsByTagName('option');
    for (let r=0; r<options.length; r++) {
        if (username.toUpperCase() === options[r].innerText.toUpperCase()) {
            options[r].remove();
            return;
        }
    }
}

function selectAddress(new_a, address_id, owner) {
    let old_a = null;

    if (owner === 'sender') {
        old_a = old_address_sender;
        document.querySelector('#id_address_sender_id').value = address_id;
    } else {
        old_a = old_address_deliver;
        document.querySelector('#id_address_deliver_id').value = address_id;
    }

    if (old_a === null) {
        old_a = new_a;
    } else {
        old_a.className = "list-group-item list-group-item-action";
        old_a = new_a;
    }
    new_a.className = "list-group-item list-group-item-success";

    if (owner === 'sender') {
        old_address_sender = old_a;
    } else {
        old_address_deliver = old_a;
    }

}

function makeSelectAddress(address, owner) {
    let new_a = document.createElement('a');
        new_a.id = `user_address-receiver_${address.id}`;
        new_a.className = "list-group-item list-group-item-action";
        new_a.href = "#";
        new_a.addEventListener('click', () => selectAddress(new_a, address.id, owner));


            new_a.innerHTML = `<b>Address:</b> ${address.address}<br>` +
                              `<b>Complement:</b> ${address.complement}<br>` +
                              `<b>City:</b> ${address.city}`
        if (address.gps) {
            new_a.innerHTML = new_a.innerHTML + `<br><b>GPS position:</b> (${address.gps.latitude}, ${address.gps.longitude})`;
        }

        return new_a;
}

function renderSelectSenderAddress() {
    document.querySelector('#address_sender-select').innerHTML = '';
    const selectUser = document.getElementById('id_user_receiver_id');
    const user_name = document.getElementById('user-name').innerText;

     let user_info = getUserInfo(user_name);
     if (user_info.addresses.length !== 0) {
        let new_p = document.createElement('p');
            new_p.innerHTML = "<b>Click on the pickup address:</b>"
        document.querySelector('#address_sender-select').appendChild(new_p);
        let div_html = '';
        user_info.addresses.forEach(address => {
            const new_ul = document.createElement('ul');
            new_ul.className = "list-group";
            new_ul.appendChild(makeSelectAddress(address, 'sender'));


       document.querySelector('#address_sender-select').appendChild(new_ul);
       document.querySelector('#address_sender-select').appendChild(document.createElement('hr'));
        });
     } else {
        document.querySelector('#address_sender-select').innerHTML = '<div class="alert alert-danger" role="alert"><p>No address registered!</p></div>';
     }

}

function renderSelectDestintionAddress() {
    document.querySelector('#address_deliver-select').innerHTML = '';
    const selectUser = document.getElementById('id_user_receiver_id');
    const user_name = selectUser.options[selectUser.selectedIndex].innerText;

//    document.querySelector('#address_deliver-select').innerText
     let user_info = getUserInfo(user_name);

     if (user_info.addresses.length !== 0) {
        let new_p = document.createElement('p');
            new_p.innerHTML = "<b>Click on the destination address:</b>"
        document.querySelector('#address_deliver-select').appendChild(new_p);
        let div_html = '';
        user_info.addresses.forEach(address => {
            const new_ul = document.createElement('ul');
            new_ul.className = "list-group";
            new_ul.appendChild(makeSelectAddress(address, 'destination'));


       document.querySelector('#address_deliver-select').appendChild(new_ul);
        });
     } else {
        document.querySelector('#address_deliver-select').innerHTML = '<div class="alert alert-danger" role="alert"><p>No address registered!</p></div>';
     }

}

function sendNewShipment() {
    if (document.querySelector('#id_user_receiver_id').selectedIndex > 0 &&
        document.querySelector('#id_address_sender_id').value !== '' &&
        document.querySelector('#id_address_deliver_id').value !== '' &&
        document.querySelector('#id_contents').value.length > 0) {
        document.querySelector('#new-shipment_form').submit();
    } else {
    }
}

function getUserInfo(user_name) {
    let result = null;
    if (users_list) {
        users_list.forEach(user => {

            if (user.username === user_name) {
                result = user;
                return;
            }
        });
    return result;

    }

}

async function loadUsersInfo() {
    fetch('/users')
    .then(response => response.json())
    .then(result => {
       users_list = result;
       renderSelectSenderAddress();
       return;
    })
    .catch(error => {
        console.error(error.message);
    });
}