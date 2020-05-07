$('#horizontal_sl').slider({
    formatter: function(value) {
        return 'Rotácia: ' + value;
    }

});
$("#vertical_sl").slider({
    orientation: 'vertical',
    tooltip_position: 'right',
    formatter: function(value) {
        return 'Výška: ' + value;
    }
});
$("#vertical_sl").on("slide", function(slideEvt) {
    $("#vertical_sl_value").val(slideEvt.value);
});
$("#horizontal_sl").on("slide", function(slideEvt) {
    $("#horizontal_sl_value").val(slideEvt.value);
});
document.getElementById("vertical_sl_value").value = 50;
document.getElementById("horizontal_sl_value").value = 90;

function sendData() {
    rotate();

}

function rotate() {
    var val = document.getElementById("horizontal_sl_value").value - 90;
    var k = "rotateX(" + val + "deg)";
    console.log(k);
    TweenMax.to(".sheet", 2, { transform: k, ease: Power4 });

}