//google maps code
var map;
function initialize(lat, long, targetID) {
    var mapOptions = {
    	zoom: 14,
    	center: new google.maps.LatLng(lat, long),
    	mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById(targetID), mapOptions);
}

// document ready
$(document).ready(function() {

	// first, see if you can get the user's geo-location
    if (navigator.geolocation) {

		var options = {
		  enableHighAccuracy: true,
		  timeout: 5000,
		  maximumAge: 0
		};

		function success(data){
			var latitude = data.coords.latitude;
			var longitude = data.coords.longitude;
			google.maps.event.addDomListener(window, 'load', initialize(latitude, longitude, "map-user"));
			var marker = new google.maps.Marker({
				position: new google.maps.LatLng(latitude,longitude),
				map: map,
				title: ''
			});
			var marker2 = new google.maps.Marker({
				position: new google.maps.LatLng(37.786004,-122.409193),
				map: map,
				icon: 'http://www.umb.edu/editor_uploads/maps-icons/ATM_icon.png',
				title: ''
			});
			var marker3 = new google.maps.Marker({
				position: new google.maps.LatLng(37.787149,-122.409897),
				map: map,
				icon: 'http://www.umb.edu/editor_uploads/maps-icons/ATM_icon.png',
				title: ''
			});
			var infowindow = new google.maps.InfoWindow({
				content: "You are here"
			});
			var infowindow2 = new google.maps.InfoWindow({
				content: "Pick up your Visa from this location"
			});
			var infowindow3 = new google.maps.InfoWindow({
				content: "Pick up your Visa from this location"
			});
			google.maps.event.addListener(marker, 'click', function() {
				infowindow.open(map,marker);
			});
			google.maps.event.addListener(marker2, 'click', function() {
				infowindow2.open(map,marker2);
			});
			google.maps.event.addListener(marker3, 'click', function() {
				infowindow3.open(map,marker3);
			});
		}
		function error(data){
			console.log(data);
		}
	    //use the navigator.geolocation.getCurrentPosition() method to get the latitude-longitude coordinates
		navigator.geolocation.getCurrentPosition(success, error, options);
    }

});
