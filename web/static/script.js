//var DesignDiv = document.getElementById("DesignDiv");
//var MacroDiv = document.getElementById("MacroDiv");
//var EmuDiv = document.getElementById("EmuDiv");
//var ZebuDiv = document.getElementById("ZebuDiv");
//var PldDiv = document.getElementById("PldDiv");
//var ProtiumDiv = document.getElementById("ProtiumDiv");
//var SimuDiv = document.getElementById("SimuDiv");
//var ImageDiv = document.getElementById("ImageDiv");
//var PeripheralDiv = document.getElementById("PeripheralDiv");
//var CheckerDiv = document.getElementById("CheckerDiv");
//var MonitorDiv = document.getElementById("MonitorDiv");
//var ConsoleSet = document.getElementById("console-set");
//var ConsolePre = document.getElementById("console");
//var fileLoad = document.getElementById("fileLoad");
//var svg_div = document.getElementById("svg_div");
//var set_configs = null;
//fileLoad.value = "";

new QWebChannel(qt.webChannelTransport, function(channel) {
    var dataObj = channel.objects.dataObj;

    var svg_div = document.getElementById("svg_div");

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

    async function Init() {
        var data = {};
        try {
            var html = await dataObj.GetHtml();
            var uls = JSON.parse(html);
            data["skt"] = uls["skts"][0];
            data["mode"] = uls["default_mode"];
        } catch (error) {
            console.error("获取html错误:", error);
        }

        try{
            var svg_file = await dataObj.GetSvg(data["skt"]);
            if (svg_file !== null) {
                svg_div.innerHTML = svg_file;
            }
            else {
                console.error("innerHtml lost");
            }
        } catch (error) {
            console.error("获取svg错误:", error);
        }

        BindEvent(uls);

    }

    Init();

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

    window.ChangeSocket = async function(mode) {
        data = {fileContent: $("#preview").html(), skt: $("#socket_select").val()};
        try {
            var re2 = await dataObj.LoadSvg(data);
        } catch (error) {
            console.error("changeSocket:", error);
        }
        svg_div.innerHTML = re2;
        BindSvgEvent();

        //DoAjax("cgi-bin/server.py?LoadSvg", JSON.stringify(data), function(re2) {
        //    svg_div.innerHTML = re2;
        //    BindSvgEvent();
        //});
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

    function BindEvent(uls) {
        document.getElementById("socket_select").innerHTML = uls["sockets"];
        MacroDiv.innerHTML = uls["macroUl"];
        EmuDiv.innerHTML = uls["emu"];
        ZebuDiv.innerHTML = uls["zebu"];
        PldDiv.innerHTML = uls["pld"];
        ProtiumDiv.innerHTML = uls["protium"];
        SimuDiv.innerHTML = uls["simu"];
        ImageDiv.innerHTML = uls["image"];
        PeripheralDiv.innerHTML = uls["peripheral"];
        CheckerDiv.innerHTML = uls["checker"];
        MonitorDiv.innerHTML = uls["monitor"];
        var BaremetalConfig = document.getElementById("BaremetalConfig");
        BaremetalConfig.outerHTML = uls["BaremetalConfig"];
        DesignDiv.innerHTML = uls["treeUl"];
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
                try {
                    var selt = document.getElementById(selId);
                } catch (error) {
                    console.error('selId:', error);
                }
                ChangeConfig(selt, valOld, this.dataset.value, true);
                break;
            }
        });
    }

    async function ChangeConfig(selt, valOld, valNew, fromSvg) {
        var data = {};
        data.config = {};
        data.configs = GetConfigMap(false);
        data.config[selt.id] = valNew;

        try {
            var getlog = await dataObj.GetLog(data);
        } catch (error) {
            console.error("GetLog失败:",error);
        }

        var res = JSON.parse(getlog);
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

    var fileSave = document.getElementById("fileSave");
    var fileLoad = document.getElementById("fileLoad");
    var overwrite = document.getElementById("overwrite");
    window.SaveConfig = async function() {
        var data = {};
        data.fileName = fileSave.value;
        data.configs = GetConfigMap(true);
        data.overwrite = overwrite.checked;
        data.CompileOption = $("#CompileOption").val();

        try {
            var re = await dataObj.Save(data);
        } catch (error) {
            console.error("save配置文件:", error);
        }
        var res = JSON.parse(re);
        alert(res.message);
    }

    window.pyqtLoadConfig = async function (configs_str) {
        try {
            var re1 = await dataObj.LoadHtml(configs_str);
        } catch (error) {
            console.error("Load配置文件2:", error);
        }
        var uls = JSON.parse(re1);
        data = {fileContent: configs_str, skt: uls["skts"][0]};

        try {
            var re2 = await dataObj.LoadSvg(data);
        } catch (error) {
            console.error("Load配置文件2:", error);
        }
        svg_div.innerHTML = re2;
        BindEvent(uls);
    }

    window.LoadConfig = async function () {
        var ext = fileLoad.value.split(/[.,/,\\]/).slice(-2, -1);
        var reader = new FileReader();

        reader.onload = async function() {
            //alert(reader.result);
            try {
                var re1 = await dataObj.LoadHtml(reader.result);
            } catch (error) {
                console.error("Load配置文件2:", error);
            }
            var uls = JSON.parse(re1);
            data = {fileContent: reader.result, skt: uls["skts"][0]};

            try {
                var re2 = await dataObj.LoadSvg(data);
            } catch (error) {
                console.error("Load配置文件2:", error);
            }
            svg_div.innerHTML = re2;
            fileSave.value = ext;
            BindEvent(uls);

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

});


function test() {
    pyqtLoadConfig("1111");
}