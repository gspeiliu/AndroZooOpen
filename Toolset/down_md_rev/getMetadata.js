/* 
Install: npm install google-play-scrape
Source code: //https://github.com/facundoolano/google-play-scraper 
Date modified: 2019-10-09
Description: Use the Google Play Scraper tools, to scrap google play store to get metadata for certain app
*/

const gplay = require('google-play-scraper');
var pname = process.argv[2]  // the argument name provided in the run command, eg"com.vanilla.umbrella"



// gplay.app({appId: pname})
//   .then(console.log, console.log);





// ----------------------------------------------------------------------------------------------------------------------------------
// Can be continue to work on to return json object
// But need to figure out how to get json stringify to implement in python


gplay.app({appId: pname})
  .then(function(value) {
    console.log(JSON.stringify(value, null, 1));}, console.log);
// ----------------------------------------------------------------------------------------------------------


