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
import hashlib

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


def loginMainPage(browser):
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

def getAvailableBooking(browser):
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
  print("Main Frame Practical Booking Page Loaded...")
 
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
      timeslot = slot.find_element(By.XPATH, './..').get_attribute('onmouseover')
      timeinfo = timeslot[20:58].replace('"', '').split(",")
      timeinfoList.append(timeinfo)  
  return timeinfoList
  #print(timeinfoList) 

def getExistingBooking(browser):
  # Switching to Left Frame and accessing element by text
  browser.switch_to.default_content()
  frame = browser.find_element(By.NAME, 'leftFrame')
  browser.switch_to.frame(frame)
  bookingBtn = browser.find_element(By.CSS_SELECTOR, "a[href*='../b-bookTestStatement.asp']");
  bookingBtn.click()
  print("...Clicking Booking Statement")

  # Booking Statement Page
  browser.switch_to.default_content()
  wait = WebDriverWait(browser, 300)
  wait.until(EC.frame_to_be_available_and_switch_to_it(browser.find_element(By.NAME, 'mainFrame')))
  wait.until(EC.visibility_of_element_located((By.NAME, "btnHome")))
  print("Main Frame for Booking Statement Page Loaded...")

  try:
    bookedDate = browser.find_element(By.XPATH, '/html/body/table/tbody/tr/td[2]/form/table/tbody/tr[5]/td/table/tbody/tr[2]/td[1]').text
    bookedSession = browser.find_element(By.XPATH, '/html/body/table/tbody/tr/td[2]/form/table/tbody/tr[5]/td/table/tbody/tr[2]/td[2]').text
    bookedTime = browser.find_element(By.XPATH, '/html/body/table/tbody/tr/td[2]/form/table/tbody/tr[5]/td/table/tbody/tr[2]/td[3]').text
    existingBooking = bookedDate + "," + bookedSession + "," + bookedTime
    print("My Existing Booking: " + existingBooking) 
    return existingBooking
  except:
    return "None"

def end():
  # Restart container 
  print("...Restarting Container...")
  subprocess.run(["systemctl", "restart", "container-chrome.service"])
  quit()

try: 
  browser_options = webdriver.ChromeOptions()
  browser_options.accept_untrusted_certs = True
  browser = webdriver.Remote(command_executor=server,options=browser_options)

  loginMainPage(browser)
  existingBooking = getExistingBooking(browser)
  timeinfoList = getAvailableBooking(browser)

  # Dummy data for troubleshooting
  #timeinfoList = []
  #timeinfoList.append(['23/01/2022 (Wed)', '6', '17:10', '18:50'])
  #timeinfoList.append(['02/02/2022 (Wed)', '6', '17:10', '18:50'])
  #timeinfoList.append(['29/01/2022 (Wed)', '6', '17:10', '18:50'])
  #timeinfoList.append(['30/01/2022 (Wed)', '6', '17:10', '18:50'])
  #timeinfoList.append(['31/01/2022 (Wed)', '6', '17:10', '18:50'])
  #timeinfoList.append(['01/02/2022 (Wed)', '6', '17:10', '18:50'])  
  #timeinfoList.append(['02/02/2022 (Wed)', '6', '17:10', '18:50'])  
  #timeinfoList.append(['03/02/2022 (Wed)', '6', '17:10', '18:50'])  

  # Set the number of days with slots to return based on day the script runs
  now_date = datetime.today()
  eta_date_wkday = now_date + timedelta(6) # Return 6day of available slots if script run during weekday
  eta_date_wkend = now_date + timedelta(10) # Return 10day of available slots if script run during weekend
  if now_date.weekday() >= 0 and now_date.weekday() <= 4:
    eta_date = eta_date_wkday
  else:
    eta_date = eta_date_wkend
  print("Looking for bookings before: " + str(eta_date))

  # Loop through all bookings and to create list of results within number of days
  resultList = []
  for t in timeinfoList: 
    dtobj = datetime.strptime(t[0][0:10], "%d/%m/%Y")
    if dtobj <= eta_date:
        resultList.append(' '.join(t))
    else:
        break
  print("Results to send to notification: " + str(resultList))

  # Read file for hash from previous run
  # Hash the current returned data results
  # Comparing previous and current run hash to prevent spaming notification if no new slot available
  try: 
    f = open("cache", "r+")
    h1 = f.read()
  except:
    h1 = ""
  mptdata = '\n'.join(resultList)
  h2 = hashlib.sha1(mptdata.encode("UTF-8")).hexdigest()

  print("Hash, h1 is " + h1)
  print("Hash, h2 is " + h2)
  if len(resultList) > 0 and (h1 != h2):
    f = open("cache", "w+")
    f.write(h2)
    f.close()

    # Concate and send message to telegram
    mptdata = 'Script Run @ ' + str(datetime.today()) + '\nMy Booking @ ' + existingBooking + '\n\n' + mptdata
    broadcastMessage(telelink, mptdata)
  
#  # Use the following code block for troubleshooting and debugging
#  #ids = browser.find_elements_by_xpath('//*[@id]')
#  #for ii in ids:
#      #print(ii.get_attribute('id'))
#  #quit()
 
except Exception as e:
  print(e)

print("...Restarting Container...")
subprocess.run(["systemctl", "restart", "container-chrome.service"]) 
quit()
