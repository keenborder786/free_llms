import io
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from langchain_core.callbacks import BaseCallbackHandler, RunManager
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, model_validator
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from free_llms.callbacks import StdOutCallbackHandler
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
    retries_attempt: int = 3
    """How many login attempts do we need to make otherwise we raise error"""
    callbacks: List[BaseCallbackHandler] = []
    """Optional list of callback handlers (or callback manager). Defaults to None."""
    run_manager: RunManager
    """Run Manager that manages and callbacks various events from the given callbacks"""
    verbose: bool = True
    """Whether you want to print logs. Defaults to True"""

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @model_validator(mode="before")
    @classmethod
    def start_run_manger(cls, data: Dict) -> Dict:
        if "callbacks" not in data:
            data["callbacks"] = [StdOutCallbackHandler(color="green")]
        data["run_manager"] = RunManager(run_id=uuid.uuid1(), handlers=data["callbacks"], inheritable_handlers=[])
        return data

    @model_validator(mode="before")
    @classmethod
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
    def login(self, retries_attempt: int) -> bool:
        """
        Logs into LLM Provider Browser using the provided email and password.
        No Social Logins e.g Google etc

        Args:
        retries_attempt (str): The number of attempts to do a login request

        Returns:
        bool: True if login is successful, False otherwise.
        """
        pass

    @abstractmethod
    def send_prompt(self, query: str) -> AIMessage:
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
        if not self.login(self.retries_attempt):
            raise ValueError("Cannot Login given the credentials")
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

    def login(self, retries_attempt: int) -> bool:
        self.driver.get(self._model_url)
        for i in range(retries_attempt):
            self.run_manager.on_text(text=f"Making login attempt no. {i+1} on ChatGPT", verbose=self.verbose)
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
                self.run_manager.on_text(text=f"Login succeed on attempt no. {i+1}", verbose=self.verbose)
                return True
            except TimeoutException:
                continue
        return False

    def send_prompt(self, query: str) -> AIMessage:
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
                self.run_manager.on_text(text="Captacha Detected on ChatGPT. Starting Annoymous Session", verbose=self.verbose)
                self.driver.get(current_url)

        text_area.click()
        text_area.send_keys(query)
        self.run_manager.on_text(text=f"Human Message: {query} send to ChatGPT", verbose=self.verbose)
        text_area.submit()
        raw_message = ""
        time.sleep(self.waiting_time)  # Wait for the query to be processed
        current_n, prev_n = 0, -1
        message_jump = 3
        while current_n != prev_n:
            prev_n = current_n
            streaming = self.driver.find_element(By.XPATH, self._elements_identifier["Prompt_Text_Output"].format(current=message_jump))
            raw_message = streaming.get_attribute("innerHTML")
            self.run_manager.on_text(text="ChatGPT is responding", verbose=self.verbose)
            current_n = len(raw_message) if raw_message is not None else 0
        message_jump += 2
        self.run_manager.on_text(text=f"ChatGPT responded with {len(raw_message)} characters", verbose=self.verbose)
        self.messages.append((HumanMessage(content=query), AIMessage(content=raw_message)))
        return AIMessage(content=raw_message)


class PreplexityChrome(LLMChrome):
    """Note: Preplexity does not right no build on previous conversation. Every Message is a new request"""

    @property
    def _model_url(self) -> str:
        return "https://www.perplexity.ai/"

    @property
    def _elements_identifier(self) -> Dict[str, str]:
        return {
            "Prompt_Text_Area": "/html/body/div/main/div/div/div/div/div/div/div[1]/div[2]/div/div/span/div/div/textarea",
            "Prompt_Text_Area_Submit": "#__next > main > div > div > div.grow.lg\:pr-sm.lg\:pb-sm.lg\:pt-sm > div > div > div > div.relative.flex.h-full.flex-col > div.mt-lg.w-full.grow.items-center.md\:mt-0.md\:flex.border-borderMain\/50.ring-borderMain\/50.divide-borderMain\/50.dark\:divide-borderMainDark\/50.dark\:ring-borderMainDark\/50.dark\:border-borderMainDark\/50.bg-transparent > div > div > span > div > div > div.bg-background.dark\:bg-offsetDark.flex.items-center.space-x-2.justify-self-end.rounded-full.col-start-3.row-start-2.-mr-2 > button",  # noqa: E501
            "Prompt_Text_Output": "/html/body/div/main/div/div/div/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[3]/div/div[1]/div[2]/div/div[2]",  # noqa: E501
            "Prompt_Text_Output_Related": "/html/body/div/main/div/div/div/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[3]/div/div[1]/div[3]/div/div",  # noqa: E501
            "App_Download_Button": "/html/body/div[1]/main/div[3]/div/div/div/div[2]/div[1]/div/div/button",
        }

    def login(self, retries_attempt: int) -> bool:
        """With Perplexity we are going to stick to anonymous session"""
        return True

    def send_prompt(self, query: str) -> AIMessage:
        self.driver.get(self._model_url)
        text_area = WebDriverWait(self.driver, self.waiting_time).until(
            EC.element_to_be_clickable((By.XPATH, self._elements_identifier["Prompt_Text_Area"]))
        )

        text_area.click()
        text_area.send_keys(query)
        text_area_submit = WebDriverWait(self.driver, self.waiting_time).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, self._elements_identifier["Prompt_Text_Area_Submit"]))
        )
        text_area_submit.click()
        raw_message: Optional[str] = ""
        while True:
            try:
                WebDriverWait(self.driver, self.waiting_time).until(
                    EC.visibility_of_element_located((By.XPATH, self._elements_identifier["Prompt_Text_Output_Related"]))
                )
                text_area_output = WebDriverWait(self.driver, self.waiting_time).until(
                    EC.visibility_of_element_located((By.XPATH, self._elements_identifier["Prompt_Text_Output"]))
                )
                raw_message = text_area_output.get_attribute("innerHTML")
                break
            except TimeoutException:
                try:
                    app_download_button = self.driver.find_element(By.XPATH, self._elements_identifier["App_Download_Button"])
                    app_download_button.click()
                except NoSuchElementException:
                    continue
        processed_message = BeautifulSoup(io.StringIO(raw_message)).get_text()
        self.messages.append((HumanMessage(content=query), AIMessage(content=processed_message)))
        return AIMessage(content=processed_message)
