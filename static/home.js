const backendAPI = 'http://127.0.0.1:5000/'
const $homePage = $('#homepage')
const $DJI = $('#DJI')
const $SP500 = $('#SP500')
const $NASDAQ = $('#NASDAQ')
const $news = $('#news')
const $dailyClose = $('#dailyClose')
const exclude = ['name', 'symbol', 'exchange', 'eps', 'marketCap', 'pe']

//function to display data sent back from backend
function displayMarketData(area,data,exclude){
    for (const [key,value] of Object.entries(data)){
        if (!exclude.includes(key)){
            area.append(`<p> ${key} : ${value}</p>`)
        }
    }
    $dailyClose.append(`<h4> ${data['name']} : ${data['price']}`)
    $dailyClose.append(`<h6> Change: ${data['change']} </h6>`)
    $dailyClose.append('<br><br>')
}

//functions to call backend routes

async function marketIndexData(){
    //makes back-end call to our market-index-data route which will pull up data from the index route in financialmodeling api
    const res = await axios.post(`${backendAPI}/market-index-data`)

    //sends index data to our handling route which will append various portions of the big 3 indexes to create homepag
    return handleMarketData(res)
}

async function getMarketNews(){
    const res = await axios.post(`${backendAPI}/market-news`)

    return handleMarketNews(res)
}

marketIndexData()
getMarketNews()

function handleMarketNews(res){
    $news.html('')

    data = res['data']

    $news.append('<h3> News: </h3>')
    for (i = 0; i < data.length; i++){
        $news.append(`<a target='_blank' href= '${data[i]['url']}'> ${data[i]['title']} </a> <br><br><br>`)
    }
}

function handleMarketData(res){

    data = res['data']

    // looks through array of dictionaries looking at 'symbol' key until it matches symbol for Dow Jones Index
    for (i = 0; i<data.length; i++){
        if (data[i]['symbol'] === '^DJI'){
            let dow = data[i]
            $DJI.html('')
            $DJI.append(`<h3> ${dow['name']} </h3>`)
            //once DJI dictionary has been found, looks through keys to create similar div section to ticker page using displayMarketData()
            //function
            displayMarketData($DJI, dow, exclude)
        }
        if (data[i]['symbol'] === '^SP500TR'){
            let sp500 = data[i]
            $SP500.html('')
            $SP500.append(`<h3> ${sp500['name']} </h3>`)
            displayMarketData($SP500, sp500, exclude)
        }
        if (data[i]['symbol'] === '^IXIC'){
            let nasdaq = data[i]
            $NASDAQ.html('')
            $NASDAQ.append(`<h3> ${nasdaq['name']} </h3>`)
            displayMarketData($NASDAQ, nasdaq, exclude)
        }
    }

}