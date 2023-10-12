/*******↓*我的 ajax*↓*******/
function DoAjax0(url, onsuccess) {
    $.ajax({
        url: url,
        type: "get",
        success: onsuccess,
        error: function (re) {
            alert("get error: " + re.status);
        }
    });
}

function DoAjax(url, data, onsuccess) {
    $.ajax({
        // headers: {
        //     Accept: "text/plain"
        // },
        url: url,
        data: data,
        type: "post",
        // dataType: "json",
        // contentType: "application/json",
        success: onsuccess,
        error: function (re) {
            alert("post error: " + re.status);
        }
    });
}

/*******↓*获取 url 参数*↓*******/
function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [, ""])[1].replace(/\+/g, '%20')) || null;
}

/*******↓*有关时间*↓*******/
function StringToDate(str) {
    return new Date(str);
}
function DateToString(date) {
    date = new Date(date);
    date = new Date(date.getTime() + 8 * 3600 * 1000); //格林尼治时区差8小时
    return date.toISOString().slice(0,10);
}
function DateAddDays(date, days) {
    return date.setDate(date.getDate() + days);
}
function StringAddDays(date_str, days) {
    var date = StringToDate(date_str);
    date.setDate(date.getDate() + days);
    return date.toISOString().slice(0,10);
}

/*******↓*Array去重*↓*******/
function unique(array) {
    var res = [];
    for (var i = 0, len = array.length; i < len; i++) {
        var current = array[i];
        if (res.indexOf(current) == -1) {
            res.push(current)
        }
    }
    return res;
}
