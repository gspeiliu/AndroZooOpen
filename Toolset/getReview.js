/* 
Install: npm install google-play-scrape
Source code: //https://github.com/facundoolano/google-play-scraper 
Date modified: 2019-10-09
Description: Use the Google Play Scraper tools, to scrap google play store to get reviews for certain app
*/

const gplay = require('google-play-scraper');
const util = require('util')
var pname = process.argv[2]  // the argument name provided in the run command, eg"com.vanilla.umbrella"

//Retrieve the 1000 reviews, sort by helpfulness 
// gplay.reviews({
//   appId: pname,
//   sort: gplay.sort.HELPFULNESS,
//   num: 1000
// }).then(function(value) {
//   console.log(util.inspect(value, { maxArrayLength: null }))}, console.log);




// ----------------------------------------------------------------------------------------------------------------------------------
// Can be continue to work on to return json object
// But need to figure out how to get json stringify to implement in python 10000000

gplay.reviews({
    appId: pname,
    sort: gplay.sort.HELPFULNESS,
    num: 10000000
  }).then(function(value) {
    console.log(JSON.stringify(value, null, 1));}, console.log);
// ----------------------------------------------------------------------------------------------------------
