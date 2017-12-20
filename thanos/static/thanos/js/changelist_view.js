// 多选框的全选、反选
$("#checkbox").click(function () {
    $(":checkbox:not(#checkbox)").prop('checked', $(this).prop('checked'));
});