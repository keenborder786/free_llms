from abc import ABC, abstractmethod
from typing import Dict, List,Tuple

import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from langchain_core.messages import AIMessage,HumanMessage
from langchain.output_parsers import MarkdownListOutputParser
import time

class LLMBrowser(ABC):
    @property
    @abstractmethod
    def _browser_name(self) -> str:
        pass

    @property
    @abstractmethod
    def _model_url(self) -> str:
        pass

    @property
    @abstractmethod
    def _elements_identifier(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def configure_options(self, driver_config: List[str]) -> uc.ChromeOptions:
        pass

    @abstractmethod
    def login(self, email: str, password: str, waiting_time: int = 10) -> bool:
        pass

    @abstractmethod
    def send_prompt(self, query: str, waiting_time: int = 10) -> str:
        pass
    
    @abstractmethod
    def __enter__(self):
        pass
    
    @abstractmethod
    def __exit__(self):
        pass


class GPTChrome(LLMBrowser):
    @property
    def _browser_name(self) -> str:
        return "chrome"

    @property
    def _model_url(self) -> str:
        return "https://chatgpt.com/auth/login?sso="
    
    @property
    def _elements_identifier(self) -> Dict[str, str]:
        return {
            "Login": "#__next > div.flex.min-h-full.w-screen.flex-col.sm\:supports-\[min-height\:100dvh\]\:min-h-\[100dvh\].md\:grid.md\:grid-cols-2.lg\:grid-cols-\[60\%_40\%\] > div.relative.flex.grow.flex-col.items-center.justify-between.bg-white.px-5.py-8.text-black.dark\:bg-black.dark\:text-white.sm\:rounded-t-\[30px\].md\:rounded-none.md\:px-6 > div.relative.flex.w-full.grow.flex-col.items-center.justify-center > div > div > button:nth-child(1)", # noqa: E501
            "Email": "username",
            "Email_Continue": "action",
            "Password": '//*[@id="password"]',
            "Prompt_Text_Area": "prompt-textarea",
            "Prompt_Text_Output":'//*[@id="__next"]/div[1]/div[2]/main/div[1]/div[1]/div/div/div/div/div[{current}]/div/div/div[2]/div/div[1]/div/div/div',
        }

    def __init__(self, driver_config: List[str], email:str = '', password:str = '', waiting_time:int = 10):
        userAgent = UserAgent(browsers=self._browser_name).random
        options = self.configure_options(driver_config)
        options.add_argument(f"--user-agent={userAgent}")
        self.driver = uc.Chrome(options=options, headless=True)
        self.email:str = email
        self.password:str = password
        self.waiting_time:int = waiting_time
        self.messages:List[Tuple[HumanMessage,AIMessage]] = []
        self.message_jump = 3

    @classmethod
    def configure_options(self, driver_config: List[str]) -> uc.ChromeOptions:
        chrome_options = uc.ChromeOptions()
        for arg in driver_config:
            chrome_options.add_argument(arg)

        return chrome_options

    def login(self) -> bool:
        self.driver.get(self._model_url)
        try:
            login_button = WebDriverWait(self.driver, self.waiting_time).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._elements_identifier["Login"]))
            )
            login_button.click()
            email_input = WebDriverWait(self.driver, self.waiting_time).until(EC.presence_of_element_located((By.ID, self._elements_identifier["Email"])))
            email_input.click()
            email_input.send_keys(self.email)
            continue_button = WebDriverWait(self.driver, self.waiting_time).until(
                EC.presence_of_element_located((By.NAME, self._elements_identifier["Email_Continue"]))
            )
            continue_button.click()
            password_button = WebDriverWait(self.driver, self.waiting_time).until(
                EC.element_to_be_clickable((By.XPATH, self._elements_identifier["Password"]))
            )
            password_button.clear()
            password_button.click()
            password_button.send_keys(self.password)
            password_button.submit()
        except TimeoutException:
            self.login()
        return True

    def send_prompt(self, query: str) -> str:
        text_area = WebDriverWait(self.driver, self.waiting_time).until(
            EC.presence_of_element_located((By.ID, self._elements_identifier["Prompt_Text_Area"]))
        )
        text_area.click()
        text_area.send_keys(query)
        text_area.submit()
        raw_message = ''
        streaming = ''
        time.sleep(self.waiting_time) # do a wait for the query to happen
        current_n,prev_n = 0,-1
        while current_n != prev_n:
            prev_n = current_n
            streaming = self.driver.find_element(By.XPATH,self._elements_identifier['Prompt_Text_Output'].format(current=self.message_jump))
            raw_message = streaming.get_attribute('innerHTML')
            current_n = len(raw_message)
        self.message_jump += 2
        self.messages.append([HumanMessage(content = query),AIMessage(content=raw_message)])
        return raw_message
    
    def __enter__(self):
        self.login()
        return self

    def __exit__(self,*args, **kwargs):
        self.driver.quit()