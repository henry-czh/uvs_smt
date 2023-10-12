var DesignDiv = document.getElementById("DesignDiv");
var MacroDiv = document.getElementById("MacroDiv");
var EmuDiv = document.getElementById("EmuDiv");
var ZebuDiv = document.getElementById("ZebuDiv");
var PldDiv = document.getElementById("PldDiv");
var ProtiumDiv = document.getElementById("ProtiumDiv");
var SimuDiv = document.getElementById("SimuDiv");
var ImageDiv = document.getElementById("ImageDiv");
var PeripheralDiv = document.getElementById("PeripheralDiv");
var CheckerDiv = document.getElementById("CheckerDiv");
var MonitorDiv = document.getElementById("MonitorDiv");
var ConsoleSet = document.getElementById("console-set");
var ConsolePre = document.getElementById("console");
var fileLoad = document.getElementById("fileLoad");
var svg_div = document.getElementById("svg_div");
var set_configs = null;
fileLoad.value = "";

/*
function ChangeMode(mode) {
    Init(mode);
}
*/

function ChangeSocket(mode) {
    data = {fileContent: $("#preview").html(), skt: $("#socket_select").val()};
    DoAjax("cgi-bin/server.py?LoadSvg", JSON.stringify(data), function(re2) {
        svg_div.innerHTML = re2;
        BindSvgEvent();
    });
}

function SetSvgVal(id, val) {
    var oldId = "unit_" + $("#socket_select").val() + "_";
    id = id.replace(oldId, "unit_:_");
    var rect = document.querySelector("[data-config='"+id+"']");
    if (rect == null) return;
    rect.dataset.value = val;
}

function GetConfigMap(is_save) {
    set_configs = document.querySelectorAll("select,input,textarea");
    var configs = {};
    for (var j = 0; j < set_configs.length; j++) {
        if (is_save && set_configs[j].id && !set_configs[j].classList.contains("set")) continue;
        configs[set_configs[j].id] = set_configs[j].value;
    }
    return configs;
}

new QWebChannel(qt.webChannelTransport, function(channel) {
    var dataObj = channel.objects.dataObj;

    // 设置数据到Python
    window.setDataToPython = function() {
        var newData = "11111111Data from JavaScript";
        alert(newData)
        dataObj.setData(newData);
    };

    // 从Python获取数据
    window.getDataFromPython = async function() {
        try {
            var data = await dataObj.getData();
            svg_div.innerHTML = data;
        } catch (error) {
            console.error("获取数据时出错:", error);
        }
    };

});

function Init() {
    var data = {};
    DoAjax("cgi-bin/server.py?GetHtml", JSON.stringify(data), function(re1) {
        var uls = JSON.parse(re1);
        data["skt"] = uls["skts"][0];
        data["mode"] = uls["default_mode"];
        DoAjax("cgi-bin/server.py?GetSvg", JSON.stringify(data), function(re2) {
            svg_div.innerHTML = re2;
            BindEvent(uls);
        });
    });
}
Init();

function BindEvent(uls) {
    if (uls["mess"].startsWith("<i>[Error]</i>")) {
        ConsolePre.innerHTML += re.trim() + "\n";
        ConsoleSet.scrollTo(0, ConsoleSet.scrollHeight);
        return;
    }
    //// document.getElementById("mode_select").innerHTML = uls["modes"];
    //document.getElementById("socket_select").innerHTML = uls["sockets"];
    //DesignDiv.innerHTML = uls["treeUl"];
    //MacroDiv.innerHTML = uls["macroUl"];
    //EmuDiv.innerHTML = uls["emu"];
    //ZebuDiv.innerHTML = uls["zebu"];
    //PldDiv.innerHTML = uls["pld"];
    //ProtiumDiv.innerHTML = uls["protium"];
    //SimuDiv.innerHTML = uls["simu"];
    //ImageDiv.innerHTML = uls["image"];
    //PeripheralDiv.innerHTML = uls["peripheral"];
    //CheckerDiv.innerHTML = uls["checker"];
    //MonitorDiv.innerHTML = uls["monitor"];
    //var BaremetalConfig = document.getElementById("BaremetalConfig");
    //BaremetalConfig.outerHTML = uls["BaremetalConfig"];
    //ConsolePre.innerHTML += uls["mess"].trim() + "\n";
    //ConsoleSet.scrollTo(0, ConsoleSet.scrollHeight);
 
    $("span").click(function() {
        var span = this;
        var select = this.nextElementSibling;
        var ul = this.parentElement.lastElementChild;
        if (select.tagName == "UL" || select.value == "D" || select.value == "G") {
            if (ul.tagName != "UL") {
                return;
            }
            span.classList.toggle("caret-down");
            ul.classList.toggle("show");
        }
        if (ul.tagName != "UL") {
            return;
        }
        var nextSpan =  ul.firstElementChild.firstElementChild;
        var nextUl =  ul.firstElementChild.children[1];
        while (nextUl.tagName == "UL") {
            nextSpan.classList.add("caret-down");
            nextUl.classList.add("show");
            nextSpan = nextUl.firstElementChild.firstElementChild;
            nextUl = nextUl.firstElementChild.children[1];
        }
    });

    $(".window legend").click(function() {
        $(this).nextAll().toggle();
    });

    $(".config_tr select").each(function () {
        this.dataset.preval = this.value;
    });

    $(".config_tr select").change(function() {
        ChangeConfig(this, this.dataset.preval, this.value, false);
    });

    BindSvgEvent();

    SetConfig();
    // ChangeWin();
}

