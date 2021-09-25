function passCheck() {
    if (document.getElementById("scam").checked == false) {
        document.getElementById("after_scam_p").classList.remove("dnone");
    }
    return false;
}