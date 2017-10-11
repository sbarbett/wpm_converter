/*
  Test stream comment
*/
var driver = openBrowser();
selenium = driver.getSelenium();

beginTransaction(function() {
  
  beginStep(function() {
    // Test inline comment
    selenium.open('https://www.neustar.biz');
    selenium.verifyTextPresent('Neustar');
  });

  /*
    Test stream 2
  */
  beginStep(function() {
    // Test inline 2
    selenium.click('link=Marketing');
    selenium.waitForPageToLoad(30000);
    selenium.verifyTextPresent('Marketing in the Connected World');
  });

});