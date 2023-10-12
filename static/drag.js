/**
 * author levi
 * url http://levi.cg.am
 */
$(function() {
    $(document).mousemove(function(e) {
        console.log('鼠标移动');
        if (!!this.move) {
            var posix = !document.move_target ? {'x': 0, 'y': 0} : document.move_target.posix,
                callback = document.call_down || function() {
                    var y = e.pageY - posix.y;
                    $(this.move_target).css({
                        'top': y < 36 ? 36 : y,
                        'left': e.pageX - posix.x
                    });
                };
            callback.call(this, e, posix);
        }
    }).mouseup(function(e) {
        console.log('鼠标放下');
        if (!!this.move) {
            var callback = document.call_up || function(){};
            callback.call(this, e);
            $.extend(this, {
                'move': false,
                'move_target': null,
                'call_down': false,
                'call_up': false
            });
        }
    });

    $('.window').mousedown(function(e) {
        ToTop(this);
    });

    $('.title').mousedown(function(e) {
        console.log('鼠标点击box');
        var father = this.parentNode;
        var offset = $(father).offset();
        father.posix = {'x': e.pageX - offset.left, 'y': e.pageY - offset.top};
        $.extend(document, {'move': true, 'move_target': father});
    }).parent();
});

function ToTop(win) {
    var wins = document.getElementsByClassName("window");
    var maxZ = 0;
    for (var i = 0; i <  wins.length; i++) {
        var z = parseInt(wins[i].style.zIndex);
        if (z > maxZ) {
            maxZ = z;
        }
    }
    var re = win.style.zIndex >= maxZ;
    win.style.zIndex = maxZ + 1;
    return re;
}

function ShowHideWindow(btm, idx) {
    var win = $(`.window:eq(${idx})`);
    var re = ToTop(win[0]);
    if (!$(win[0]).is(":visible") || re) {
        $(win[0]).toggle();
        $(btm).toggleClass('hide_win');
    }
    if (!$(win[0]).is(":visible")) {
        win[0].style.zIndex = 1;
    }
}
