/*
 * Bootstrap Cookie Alert by Wruczek
 * https://github.com/Wruczek/Bootstrap-Cookie-Alert
 * Released under MIT license
 */

// Functions from w3 ---



function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
        c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
        }
    }
    return "";
    }


 

function checkCookie(){
    var cookieEnabled = navigator.cookieEnabled;
    acceptCookies = getCookie("acceptCookies")
    acceptCookies = acceptCookies != ""

    return cookieEnabled && acceptCookies;
}

   

function acceptCookie(){
    if (!navigator.cookieEnabled){
        alert("Please enable the cookies from your browser settings.");
        return;

    }


    const d = new Date();
    d.setTime(d.getTime() + (365*24*60*60*1000));
    let expires = "expires="+ d.toUTCString();
    document.cookie = "acceptCookies" + "=" + true + ";" + expires + ";path=/";
}



function setCookie(cname, cvalue, exdays , flash) {

    
    if (!checkCookie()){
        if (flash){
            alert("Please enable the cookies!")
        }
        return;
    }

    const d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    let expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
  }

function deleteCookie(cname) {
    const d = new Date();
    d.setTime(d.getTime() - 1000);
    let expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + "" + ";" + expires + ";path=/";
  }



(function () {
    "use strict";

    var cookieAlert = document.querySelector(".cookiealert");
    var acceptCookies = document.querySelector(".acceptcookies");

    if (!cookieAlert) {
       return;
    }

    cookieAlert.offsetHeight; // Force browser to trigger reflow (https://stackoverflow.com/a/39451131)

    // Show the alert if we cant find the "acceptCookies" cookie
    if (!getCookie("acceptCookies")) {
        cookieAlert.classList.add("show");
    }

    // When clicking on the agree button, create a 1 year
    // cookie to remember user's choice and close the banner
    acceptCookies.addEventListener("click", function () {
        acceptCookie()
        cookieAlert.classList.remove("show");

        // dispatch the accept event
        window.dispatchEvent(new Event("cookieAlertAccept"))
    });
})();