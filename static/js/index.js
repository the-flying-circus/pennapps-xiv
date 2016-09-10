var autocomplete;
var $search;

$(document).ready(function() {
    $("#welcome-div").velocity({top: 0, opacity: 1}, {duration: 600});

    $search = $("#search");
    autocomplete = new google.maps.places.Autocomplete(document.getElementById("search"));
    autocomplete.setTypes(["address"]);
    autocomplete.addListener("place_changed", submitAddress);
});

function start_preloader() {
    $(".preloader-wrapper").addClass("active");
}

if (!Array.prototype.includes) {
    Array.prototype.includes = function(searchElement /*, fromIndex*/) {
        'use strict';
        if (this == null) {
            throw new TypeError('Array.prototype.includes called on null or undefined');
        }

        var O = Object(this);
        var len = parseInt(O.length, 10) || 0;
        if (len === 0) {
            return false;
        }
        var n = parseInt(arguments[1], 10) || 0;
        var k;
        if (n >= 0) {
            k = n;
        } else {
            k = len + n;
            if (k < 0) {k = 0;}
        }
        var currentElement;
        while (k < len) {
            currentElement = O[k];
            if (searchElement === currentElement ||
                    (searchElement !== searchElement && currentElement !== currentElement)) { // NaN !== NaN
                return true;
            }
            k++;
        }
        return false;
    };
}

function submitAddress() {
    var place = autocomplete.getPlace();
    if (place.types.includes("geocode") || place.types.includes("address") || place.types.includes("street_address")) {
        window.location = "/info?place_id=" + encodeURIComponent(place.place_id) + "&query=" + encodeURIComponent($search.val());
    }
}
