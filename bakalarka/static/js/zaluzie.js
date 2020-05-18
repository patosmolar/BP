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
$("#vertical_sl").on("slideStart", function(slideEvt) {
    $("#vertical_sl_value").val(slideEvt.value);
});
$("#vertical_sl").on("slide", function(slideEvt) {
    $("#vertical_sl_value").val(slideEvt.value);
});
$("#vertical_sl").on("slideStop", function(slideEvt) {
    console.log("aaa");
    pullUp();
});



$("#horizontal_sl").on("slideStart", function(slideEvt) {
    $("#horizontal_sl_value").val(slideEvt.value);
});
$("#horizontal_sl").on("slide", function(slideEvt) {
    $("#horizontal_sl_value").val(slideEvt.value);
});
$("#horizontal_sl").on("slideStop", function(slideEvt) {
    rotate();
});

document.getElementById("vertical_sl_value").value = 100;
document.getElementById("horizontal_sl_value").value = 90;

function integer(number) {
    return Math[number < 0 ? 'ceil' : 'floor'](number);
}

function sendData() {
    vyska = document.getElementById("vertical_sl_value").value;
    uhol = document.getElementById("horizontal_sl_value").value;

}

function rotate() {
    var val = document.getElementById("horizontal_sl_value").value;
    if (val == 0) {
        val = 5;
    }
    val = val - 90;
    var k = "rotateX(" + val + "deg)";
    TweenMax.to(".sheet", 2, { transform: k, ease: Power4 });
}

function pullUp() {
    var val = document.getElementById("vertical_sl_value").value;
    val = 100 - val;
    val = "-" + val + "%";

    var obj = document.getElementById("sheets");
    TweenMax.to(obj, 1, { y: val });



}