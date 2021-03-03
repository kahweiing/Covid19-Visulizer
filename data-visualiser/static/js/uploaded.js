
var clicked = true;

$(document).ready(function() {
    //Register toggle event handler
    var toggler = document.getElementsByClassName("slider")[0];
    toggler.addEventListener("click", registerToggleEvent);

});

function registerToggleEvent() {
    var chart = document.getElementById("chartrow");
    var table = document.getElementById("tablerow");
    if (clicked) {
        chart.style.display = "block";
        table.style.display = "none"
        clicked = false;
    } else {
        chart.style.display = "none";
        table.style.display = "block"
        clicked = true;
    }
}