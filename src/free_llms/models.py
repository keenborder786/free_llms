import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

import undetected_chromedriver as uc
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, model_validator
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from free_llms.constants import DRIVERS_DEFAULT_CONFIG
from free_llms.utils import configure_options


class LLMChrome(BaseModel, ABC):
    """
    Abstract Class for establishing a single session with an LLM through a Chrome browser.

    This class defines the interface for creating a Chrome-based interaction with a language model for a single session.

    Methods:
    login(email: str, password: str, waiting_time: int = 10) -> bool:
        Logs into the language model interface using the provided email and password.

    send_prompt(query: str, waiting_time: int = 10) -> str:
        Sends a query prompt to the language model and returns the response as a string.

    __enter__():
        Enters the runtime context related to this object (for use in 'with' statements).

    __exit__(*args, **kwargs):
        Exits the runtime context related to this object.
    """

    email: str
    """LLM Provider Account Email"""
    password: str
    """LLM Proiver Account Password"""
    waiting_time: int = 10
    """How much time do you need to wait for elements to appear. Client cannot change this. This depends on LLM providers"""
    driver: uc.Chrome
    """UnDetected Chrome Driver. This is started automatically and client do not need to provide."""
    driver_config: List[str]
    """Configuration for UnDetected Chrome Driver."""
    messages: List[Tuple[HumanMessage, AIMessage]] = []
    """Messages in the current session"""

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @model_validator(mode="before")
    def check_start_driver(cls, data: Dict) -> Dict:
        """
        Validates and starts the Chrome driver with appropriate configurations.
        Ensures certain configurations are not modified or reused.
        """
        if "driver" in data:
            raise ValueError("You cannot pass in an already started driver")
        if "message_jump" in data:
            raise ValueError("You cannot set message jump")
        for default_config in DRIVERS_DEFAULT_CONFIG:
            if default_config in data["driver_config"]:
                raise ValueError(f"You cannot put in {default_config} in your provided driver config")
        for started_config in data["driver_config"]:
            if "--window-size" in started_config:
                raise ValueError("You cannot change the window size in your provided driver config")
        options = configure_options(data["driver_config"] + DRIVERS_DEFAULT_CONFIG)
        data["driver"] = uc.Chrome(options=options, headless=True)
        return data

    @property
    @abstractmethod
    def _model_url(self) -> str:
        """The URL to the LLM provider's login page."""
        pass

    @property
    @abstractmethod
    def _elements_identifier(self) -> Dict[str, str]:
        """A dictionary containing identifiers for various elements on the page"""
        pass

    @property
    def session_history(self) -> List[Tuple[HumanMessage, AIMessage]]:
        """All of the messages in the current session in the form of Human and AI pairs."""
        return self.messages

    @abstractmethod
    def login(self, retries_attempt: int = 3) -> bool:
        """
        Logs into LLM Provider Browser using the provided email and password.
        No SSO (Single Sign On)

        Args:
        retries_attempt (str): The number of attempts to do a login request

        Returns:
        bool: True if login is successful, False otherwise.
        """
        pass

    @abstractmethod
    def send_prompt(self, query: str) -> str:
        """
        Sends a query prompt to LLM Provider and returns the response as a string.

        Args:
        query (str): The query to send to LLM Provider.

        Returns:
        str: The response from LLM Provider.
        """
        pass

    def __enter__(self) -> "LLMChrome":
        """
        Enters the runtime context related to this object (for use in 'with' statements).
        Automatically logs in upon entering the context.
        """
        self.login()
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        """
        Exits the runtime context and closes the browser session.
        """
        self.driver.quit()


class GPTChrome(LLMChrome):
    """
    Concrete implementation of LLMChrome for establishing a single session with ChatGPT through a Chrome browser.

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
            "Login": '//*[@id="__next"]/div[1]/div[2]/div[1]/div/div/button[1]',  # noqa: E501
            "Email": "username",
            "Email_Continue": "action",
            "Password": '//*[@id="password"]',
            "Prompt_Text_Area": "prompt-textarea",
            "Prompt_Text_Output": '//*[@id="__next"]/div[1]/div[2]/main/div[2]/div[1]/div/div/div/div/div[{current}]/div/div/div[2]/div[2]/div[1]/div/div',  # noqa: E501
        }

    def login(self, retries_attempt: int = 3) -> bool:
        self.driver.get(self._model_url)
        for _ in range(retries_attempt):
            try:
                login_button = WebDriverWait(self.driver, self.waiting_time).until(
                    EC.element_to_be_clickable((By.XPATH, self._elements_identifier["Login"]))
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
                return True
            except TimeoutException:
                continue
        return False

    def send_prompt(self, query: str) -> str:
        while True:
            try:
                text_area = WebDriverWait(self.driver, self.waiting_time).until(
                    EC.presence_of_element_located((By.ID, self._elements_identifier["Prompt_Text_Area"]))
                )
                break
            except TimeoutException:
                current_url = self.driver.current_url
                self.driver.quit()
                self.driver = uc.Chrome(options=configure_options(self.driver_config + DRIVERS_DEFAULT_CONFIG), headless=True)
                self.driver.get(current_url)

        text_area.click()
        text_area.send_keys(query)
        text_area.submit()
        raw_message = ""
        time.sleep(self.waiting_time)  # Wait for the query to be processed
        current_n, prev_n = 0, -1
        message_jump = 3
        while current_n != prev_n:
            prev_n = current_n
            streaming = self.driver.find_element(By.XPATH, self._elements_identifier["Prompt_Text_Output"].format(current=message_jump))
            raw_message = streaming.get_attribute("innerHTML")
            current_n = len(raw_message) if raw_message is not None else 0
        message_jump += 2
        self.messages.append((HumanMessage(content=query), AIMessage(content=raw_message)))
        return raw_message
