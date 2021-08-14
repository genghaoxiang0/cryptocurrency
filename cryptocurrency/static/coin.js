/* globals Chart:false, feather:false */

function coinChart() {
  'use strict'
  feather.replace()

  // Graphs
  var ctx = document.getElementById('coinChart')
  // eslint-disable-next-line no-unused-vars
  var myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [
        '',
        '',
        '',
        '',
        '',
        '',
        ''
      ],
      datasets: [{
        data: [
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ],
        lineTension: 0,
        backgroundColor: 'transparent',
        borderColor: '#007bff',  
        borderWidth: 4,
        pointBackgroundColor: '#007bff',
        label: "Price(USD)"
      }]
    },
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: false
          }
        }]
      },
      legend: {
        display: false
      }
    }
  })

  $.getJSON("https://min-api.cryptocompare.com/data/v2/histoday?fsym="+currentTicker+"&tsym=USD&limit=6&api_key=979689f3ab33df3a76d4210693db6f51b5eb93b3ff8f426e78f897339b7d709c", 
      function(result){
        //result.Data.each(function() {
        //  myChart.data.datasets[0].data[i] = result.Data[i].close
        //})
        for (let p in result.Data.Data){
          console.log(result)
          myChart.data.datasets[0].data[p] = result.Data.Data[p].close
          let date = new Date(result.Data.Data[p].time*1000)
          let options = { weekday: 'short', year: 'numeric', month: 'long', day: 'numeric'};

          //myChart.data.labels[p] = date.getMonth() + "/" + date.getDate() +"/"+ date.getFullYear()
          myChart.data.labels[p] = new Intl.DateTimeFormat('en-US', options).format(date)
        }
    });
    //myChart.data.datasets[0].data[0] = 10000;
    myChart.update();
	
	
	setTimeout(function(){
		myChart.update();
	  }, 100);


}

