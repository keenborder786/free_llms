import sys

sys.path.insert(0,'/Users/mac/free_llms/src')

from free_llms.models import GPTChrome



driver_config = ["--disable-gpu", "--window-size=1920,1080"]
driver = GPTChrome(driver_config)
driver.login('mohammad.mohtashim78@gmail.com','536A536a')