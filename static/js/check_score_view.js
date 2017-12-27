$(function () {
    $("ul li").click(function () {
        var sid = $('#classList').attr('sid');
        var cid = $(this).attr('cid');

        $.get({
            url: '/crm/app03/student/chart/',
            data: {"sid": sid, "cid": cid},
            dataType: 'json',
            success: function (data) {
                // console.log(data);
                alert('展示图表功能未完成');
            }
        })
    })
});

