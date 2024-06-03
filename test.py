import sys

sys.path.insert(0,'/Users/mac/free_llms/src')

from free_llms.models import GPTChrome


if __name__ == '__main__':
    driver_config = ["--disable-gpu", "--window-size=1920,1080"]
    model = GPTChrome(driver_config)
    model.login('21110290@lums.edu.pk','')