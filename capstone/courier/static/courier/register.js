// Initiate after page load
document.addEventListener('DOMContentLoaded', function() {
    GPS_for_Register();
});

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

