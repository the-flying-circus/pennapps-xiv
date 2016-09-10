var autocomplete;
var $search;

$(document).ready(function() {
    $("#welcome-div").velocity({top: 0, opacity: 1}, {duration: 600});
    
    $search = $("#search");
    autocomplete = new google.maps.places.Autocomplete(document.getElementById("search"), {type: "geocode"});
    autocomplete.addListener("place_changed", submitAddress);
});

function submitAddress() {
    var place = autocomplete.getPlace();
    window.location = "/info?place_id="+place.place_id+"&query="+$search.val();
}
