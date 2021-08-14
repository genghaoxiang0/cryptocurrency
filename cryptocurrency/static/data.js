/*function getPrice(coinList){
  
  // default source == "CC"
  let obj = JSON.parse(JSON.stringify(coinList));
  console.log(obj);
  //console.log(obj.Data[0]);
  let cList = JSON.parse(JSON.stringify(obj.Data));

  for (i in obj.Data){
    console.log(i);
  }
  $.ajax({
    //url: "/socialnetwork/get-global",
    url: "https://min-api.cryptocompare.com/data/pricemulti?fsyms=ETH,DASH&tsyms=BTC,USD,EUR&api_key=979689f3ab33df3a76d4210693db6f51b5eb93b3ff8f426e78f897339b7d709c",
    dataType : "json",
    success: displayMessage,
    error: displayError
  });
  //alert("g")
}*/
function getPrice(){
  let cList = getCoinList();
  let pList = "";
  for (c in cList){
    let ticker = cList[c];
/*    $.ajax({
      url: "https://min-api.cryptocompare.com/data/price?fsym="+cList[c]+"&tsyms=USD&api_key=979689f3ab33df3a76d4210693db6f51b5eb93b3ff8f426e78f897339b7d709c",
      dataType : "json",
      data: data,
      success: updatePriceList(data,ticker),
      error: displayError
    });*/
    $.getJSON("https://min-api.cryptocompare.com/data/price?fsym="+cList[c]+"&tsyms=USD&api_key=979689f3ab33df3a76d4210693db6f51b5eb93b3ff8f426e78f897339b7d709c",
	function(data){
      updatePriceList(data,ticker);
    });
  }

}

function getOnePrice(){
    $.getJSON("https://min-api.cryptocompare.com/data/price?fsym="+currentTicker+"&tsyms=USD&api_key=979689f3ab33df3a76d4210693db6f51b5eb93b3ff8f426e78f897339b7d709c",
	function(data){
      updatePriceList(data,currentTicker);
    });

}

function getDVolume(coinList){
  let cList = getCoinList();
  for (c in cList){
    let ticker = cList[c];

    $.getJSON("https://min-api.cryptocompare.com/data/v2/histoday?fsym="+cList[c]+"&tsym=USD&limit=10&api_key=979689f3ab33df3a76d4210693db6f51b5eb93b3ff8f426e78f897339b7d709c",
  function(data){
      updateVolumeList(data,ticker);
    });
  }
}

function getDStats(coinList){
  
  $.ajax({
    //url: "/socialnetwork/get-global",
    url: "https://min-api.cryptocompare.com/data/symbol/histoday?fsym=BTC&tsym=USD&limit=10&api_key=979689f3ab33df3a76d4210693db6f51b5eb93b3ff8f426e78f897339b7d709c",
    dataType : "json",
    success: displayMessage,
    error: displayError
  });
  //alert("g")
}

function getCoinList(){
/*  $.ajax({
    url: "https://min-api.cryptocompare.com/data/blockchain/list?api_key=979689f3ab33df3a76d4210693db6f51b5eb93b3ff8f426e78f897339b7d709c",
    dataType : "json",
    success: getPrice,
    error: displayError
  });*/

  let cList = [];
  cList = ["BTC","ETH","LTC","DOGE","LINK","ETC","EXMR","USDT","ZEC","DASH","BCH","ADA","MKR","NMR","KNC","ZRX","DAI","SOLVE","LOOM"]
  return cList;
}

function getNews(){
  
  let cList = getCoinList();
  let nList = "";
  for (c in cList){
    let ticker = cList[c];
/*    if (ticker=="DOGE"){
      break;
    }*/

    $.getJSON("https://min-api.cryptocompare.com/data/v2/news/?lang=EN&categories="+cList[c]+"&api_key=979689f3ab33df3a76d4210693db6f51b5eb93b3ff8f426e78f897339b7d709c",
  function(data){
      updateNewsList(data,ticker);
    });
  }
}

function getIndex(){
  let cList = getCoinList();

  let iList = {};
  iList = {"BTC": 0.1,"ETH": 0.05,"LTC": 0.05,"DOGE": 0.05,"LINK": 0.05,"ETC": 0.05,"EXMR": 0.05,"USDT": 0.05,"ZEC": 0.05,"DASH": 0.05,"BCH": 0.05,"ADA": 0.05,"MKR": 0.05,"NMR": 0.05,"KNC": 0.05,"ZRX": 0.05,"DAI": 0.05,"SOLVE": 0.05,"LOOM": 0.05}
  return iList;
}

function updateIndex(){
}

function updatePrice(response,t){
  if(Array.isArray(response)){
    //alert("upPost")
    updatePriceList(response,t)
  }else if(response.hasOwnProperty('error')){
    displayError(response.error)
  }else{
    displayError(response)
  }
}

function updatePriceList(price,t){
  let priceUSD = price.USD;
  //alert(priceUSD)
  console.log(t)
  if (t == currentTicker) {
	$("#current-price").empty()
	$("#current-price").append("Price: " + priceUSD + "USD")
  }
  $("#"+t).empty()
  $("#"+t).append("$" + priceUSD)
  
  $.ajax({
    url: "/update-price",
    type: "POST",
    //data: "comment="+com_text+"&csrfmiddlewaretoken="+getCSRFToken(),
    data: "price="+priceUSD+"&ticker="+t+"&csrfmiddlewaretoken="+getCSRFToken(),
    dataType: "json"
    });
  
}

function updateNewsList(news,t){
  //let priceUSD = price.USD;
  //console.log(t)
  //console.log(news.Data)
  for(i in news.Data){
    //console.log(news.Data[i].id)
    //console.log(news.Data[i].guid)
    $.ajax({
    url: "/update-news",
    type: "POST",
    data: "news_id="+news.Data[i].id+"&news_link="+news.Data[i].guid+"&news_image="+news.Data[i].imageurl+"&news_title="+news.Data[i].title+"&news_body="+news.Data[i].body+"&news_time="+news.Data[i].published_on+"&ticker="+t+"&csrfmiddlewaretoken="+getCSRFToken(),
    dataType: "json"
    });
  }
  //alert(t)

}


function displayMessage(message){
  console.log(message);
}

function displayError(message){
  console.log("Error Warning:" + message);
}

function myHello(){
  console.log("Hello World!")
}

function homeLoad(){
  getNews();
  getPrice();
}

function getCSRFToken(){
  let cookies = document.cookie.split(";")
  for (let i = 0; i< cookies.length; i++){
    let c = cookies[i].trim()
    if(c.startsWith("csrftoken")){
      return c.substring("csrftoken=".length, c.length)
    }
  }
  return "unknown";
}