function BindSvgEvent() {
    $("[data-config]").click(function(e) {
        e.stopPropagation(); //防止子元素被点击，父元素也会有点击事件
        var vals = JSON.parse(this.dataset.values);
        for (var i in vals) {
            if (parseInt(i) != vals.length - 1 && vals[i] != this.dataset.value) continue;
            var idx = (parseInt(i)+1)%vals.length
            var valOld = this.dataset.value;
            this.dataset.value = vals[idx.toString()];
            var selId = this.dataset.config.replace(":", $("#socket_select").val());
            var selt = document.getElementById(selId);
            ChangeConfig(selt, valOld, this.dataset.value, true);
            break;
        }
    });
}

function ChangeConfig(selt, valOld, valNew, fromSvg) {
    var data = {};
    data.config = {};
    data.configs = GetConfigMap(false);
    data.config[selt.id] = valNew;
    DoAjax("cgi-bin/server.py?getlog", JSON.stringify(data), function(re) {
        var res = JSON.parse(re);
        ConsolePre.innerHTML += res.message.trim() + "\n";
        ConsoleSet.scrollTo(0, ConsoleSet.scrollHeight);
        if (!res.success) {
            selt.value = valOld;
            SetSvgVal(selt.id, valOld);
            return;
        }
        for (var c in res.depend_change) {
            ChangeSelect(c, res.depend_change[c]);
        }
        for (var c in res.depend_change_multiple) {
            ChangeSelect(c, res.depend_change_multiple[c][0]);
        }
        ChangeSelect(selt.id, valNew);
        if (Object.keys(res.depend_change_multiple).length != 0) {
            MultipleDepend(res.depend_change_multiple);
        }
        SetConfig();
    });
}

function ChangeSelect(id, val) {
    var sel = $('#'+id);
    sel.val(val);
    sel.attr("data-preval", val)
    sel.addClass("set");
    var ul = sel[0].parentElement.lastElementChild;
    if (ul.tagName == "UL" && (val == "D" || val == "G")) {
        sel.prev().addClass("caret");
        SetUl(ul);
    } else {
        sel.prev().removeClass("caret");
        RmSet(ul);
    }
    SetSvgVal(id, val);
}

function SetUl(ul) {
    // ul.classList.add("show");
    var ul_selects = ul.getElementsByTagName("select");
    for (var i = 0; i < ul_selects.length; i++) {
        ul_selects[i].classList.add("set");
    }
}

function RmSet(el) {
    el.classList.remove("show");
    var slcts = el.getElementsByTagName("select");
    for (var i = 0; i < slcts.length; i++) {
        slcts[i].classList.remove("set");
    }
}

var preview = document.getElementById("preview");
function SetConfig() {
    set_configs = document.querySelectorAll(".set");
    for (var i in set_configs) {
        if (set_configs[i].value == "N" || set_configs[i].value == "S" || set_configs[i].value == "V") {
            var ul = set_configs[i].parentElement.lastElementChild;
            if (ul.tagName == "UL") {
                RmSet(ul);
            }
        }
    }
    var text = "";
    for (var i = 0; i < set_configs.length; i++) {
        //判断是否在显示 : set_configs[i].offsetParent == null
        if (!set_configs[i].className.includes("set")) {
            continue;
        }
        text += set_configs[i].id + " = " + set_configs[i].value + "\n";
    }
    preview.innerHTML = text;
}

var fileSave = document.getElementById("fileSave");
var fileLoad = document.getElementById("fileLoad");
var overwrite = document.getElementById("overwrite");
function SaveConfig() {
    var data = {};
    data.fileName = fileSave.value;
    data.configs = GetConfigMap(true);
    data.overwrite = overwrite.checked;
    data.CompileOption = $("#CompileOption").val();
    DoAjax("cgi-bin/server.py?save", JSON.stringify(data), function(re) {
        var res = JSON.parse(re);
        alert(res.message);
    });
}

function LoadConfig() {
    var ext = fileLoad.value.split(/[.,/,\\]/).slice(-2, -1);
    var reader = new FileReader();
    reader.onload = function() {
        //alert(reader.result);
        DoAjax("cgi-bin/server.py?LoadHtml", reader.result, function(re1) {
            var uls = JSON.parse(re1);
            data = {fileContent: reader.result, skt: uls["skts"][0]};
            DoAjax("cgi-bin/server.py?LoadSvg", JSON.stringify(data), function(re2) {
                svg_div.innerHTML = re2;
                fileSave.value = ext;
                BindEvent(uls);
            });
        });
        fileLoad.value = "";
    }
    reader.readAsText(fileLoad.files[0]);
}

var secondUl = document.getElementById("second-ul");

function MultipleDepend(mds) {
    var ulHtml = '';
    for (var md in mds) {
        ulHtml += '<li><span>' + md + '</span><select data-id=' + md + '>';
        for (var i = 0; i < mds[md].length; i++) {
            ulHtml += '<option>' + mds[md][i] + '</option>';
        }
        ulHtml += '</select></li>';
    }
    $("#second-ul").html(ulHtml);
    $("section").show();
}

function MultipleSubmit() {
    // var sels = document.getElementById("second-ul").getElementsByTagName("select");
    var sels = document.querySelectorAll("#second-ul select");
    for (var i = 0; i < sels.length; i++) {
        var id = sels[i].dataset.id;
        $('#'+id).val(sels[i].value);
        SetSvgVal(id, sels[i].value);
    }
    $("section").hide();
    SetConfig();
}
