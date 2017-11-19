var cid = null;
var currentString = null;
var strings = [];

$(document).ready(function() {
    init();
})

function nextString() {
    if(strings == null || strings.length == 0) {
        currentString = null;
        fetchStrings();
        return;
    }
    currentString = strings[0];
    $("#text").text(currentString.target);
    strings = strings.slice(1);
}

function init() {
    if(Cookies.get("kaid") === undefined) {
        cid = ("" + Math.random()).slice(2) // long number
        Cookies.set("id", cid);
    }
    fetchStrings();
    // Swipe event
    var body = document.getElementsByTagName("body")[0]
    var hammer    = new Hammer.Manager(body);
    var swipe     = new Hammer.Swipe();

    hammer.add(swipe);

    hammer.on('swipeleft', function(){
        console.log("Swipe left");
        thumbUp();
    });

    hammer.on('swiperight', function(){
        console.log("Swipe right");
        thumbDown();
    });
}

function submit(yn) {
    json = {"client": cid, "string": currentString.id, "score": yn ? 1 : -1}
    $.post("http://localhost:9922/api/submit", json, function(data) {
        console.log("Submitted", json);
    })
}

function thumbUp() {
    submit(true);
    nextString();
}

function thumbDown() {
    submit(false);
    nextString();
}

function fetchStrings() {
    $.getJSON("http://localhost:9922/api/strings", function(data) {
        strings = data;
        console.info(strings)
        if(currentString == null) {
            nextString();
        }
    })
}