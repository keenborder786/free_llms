from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from langchain_core.messages import AIMessage, HumanMessage
import time

class LLMChrome(ABC):
    """
    Abstract base class for an LLM (Language Model) Chrome interface.

    This class defines the interface for creating a chrome-based interaction with a language model. 
    
    Properties:
    _model_url (str): The URL to the model's login page.
    _elements_identifier (Dict[str, str]): A dictionary containing identifiers for various elements on the page.
    session_history (List[Tuple[HumanMessage, AIMessage]]): All of the messages in the current session in form of Human and AI pair.

    Methods:
    configure_options(driver_config: List[str]) -> uc.ChromeOptions:
        Configures the browser options based on provided driver configuration.
        
    login(email: str, password: str, waiting_time: int = 10) -> bool:
        Logs into the language model interface using the provided email and password.
        
    send_prompt(query: str, waiting_time: int = 10) -> str:
        Sends a query prompt to the language model and returns the response as a string.
        
    __enter__():
        Enters the runtime context related to this object (for use in 'with' statements).
        
    __exit__(*args, **kwargs):
        Exits the runtime context related to this object.
    """
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


class GPTChrome(LLMChrome):
    """
    Concrete implementation of LLMBrowser for interacting with ChatGPT through a Chrome browser.

    This class uses the undetected_chromedriver and selenium to automate interactions with the ChatGPT web interface.

    Properties:
    _model_url (str): Returns the ChatGPT login URL.
    _elements_identifier (Dict[str, str]): Returns a dictionary of CSS selectors and XPaths for various elements on the ChatGPT page.
    session_history (List[Tuple[HumanMessage, AIMessage]]): All of the messages in the current session in form of Human and AI pair.

    Methods:
    configure_options(driver_config: List[str]) -> uc.ChromeOptions:
        Configures Chrome options based on the provided driver configuration.
        
    login() -> bool:
        Logs into ChatGPT using the provided email and password.
        
    send_prompt(query: str) -> str:
        Sends a query prompt to ChatGPT and returns the response as a string.
        
    __enter__():
        Enters the runtime context for the browser session (for use in 'with' statements). Automatically logs in.
        
    __exit__(*args, **kwargs):
        Exits the runtime context and closes the browser session.

    Usage:
    with GPTChrome(driver_config=["--disable-gpu"], email="your_email", password="your_password") as browser:
        response = browser.send_prompt("What is the capital of France?")
        print(response)
    """

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
            "Prompt_Text_Output": '//*[@id="__next"]/div[1]/div[2]/main/div[1]/div[1]/div/div/div/div/div[{current}]/div/div/div[2]/div/div[1]/div/div/div',
        }

    @property
    def session_history(self) -> List[Tuple[HumanMessage, AIMessage]]:
        return self.messages
    
    def __init__(self, driver_config: List[str], email: str = '', password: str = '', waiting_time: int = 10):
        """
        Initializes the GPTChrome browser instance.

        Args:
        driver_config (List[str]): List of Chrome driver configuration options.
        email (str): The email address for logging into ChatGPT.
        password (str): The password for logging into ChatGPT.
        waiting_time (int): The time to wait for elements to load and interact with them (default is 10 seconds).
        """
        userAgent = UserAgent(browsers='chrome').random
        options = self.configure_options(driver_config)
        options.add_argument(f"--user-agent={userAgent}")
        self.driver = uc.Chrome(options=options, headless=True)
        self.email: str = email
        self.password: str = password
        self.waiting_time: int = waiting_time
        self.messages: List[Tuple[HumanMessage, AIMessage]] = []
        self.message_jump = 3

    @classmethod
    def configure_options(self, driver_config: List[str]) -> uc.ChromeOptions:
        """
        Configures the Chrome options.

        Args:
        driver_config (List[str]): List of Chrome driver configuration options.

        Returns:
        uc.ChromeOptions: Configured Chrome options.
        """
        chrome_options = uc.ChromeOptions()
        for arg in driver_config:
            chrome_options.add_argument(arg)
        return chrome_options

    def login(self) -> bool:
        """
        Logs into ChatGPT using the provided email and password.

        Returns:
        bool: True if login is successful, False otherwise.
        """
        self.driver.get(self._model_url)
        try:
            login_button = WebDriverWait(self.driver, self.waiting_time).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._elements_identifier["Login"]))
            )
            login_button.click()
            email_input = WebDriverWait(self.driver, self.waiting_time).until(
                EC.presence_of_element_located((By.ID, self._elements_identifier["Email"]))
            )
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
        """
        Sends a query prompt to ChatGPT and returns the response as a string.

        Args:
        query (str): The query to send to ChatGPT.

        Returns:
        str: The response from ChatGPT.
        """
        text_area = WebDriverWait(self.driver, self.waiting_time).until(
            EC.presence_of_element_located((By.ID, self._elements_identifier["Prompt_Text_Area"]))
        )
        text_area.click()
        text_area.send_keys(query)
        text_area.submit()
        raw_message = ''
        streaming = ''
        time.sleep(self.waiting_time)  # Wait for the query to be processed
        current_n, prev_n = 0, -1
        while current_n != prev_n:
            prev_n = current_n
            streaming = self.driver.find_element(By.XPATH, self._elements_identifier['Prompt_Text_Output'].format(current=self.message_jump))
            raw_message = streaming.get_attribute('innerHTML')
            current_n = len(raw_message)
        self.message_jump += 2
        self.messages.append([HumanMessage(content=query), AIMessage(content=raw_message)])
        return raw_message
    
    def __enter__(self):
        """
        Enters the runtime context related to this object (for use in 'with' statements).
        Automatically logs in upon entering the context.
        
        Returns:
        GPTChrome: The browser instance.
        """
        self.login()
        return self

    def __exit__(self, *args, **kwargs):
        """
        Exits the runtime context and closes the browser session.
        """
        self.driver.quit()
