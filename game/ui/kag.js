var cid = null;
var currentString = null;
var strings = [];

$(document).ready(function() {
    init();
})

function nextString() {
    if(strings == null || strings.length == 0) {
        currentString = null;
        newStrings();
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
    newStrings();
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

function newStrings() {
    $.getJSON("http://localhost:9922/api/strings", function(data) {
        strings = data;
        console.info(strings)
        if(currentString == null) {
            nextString();
        }
    })
}