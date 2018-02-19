// 以图表展示成绩
$(function () {
    $("ul li").click(function () {
        var sid = $('#classList').attr('sid');
        var cid = $(this).attr('cid');

        $.get({
            url: '/crm/app03/student/chart/',
            data: {"sid": sid, "cid": cid},
            dataType: 'json',
            success: function (res_dict) {
                if (res_dict["status"]) {
                    class_name = res_dict["class_name"];
                    data_list = res_dict["data_list"];

                    var chart = Highcharts.chart('chart', {
                        title: {
                            text: '个人成绩折线图'
                        },
                        xAxis: {
                            type: 'category',
                            labels: {
                                rotation: 0,
                                style: {
                                    fontSize: '13px',
                                    fontFamily: 'Verdana, sans-serif'
                                }
                            }
                        },
                        yAxis: {
                            title: {
                                text: '分数'
                            }
                        },
                        legend: {
                            layout: 'vertical',
                            align: 'right',
                            verticalAlign: 'middle'
                        },
                        plotOptions: {
                            series: {
                                label: {
                                    connectorAllowed: false
                                },
                                pointStart: 1
                            }
                        },
                        series: [{"name": class_name, "data": data_list}],
                        responsive: {
                            rules: [{
                                condition: {
                                    maxWidth: 500
                                },
                                chartOptions: {
                                    legend: {
                                        layout: 'horizontal',
                                        align: 'center',
                                        verticalAlign: 'bottom'
                                    }
                                }
                            }]
                        }
                    });
                }
            }
        })
    })
});

