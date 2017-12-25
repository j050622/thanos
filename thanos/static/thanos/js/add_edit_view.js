// popUp弹出窗口
function popUp(url) {
    var popupPage = window.open(url, url, "status=1, height:500, width:600, toolbar=0, resizeable=0");
}

// popUp回调函数
function popUpcallback(popback_info) {
    if (popback_info["status"]) {
        var $option = $("<option>").prop('selected', true).html(popback_info['text']).val(popback_info['value']);
        $("#" + popback_info['popback_id']).append($option);
    }
}