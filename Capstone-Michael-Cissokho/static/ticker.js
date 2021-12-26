const $incomeStatement = $('#incomeStatement')
const $balanceSheet = $('#balanceSheet')
const $cashFlowStatement = $('#cashFlowStatement')
const $profile = $('#profile')
const $recent = $('#recent')

let backendAPI = 'http://127.0.0.1:5000'
const $tickerForm = $('.tickerForm')
const $description = $('#description')
const $keyFinancials = $('#keyFinancials')

$tickerForm.on('submit', function(e){
    e.preventDefault();
    const data = new FormData($tickerForm[0]);
    const ticker = data.get('ticker').toUpperCase();
    console.log(ticker)
    $keyFinancials.html('')
    $keyFinancials.append(`<h2> Key Financials: ${ticker} </h2>`)
    profileData(ticker)
    incomeStatementData(ticker)
    balanceSheetData(ticker)
    cashFlowStatementData(ticker)
    historicalPriceData(ticker)
    return
  });

function displayTickerData(area,data,exclude){
    for (const [key,value] of Object.entries(data)){
        if (!exclude.includes(key)){
            area.append(`<p> ${key} : ${value}</p>`)
        }
    }
}

////////////////////////////////////////////////////////////////////////////////////////
//backend calls

async function profileData(ticker){
    //send api to backend to make request to external API and pull profile data
    // backend will send profile data back here to be displayed via DOM manipulation

    const res = await axios.post(`${backendAPI}/profile-data`, {
        ticker: ticker
    })

    return handleProfileData(res)
}

async function incomeStatementData(ticker){
    // purpose of this function is to make a post request to our back-end server with the following parameters
    // backend server will make request to public API and send data back which we receive as "res"
    const res = await axios.post(`${backendAPI}/income-statement-data`, {
            limit: 1,
            ticker: ticker
    })

    // send "res" to our 'handleResponse' function which will submit convert the received data that we got from backend server
    // to actual manipulate the DOM and create an interface for our users to see the data
    return handleIncomeStatement(res)
}

async function balanceSheetData(ticker){

    const res = await axios.post(`${backendAPI}/balance-sheet-statement-data`, {
            limit: 1,
            ticker: ticker
    })
    console.log(res)

    return handleBalanceSheet(res)
}

async function cashFlowStatementData(ticker){
    const res = await axios.post(`${backendAPI}/cash-flow-statement-data`, {
            limit: 1,
            ticker: ticker
    })

    return handleCashFlowStatement(res)
}

async function historicalPriceData(ticker){
    const res = await axios.post(`${backendAPI}/historical-price-data`, {
            ticker: ticker
    })

    return handleHistoricalPriceData(res)
}





//////////////////////////////////////////////////////////////////////////////////////////////////
// handle functions

function handleProfileData(res){
    $profile.html('')

    let data = res['data']

    let exclude = ['cik', 'cusip', 'defaultImage', 'image','isin','website', 'changes']

    $profile.append(`<h3> About: ${data['symbol']} </h3>`)
    displayTickerData($profile, data, exclude)
}

function handleIncomeStatement(res){
    //empty div section to clear space for new search
    $incomeStatement.html('')

    // received data "res" in javascript notation from 'getData' function
    // dictionary (on browser at least) has seperate item for 'data' within response where data requested will be hence the 'res[data]'
    let data = res['data']

    let exclude = ['link', 'finalLink', 'acceptedDate', 'date']

    // appending heading to section, and then using for loop to unpack the dictionary received from backend and appending 
    // them via a string literate
    $incomeStatement.append(`<h3> Income Statement </h3>`)
    displayTickerData($incomeStatement,data,exclude)
}

function handleBalanceSheet(res){
    $balanceSheet.html('')

    let data = res['data']

    let exclude = ['link', 'finalLink', 'acceptedDate', 'date']

    $balanceSheet.append(`<h3> Balance Sheet </h3>`)
    displayTickerData($balanceSheet,data,exclude)
}

function handleCashFlowStatement(res){
    $cashFlowStatement.html('')

    let data = res['data']

    let exclude = ['link', 'finalLink', 'acceptedDate', 'date']

    $cashFlowStatement.append(`<h3> Cash Flow Statement </h3>`)
    displayTickerData($cashFlowStatement,data,exclude)
}

function handleHistoricalPriceData(res){
    $recent.html('')

    let data = res['data']['historical'][0]

    let exclude = ['label', 'vwap', 'changeOverTime', 'date']

    $recent.append(`<h5> Most Recent Close: ${res['data']['symbol']}`)
    $recent.append(`<h6> Date: ${data['date']} <br><br>`)
    displayTickerData($recent, data, exclude)
}