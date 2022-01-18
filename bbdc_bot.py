from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import os

server ="http://127.0.0.1:4444/wd/hub"

#service = Service(executable_path="/root/BBDC-Bot/geckodriver")
browser_options = webdriver.ChromeOptions()#service=service)
browser_options.accept_untrusted_certs = True
#browser_options.add_argument('--headless')
browser = webdriver.Remote(command_executor=server,options=browser_options)

#browser = webdriver.Chrome('/root/BBDC-Bot/chromedriver')
#service = Service(executable_path=ChromeDriverManager().install())
#browser = webdriver.Chrome(service=service,service_args=["--headless", "--no-sandbox", "--disable-dev-shm-usage"])
#browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Get environment variables
USER = os.getenv('BOOKING_USER')
PASSWORD = os.environ.get('BOOKING_PASSWORD')

try: 
 # Load Main Login Page
 browser.get('https://info.bbdc.sg/members-login/')
 print("Main Login Page")
 
 # Input Username, Password and Login
 idLogin = browser.find_element(By.ID, "txtNRIC")
 idLogin.send_keys(USER)
 idLogin = browser.find_element(By.ID, "txtPassword")
 idLogin.send_keys(PASSWORD)
 loginButton = browser.find_element(By.ID, "loginbtn")
 loginButton.click()
 print("Logging In")
 
 
 # Accept Insecure and Choose default enrolled course
 proceedBtn = browser.find_element(By.ID, 'proceed-button')
 proceedBtn.click()
 submitBtn = browser.find_element(By.NAME,'btnSubmit')
 submitBtn.click()
 print("Main Booking Page")
 
 
 # Switching to Left Frame and accessing element by text
 browser.switch_to.default_content()
 frame = browser.find_element(By.NAME, 'leftFrame')
 browser.switch_to.frame(frame)
 bookingBtn = browser.find_element(By.CSS_SELECTOR, "a[href*='../b-2-pLessonBooking.asp?limit=pl']");
 bookingBtn.click()
 print("Clicking Practical Booking")
 
 
 #ids = browser.find_elements_by_xpath('//*[@id]')
 #for ii in ids:
     #print(ii.get_attribute('id'))
 #quit()
 
 # Selection menu
 browser.switch_to.default_content()
 wait = WebDriverWait(browser, 300)
 wait.until(EC.frame_to_be_available_and_switch_to_it(browser.find_element(By.NAME, 'mainFrame')))
 wait.until(EC.visibility_of_element_located((By.ID, "checkMonth")))
 
 # 0 refers to first month, 1 refers to second month, and so on...
 months = browser.find_element(By.ID, 'checkMonth')
 months[12].click() # all months
 
 # 0 refers to first session, 1 refers to second session, and so on...
 sessions = browser.find_element(By.ID, 'checkSes')
 sessions[8].click() # all sessions
 
 # 0 refers to first day, 1 refers to second day, and so on...
 days = browser.find_element(By.ID, 'checkDay')
 days[7].click() # all days
 
 # Selecting Search
 browser.find_element(By.NAME, 'btnSearch').click()
 
 # Dismissing Prompt
 wait = WebDriverWait(browser, 300)
 wait.until(EC.alert_is_present())
 alert_obj = browser.switch_to.alert
 alert_obj.accept()
 wait.until(EC.visibility_of_element_located((By.NAME, "slot")))
 
 # 0 refers to first slot, 1 refers to second slot, and so on...
 slots = browser.find_element(By.NAME, 'slot')
 for slot in slots:     # Selecting all checkboxes
     #slot.click()
     timeslot = slot.find_element(By.XPATH, './..').get_attribute('onmouseover')
     print(timeslot[20:58])
     #browser.find_element_by_class_name('pgtitle').click()     # clicking random element to hide hover effect
 
 #print(slots)
 quit()
 
 #ids = browser.find_elements_by_xpath('//*[@id]')
 #for ii in ids:
     #print(ii.get_attribute('id'))
 #quit()
 
 # Selecting Submit
 #browser.find_element_by_name('btnSubmit').click()
 
 # Selecting confirm
 #wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@value='Confirm']")))
 #browser.find_element_by_xpath("//input[@value='Confirm']").click()

except Exception as e:
  print(e) 
  quit()
