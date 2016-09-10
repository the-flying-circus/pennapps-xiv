$(document).ready(function() {
    $(".timeago").timeago();

    var sr = ScrollReveal();
    sr.reveal(".property-img, .map, .card");
    var chart_data = JSON.parse($("#school-data").text());
    $.each(["math", "science", "english"], function(k, v) {
        new Chart($("#chart-" + v)[0].getContext("2d"), {
            type: "pie",
            data: {
                labels: ["Advanced", "Proficient", "Basic", "Failing"],
                datasets: [
                    {
                        data: chart_data[v],
                        backgroundColor: [
                            "#66BB6A",
                            "#36A2EB",
                            "#FFCE56",
                            "#FF6384"
                        ]
                    }
                ]
            },
            maintainAspectRatio: true
        });
    });
});
