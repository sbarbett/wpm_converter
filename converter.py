import re

class OpenScript:
  def __init__(self, script_name):
    self.original_script = self._remove_comments(open(script_name, 'r').read())
    self.wd_object_name = self._get_object_name(self.original_script)
    # Raise exception if there's no openBrowser method in the script
    if self.wd_object_name == None:
      raise Exception('File is not a real browser script.')
    self.se_object_name = self._get_object_name(self.original_script, 'se')
    # Raise exception if there's no getSelenium method in the script
    if self.se_object_name == None:
      raise Exception('File is not a Selenium script.')
    self.global_timeout = 30000
    self.converted_script = ''

  # Remove all the stream and inline comments, we don't want to process 
  # those
  def _remove_comments(self, script):
    no_stream = re.sub(r"/\*([\s\S]*?)\*/", '', script)
    lines = no_stream.splitlines()
    result = ''
    for line in lines:
      if re.match(r"^\s*//", line):
        continue
      result = result + line + '\n'
    return result

  # Get the name of the defined Selenium or Webdriver objects
  def _get_object_name(self, script, type='wd'):
    lines = script.splitlines()
    for line in lines:
      object_line = line.strip()
      if 'getSelenium()' in line and type == 'se':
        if re.match(r"^var", object_line):
          return object_line[3:].split('=')[0].strip()
        return object_line.split('=')[0].strip()
      if 'openBrowser(' in line and type == 'wd':
        if re.match(r"^var", object_line):
          return object_line[3:].split('=')[0].strip()
        return object_line.split('=')[0].strip()
    return None

  def _get_method(self, line):
    # Split at the first period
    two_part = line.split('.', 1)
    # Store whitespace or nothing if none found at beginning of line
    white_space = ''
    white_space_match = re.findall(r"^\s*", two_part[0])
    if white_space_match:
      white_space = white_space_match[0]
    # Store method name, match all letters up until open parenthese
    method_match = re.findall(r"^[a-zA-Z]*", two_part[1])
    if not method_match:
      raise Exception('Error parsing method name.')
    method = method_match[0]
    # Trim method off the params
    param_string = two_part[1][len(method):]
    return {'white_space': white_space, 'method': method, 'param_string': param_string}

  # Map of how many parameters each method had
  def _get_method_params(self, method):
    all_methods = {
      'getSelenium': 0,
      'open': 1,
      'verifyTextPresent': 1,
      'click': 1,
      'waitForPageToLoad': 1
    }
    if method not in all_methods:
      raise Exception('Method not available.')
    return all_methods[method]

  # Parse out the arguments passed to a method. Only supports 2 args right now
  def _parse_params(self, param_string, param_length):
    # Use regex to match arguments
    if param_length == 0:
      params = None
    elif param_length == 1:
      if '"' not in param_string and '\'' not in param_string:
        params = re.findall(r"^\((\d*)\)", param_string)
      else:
        params = re.findall(r"^\(\s*['\"]\s*(?P<first_param>.*?)\s*['\"]\)", param_string)
      if not params:
        raise Exception('Error parsing params.')
    elif param_length == 2:
      param_tuple = re.findall(r"^\(\s*['\"]\s*(?P<first_param>.*?)(\"\s*,\s*\"|'\s*,\s*')(?P<second_param>.*?)\s*['\"]\)", param_string)
      if not param_tuple[0][0] or param_tuple[0][2]:
        raise Exception('Error parsing params.')
      params = [param_tuple[0][0], param_tuple[0][2]]
    else:
      raise Exception('Param length must be 1 or 2.')
    return params

  # When dealing with Selenium locators, separate type from value and return a
  # By object
  def _locator_parser(self, locator):
    by = None;
    if locator.startswith('//'):
      by = 'By.xpath("' + locator + '")'
    elif '=' in locator:
      loc_type = locator.split('=', 1)[0]
      loc_value = locator.split('=', 1)[1]
      if loc_type.lower() == 'name':
        by = 'By.name("' + loc_value + '")'
      elif loc_type.lower() == 'css':
        by = 'By.cssSelector("' + loc_value + '")'
      elif loc_type.lower() == 'id':
        by = 'By.id("' + loc_value + '")'
      elif loc_type.lower() == 'identifier':
        by = 'By.id("' + loc_value + '")'
      elif loc_type.lower() == 'link':
        by = 'By.linkText("' + loc_value + '")'
      elif loc_type.lower() == 'xpath':
        by = 'By.xpath("' + loc_value + '")'
      else:
        by = 'By.id("' + loc_value + '")'
    else:
      by = 'By.id("' + locator + '")'
    return by

  # Take an object containing white space, method type and parameters and attempt
  # to convert it to WebDriver
  def _driver_convert(self, wd_object):
    print wd_object
    if 'getSelenium' in wd_object['method']:
      return ''
    if wd_object['method'] == 'open':
      return wd_object['white_space'] + self.wd_object_name + '.get("' + wd_object['params'][0] + '");\n'
    if wd_object['method'] == 'verifyTextPresent':
      return wd_object['white_space'] + 'assertTrue(' + self.wd_object_name + '.findElement(By.tagName("body")).getText().contains("' + wd_object['params'][0] + '"));\n'
    if wd_object['method'] == 'click':
      locator = self._locator_parser(wd_object['params'][0])
      return wd_object['white_space'] + self.wd_object_name + '.findElement(' + locator + ').click();\n'
    if wd_object['method'] == 'waitForPageToLoad':
      return_value = wd_object['white_space'] + 'waitFor(function() {\n'
      return_value = return_value + wd_object['white_space'] + '    ' + self.wd_object_name + '.executeScript("return document.readyState;").equals("complete");\n'
      return_value = return_value + wd_object['white_space'] + '}, ' + wd_object['params'][0] + ');\n'
      return return_value
    return None

  # Perform conversion on original script passed to OpenScript
  def convert(self):
    lines = self.original_script.splitlines()
    for line in lines:
      if line.strip().startswith(self.se_object_name):
        parts = self._get_method(line)
        params = self._parse_params(parts['param_string'], self._get_method_params(parts['method']))
        wd_object = {'white_space': parts['white_space'], 'method': parts['method'], 'params': params}
        converted_line = self._driver_convert(wd_object)
        if converted_line != None:
          self.converted_script = self.converted_script + converted_line
        else:
          raise Exception('Failed to convert line "' + line + '"')
      else:
        self.converted_script = self.converted_script + line + '\n'

  # Save the converted script property
  def save(self, file_path):
    if self.converted_script:
      output_file = open(file_path, 'w')
      output_file.write(self.converted_script)
      output_file.close()

