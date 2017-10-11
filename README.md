wpm_converter
===============

Attempting to convert scripts using WPM's old Selenium RC Interface to methods only in WebDriver and other native classes.

Usage
===============

This is done in the directory containing converter.py, keep that in mind when considering file-path relativity.

1. Open Python 2.7

```
sbarbett$ python
Python 2.7.13 (default, Dec 18 2016, 07:03:34) 
[GCC 4.2.1 Compatible Apple LLVM 7.0.2 (clang-700.1.81)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
```

2. Import converter.py and load a script

```
>>> import converter
>>> se_script = converter.OpenScript('testscript_se.js')
>>> print se_script.original_script

var driver = openBrowser();
selenium = driver.getSelenium();

beginTransaction(function() {
  
  beginStep(function() {
    selenium.open('https://www.neustar.biz');
    selenium.verifyTextPresent('Neustar');
  });

  
  beginStep(function() {
    selenium.click('link=Marketing');
    selenium.waitForPageToLoad(30000);
    selenium.verifyTextPresent('Marketing in the Connected World');
  });

});

```

3. Run the convert method

```
>>> se_script.convert()
{'white_space': '', 'params': None, 'method': 'getSelenium'}
{'white_space': '    ', 'params': ['https://www.neustar.biz'], 'method': 'open'}
{'white_space': '    ', 'params': ['Neustar'], 'method': 'verifyTextPresent'}
{'white_space': '    ', 'params': ['link=Marketing'], 'method': 'click'}
{'white_space': '    ', 'params': ['30000'], 'method': 'waitForPageToLoad'}
{'white_space': '    ', 'params': ['Marketing in the Connected World'], 'method': 'verifyTextPresent'}
>>> print se_script.converted_script

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
```

4. Save converted script to a file

```
>>> se_script.save('converted_script.js')
>>> exit()
sbarbett$ cat converted_script.js

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
```