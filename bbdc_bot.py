from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import os
import subprocess
from datetime import datetime, timedelta
import urllib.request
import ssl
import json

server ="http://127.0.0.1:4444/wd/hub"

# Import env values for telegram
USER = os.getenv('BOOKING_USER')
PASSWORD = os.getenv('BOOKING_PASSWORD')

# Import env values for telegram
chatid = os.getenv('chatid') #replace if hardcode needed
teleid = os.getenv('teleid') #replace if hardcode needed
telelink = "https://api.telegram.org/" + teleid + "/{}?{}"

def broadcastMessage(elink,einfo):
   headers = {"Accept": "application/json"}                                                                                 
   myssl = ssl._create_unverified_context()     
   params = {"text": einfo}
   params.update({"chat_id": chatid})
   url = elink.format("sendMessage", urllib.parse.urlencode(params))
   request = urllib.request.Request(url, None, headers)
   with urllib.request.urlopen(request, context=myssl) as r:
     r.read()

try: 
  browser_options = webdriver.ChromeOptions()
  browser_options.accept_untrusted_certs = True
  browser = webdriver.Remote(command_executor=server,options=browser_options)

  # Load Main Login Page
  browser.get('https://info.bbdc.sg/members-login/')
  print("Main Login Page Loaded...")
  
  # Input Username, Password and Login
  idLogin = browser.find_element(By.ID, "txtNRIC")
  idLogin.send_keys(USER)
  idLogin = browser.find_element(By.ID, "txtPassword")
  idLogin.send_keys(PASSWORD)
  loginButton = browser.find_element(By.ID, "loginbtn")
  loginButton.click()
  print("...Clicking Log In")
   
  # Accept Insecure and Choose default enrolled course
  proceedBtn = browser.find_element(By.ID, 'proceed-button')
  proceedBtn.click()
  submitBtn = browser.find_element(By.NAME,'btnSubmit')
  submitBtn.click()
  print("Main Booking Page Loaded...")
    
  # Switching to Left Frame and accessing element by text
  browser.switch_to.default_content()
  frame = browser.find_element(By.NAME, 'leftFrame')
  browser.switch_to.frame(frame)
  bookingBtn = browser.find_element(By.CSS_SELECTOR, "a[href*='../b-2-pLessonBooking.asp?limit=pl']");
  bookingBtn.click()
  print("...Clicking Practical Booking")
  
  # Selection menu
  browser.switch_to.default_content()
  wait = WebDriverWait(browser, 300)
  wait.until(EC.frame_to_be_available_and_switch_to_it(browser.find_element(By.NAME, 'mainFrame')))
  wait.until(EC.visibility_of_element_located((By.ID, "checkMonth")))
  print("Main Frame Page Loaded...")
 
  # 0 refers to first month, 1 refers to second month, and so on...
  months = browser.find_elements(By.ID, 'checkMonth')
  months[12].click() # all months
  # 0 refers to first session, 1 refers to second session, and so on...
  sessions = browser.find_elements(By.ID, 'checkSes')
  sessions[8].click() # all sessions
  # 0 refers to first day, 1 refers to second day, and so on...
  days = browser.find_elements(By.ID, 'checkDay')
  days[7].click() # all days
  # Selecting Search
  browser.find_element(By.NAME, 'btnSearch').click()
  print("...Clicking Search after checking all boxes")
 
  # Dismissing Prompt
  wait = WebDriverWait(browser, 300)
  wait.until(EC.alert_is_present())
  alert_obj = browser.switch_to.alert
  alert_obj.accept()
  wait.until(EC.visibility_of_element_located((By.NAME, "slot")))
  print("===Dismissed Prompt===")

  # 0 refers to first slot, 1 refers to second slot, and so on...
  slots = browser.find_elements(By.NAME, 'slot')
  timeinfoList = []
  for slot in slots:     # Selecting all checkboxes
      #slot.click()
      timeslot = slot.find_element(By.XPATH, './..').get_attribute('onmouseover')
      timeinfo = timeslot[20:58].replace('"', '').split(",")
      timeinfoList.append(timeinfo)
  
  #print(timeinfoList) 
  #timeinfoList.append(['11/01/2022 (Wed)', '6', '17:10', '18:50'])
  #timeinfoList.append(['12/01/2022 (Wed)', '6', '17:10', '18:50'])
  #timeinfoList.append(['30/01/2022 (Wed)', '6', '17:10', '18:50'])
  #timeinfoList.append(['29/01/2022 (Wed)', '6', '17:10', '18:50'])  
  
  start_date = datetime.today()
  end_date = start_date + timedelta(6)

  printList = []
  for t in timeinfoList: 
    dtobj = datetime.strptime(t[0][0:10], "%d/%m/%Y")
    if dtobj <= end_date:
      printList.append(' '.join(t))
 
  print(printList)

  # Craft message and send to telegram
  if len(printList) > 0:
    mptdata = '\n'.join(printList)
    mptdata = 'Run @ ' + str(start_date) + '\n\n' + mptdata
    broadcastMessage(telelink, mptdata)

  subprocess.run(["podman", "restart", "chrome"]) 
  quit()
  
  #ids = browser.find_elements_by_xpath('//*[@id]')
  #for ii in ids:
      #print(ii.get_attribute('id'))
  #quit()
 
except Exception as e:
  print(e) 
  subprocess.run(["podman", "restart", "chrome"])
  quit()
