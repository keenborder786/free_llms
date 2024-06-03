import time
from abc import ABC, abstractmethod
from typing import List

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from fake_useragent import UserAgent


class LLMBrowser(ABC):
   
    @property
    @abstractmethod
    def _browser_name(self):
        pass
    
    @property
    @abstractmethod
    def _model_url(self):
        pass

    @property
    @abstractmethod
    def _elements_identifier(self):
        pass

    @abstractmethod
    def configure_options(self, driver_config: List[str]) -> Options:
        pass

    @abstractmethod
    def send_prompt(self, query: str, model_name: str) -> str:
        pass


class GPTChrome(LLMBrowser):

    @property
    def _browser_name(self):
        return 'chrome'
    
    @property
    def _model_url(self):
        return 'https://platform.openai.com/login?launch'
    
    @property
    def _elements_identifier(self):
        return {"Prompt_Text_Area": "prompt-textarea","Email":"email-input",
            "Email_Continue":"continue-btn",
            "Password":'//*[@id="password"]'}

    
    def __init__(self, driver_config: List[str]):
        chromedriver_autoinstaller.install()
        userAgent = UserAgent(browsers=self._browser_name).random
        options = self.configure_options(driver_config)
        options.add_argument(f'user-agent={userAgent}')
        self.driver = webdriver.Chrome(options=options)

    @classmethod
    def configure_options(self, driver_config: List[str]) -> Options:
        chrome_options = Options()
        for arg in driver_config:
            chrome_options.add_argument(arg)
            
        return chrome_options
    
    def login(self, email:str, password:str, waiting_time: int = 10) -> bool:
        
        self.driver.get(self._model_url)
        email_input = WebDriverWait(self.driver, waiting_time).until(
            EC.presence_of_element_located((By.ID, self._elements_identifier["Email"]))
        )
        email_input.click()
        email_input.send_keys(email)
        continue_button = WebDriverWait(self.driver, waiting_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, self._elements_identifier["Email_Continue"]))
        )
        continue_button.click()
        password_button = WebDriverWait(self.driver, waiting_time).until(
            EC.element_to_be_clickable((By.XPATH, self._elements_identifier["Password"]))
        )
        password_button.clear()
        password_button.click()
        password_button.send_keys(password)
        password_button.submit()
        time.sleep(1000)
        return True
    
    def send_prompt(self, query: str, waiting_time: int = 10) -> str:
        
        text_area = WebDriverWait(self.driver, waiting_time).until(
            EC.presence_of_element_located((By.ID, self._elements_identifier["Prompt_Text_Area"]))
        )
        text_area.click()
        text_area.send_keys(query)
        text_area.submit()
        time.sleep(1000)
        return ''
