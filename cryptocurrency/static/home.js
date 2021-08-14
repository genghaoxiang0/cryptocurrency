/* globals Chart:false, feather:false */

/*(function () {
  'use strict'

  feather.replace()

  // Graphs
  var ctx = document.getElementById('myChart').getContext('2d')
  // eslint-disable-next-line no-unused-vars
  var myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [
        'Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday'
      ],
      datasets: [{
        data: [
          17,
          21345,
          18483,
          24003,
          23489,
          24092,
          12034
        ],
        lineTension: 0,
        backgroundColor: 'transparent',
        borderColor: '#007bff',  
        borderWidth: 4,
        pointBackgroundColor: '#007bff'
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

  myChart.data.datasets[0].data[0] = 10000;
  myChart.update();
})()*/

function drawIndex(){
  'use strict'

  feather.replace()

  // Graphs
  var ctx = document.getElementById('myChart').getContext('2d')
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
        label: 'ETF Index',
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
        pointBackgroundColor: '#007bff'
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

  

    let iList = {"BTC": 0.075,"ETH": 0.075,"LTC": 0.05,"DOGE": 0.05,"LINK": 0.05,"ETC": 0.05,"EXMR": 0.05,"USDT": 0.05,"ZEC": 0.05,"DASH": 0.05,"BCH": 0.05,"ADA": 0.05,"MKR": 0.05,"NMR": 0.05,"KNC": 0.05,"ZRX": 0.05,"DAI": 0.05,"SOLVE": 0.05,"LOOM": 0.05}
    for (let i in iList){
      $.getJSON("https://min-api.cryptocompare.com/data/v2/histoday?fsym="+i+"&tsym=USD&limit=6&api_key=979689f3ab33df3a76d4210693db6f51b5eb93b3ff8f426e78f897339b7d709c", 
      function(result){
        //result.Data.each(function() {
        //  myChart.data.datasets[0].data[i] = result.Data[i].close
        //})
        for (let p in result.Data.Data){
          //console.log(result)
          if (i == "BTC"){
            myChart.data.datasets[0].data[p] = result.Data.Data[p].close * iList[i]
          }
          else{
            myChart.data.datasets[0].data[p] += result.Data.Data[p].close * iList[i]
          }
          let date = new Date(result.Data.Data[p].time*1000)
          let options = { weekday: 'short', year: 'numeric', month: 'long', day: 'numeric'};

          //myChart.data.labels[p] = date.getMonth() + "/" + date.getDate() +"/"+ date.getFullYear()
          myChart.data.labels[p] = new Intl.DateTimeFormat('en-US', options).format(date)
        }
    });
    }
    //myChart.data.datasets[0].data[0] = 10000;
    myChart.update();
	
	setTimeout(function(){
		myChart.update();
	  }, 100);

}


