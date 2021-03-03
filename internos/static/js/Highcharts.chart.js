
function formatNumber(num) {
  return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,')
}

function tooltipFormatter(obj, unit){

  var index = obj.point.index;
  var current_value = parseFloat(obj.series.data[index].y);
  var previous_value = 0;
  if(index > 0) {
      previous_value = parseFloat(obj.series.data[index - 1].y);
  }

  var difference_value = Number((((current_value - previous_value) / current_value) * 100).toFixed(2));

  var html = '<b>'+obj.series.name+'</b><br>' +
              new Date(obj.x).toDateString() +': '+ formatNumber(obj.y)+ unit + ' <br>' +
              difference_value + ' %';

  return html;

}

function formatData(data) {

    var new_series = [];
    $(data).each(function(i, item){
        new_data = []
        $(item.data).each(function(j, item1){
            new_data[j] = [Date.UTC(item1[0], item1[1]-1, item1[2]), item1[3]]
        });

        new_series[i] = {
          name: item.name,
          data: new_data
        }
    });

    return new_series;
}

function createChart(data, container, title, subtitle, yTitle, xTitle, unit) {

    var series = formatData(data);

    Highcharts.chart(container, {

        title: {
            text: title
        },

        subtitle: {
            text: subtitle
        },

        yAxis: {
            title: {
                text: yTitle
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                month: '%e. %b',
                year: '%b'
            },
            title: {
                text: 'Date'
            }
        },
        tooltip: {
            <!--headerFormat: '<b>{series.name}</b><br>',-->
            <!--pointFormat: '{point.x:%e. %b}: {point.y:.2f} '+unit,-->
            <!--animation: true,-->
            <!--followPointer: true,-->
            formatter: function() {
                return tooltipFormatter(this, unit);
            }
        },

        <!--legend: {-->
            <!--layout: 'vertical',-->
            <!--align: 'right',-->
            <!--verticalAlign: 'middle'-->
        <!--},-->

        plotOptions: {
            series: {
                label: {
                    connectorAllowed: false
                },
               marker: {
                    enabled: true
                },
                allowPointSelect: true,
            },
            <!--line: {-->
                <!--dataLabels: {-->
                    <!--enabled: true-->
                <!--}-->
            <!--},-->
        },

        series: series,

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
