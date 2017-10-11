
var driver = openBrowser();

beginTransaction(function() {
  
  beginStep(function() {
    driver.get("https://www.neustar.biz");
    assertTrue(driver.findElement(By.tagName("body")).getText().contains("Neustar"));
  });

  
  beginStep(function() {
    driver.findElement(By.linkText("Marketing")).click();
    waitFor(function() {
        driver.executeScript("return document.readyState;").equals("complete");
    }, 30000);
    assertTrue(driver.findElement(By.tagName("body")).getText().contains("Marketing in the Connected World"));
  });

});
