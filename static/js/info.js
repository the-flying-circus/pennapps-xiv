$(document).ready(function() {
    $(".timeago").timeago();
    
    var sr = ScrollReveal();
    sr.reveal(".property-img, .map, .card", {duration: 1000});
});
