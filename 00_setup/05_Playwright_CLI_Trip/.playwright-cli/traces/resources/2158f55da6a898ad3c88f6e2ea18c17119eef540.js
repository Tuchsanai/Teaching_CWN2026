var isDesktop = function (ua) {
    return isContains(ua, "wow64") || isContains(ua, ".net clr") || isContains(ua, "gtb7") || isContains(ua, "macintosh") || isContains(ua, "slcc1") || isContains(ua, "gtb6") || isContains(ua, "funwebproducts") || isContains(ua, "aol 9.") || isContains(ua, "iceweasel") || isContains(ua, "epiphany") || isContains(ua, "gtb8")
};
var isMobile = function (ua) {
    return (isContains(ua, "midp") || isContains(ua, "mobile") || isContains(ua, "nokia") || isContains(ua, "up.browser") || isContains(ua, "phone") || isContains(ua, "opera mini") || isContains(ua, "opera mobi") || isContains(ua, "brew") || isContains(ua, "sonyericsson") || isContains(ua, "blackberry") || isContains(ua, "netfront") || isContains(ua, "uc browser") || isContains(ua, "symbian") || isContains(ua, "j2me") || isContains(ua, "wap2.") || isContains(ua, "up.link") || isContains(ua, "windows ce") || isContains(ua, "vodafone") || isContains(ua, "ucweb") || isContains(ua, "zte-") || isContains(ua, "docomo") || isContains(ua, "armv") || isContains(ua, "maemo") || isContains(ua, "palm") || isContains(ua, "bolt") || isContains(ua, "fennec") || isContains(ua, "wireless") || isContains(ua, "adr-") || isContains(ua, "htc") || isContains(ua, "nintendo") || isContains(ua, "zunewp7") || isContains(ua, "skyfire") || isContains(ua, "silk") || isContains(ua, "untrusted") || isContains(ua, "lgtelecom") || isContains(ua, " gt-") || isContains(ua, " arm;") || isContains(ua, "ventana") || isContains(ua, "iphone") || isContains(ua, "ipod") || isContains(ua, "itouch") || (isContains(ua, "mqqbrowser") && isContains(ua, "adr")) || (isContains(ua, "firefox") && isContains(ua, "android")) || (isContains(ua, "firefox") && isContains(ua, "mobile")) || isContains(ua, "windowsphone") || isContains(ua, "windows phone") || isContains(ua, "iemobile") || isContains(ua, "wp7") || isContains(ua, "wp8") || isContains(ua, "android 2") || isContains(ua, "android 3") || isContains(ua, "android 4") || isContains(ua, "android 5") || isContains(ua, "android/2") || isContains(ua, "android/3") || isContains(ua, "android/4") || isContains(ua, "android/5"))
};
var isPad = function (ua) {
    return isContains(ua, "ipad") || isContains(ua, "lepad_")
};

function isContains(str, substr) {
    return new RegExp(substr).test(str)
};