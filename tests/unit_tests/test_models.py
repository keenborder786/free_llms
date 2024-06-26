import pytest
from free_llms.langchain_model import FreeLLMs
from free_llms.models import AIMessage, ClaudeChrome, GPTChrome, MistralChrome, PreplexityChrome


def test_gpt_chrome():
    assert GPTChrome(driver_config=[], email="", password="")._elements_identifier == {
            "Prompt_Text_Area": "prompt-textarea",
            "Prompt_Text_Output": '/html/body/div[1]/div[1]/div[2]/main/div[2]/div[1]/div/div/div/div/div[{current}]/div/div/div[2]/div[2]/div[1]/div/div',  # noqa: E501
        }
    assert GPTChrome(driver_config=[], email="", password="")._model_url == "https://chatgpt.com/"
    chrome_instance = GPTChrome(driver_config=[], email="", password="", retries_attempt=1)
    chrome_instance.driver.get("https://chatgpt.com/")
    ans = chrome_instance.send_prompt("How are you doing?")
    assert isinstance(ans, AIMessage)


def test_preplexity_chrome():
    assert PreplexityChrome(driver_config=[], email="email", password="password")._elements_identifier == {
        "Prompt_Text_Area": "/html/body/div/main/div/div/div/div/div/div/div[1]/div[2]/div/div/span/div/div/textarea",
        "Prompt_Text_Area_Submit": "#__next > main > div > div > div.grow.lg\:pr-sm.lg\:pb-sm.lg\:pt-sm > div > div > div > div.relative.flex.h-full.flex-col > div.mt-lg.w-full.grow.items-center.md\:mt-0.md\:flex.border-borderMain\/50.ring-borderMain\/50.divide-borderMain\/50.dark\:divide-borderMainDark\/50.dark\:ring-borderMainDark\/50.dark\:border-borderMainDark\/50.bg-transparent > div > div > span > div > div > div.bg-background.dark\:bg-offsetDark.flex.items-center.space-x-2.justify-self-end.rounded-full.col-start-3.row-start-2.-mr-2 > button",  # noqa: E501
        "Prompt_Text_Area_Output": "/html/body/div/main/div/div/div/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[3]/div/div[1]/div[2]/div/div[2]",  # noqa: E501
        "Prompt_Text_Area_Output_Related": "/html/body/div/main/div/div/div/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[3]/div/div[1]/div[3]/div/div",  # noqa: E501
        "App_Download_Button": "/html/body/div[1]/main/div[3]/div/div/div/div[2]/div[1]/div/div/button",
    }
    assert PreplexityChrome(driver_config=[], email="email", password="password")._model_url == "https://www.perplexity.ai/"
    with PreplexityChrome(
        driver_config=[],
        email="",
        password="",
    ) as session:
        ans = session.send_prompt("How are you doing?")
        assert isinstance(ans, AIMessage)


def test_mistral_chrome():
    with pytest.raises(ValueError, match="Cannot Login given the credentials"):
        with MistralChrome(
            driver_config=[], email="wrong_email", password="wrong_password", retries_attempt=1
        ) as session:  # A single session started with ChartGPT
            pass
    assert MistralChrome(driver_config=[], email="wrong_email", password="wrong_password")._elements_identifier == {
        "Email": ":Rclkn:",
        "Password": ":Rklkn:",
        "Login_Button": "/html/body/main/div/div[1]/div/div/div[2]/div/form[2]/div[3]/div[2]/div/button",
        "Prompt_Text_Area": "/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div[1]/div/textarea",
        "Prompt_Text_Area_Submit": "/html/body/div[1]/div[2]/div[2]/div/div[2]/div/div[1]/div/button",
        "Prompt_Text_Area_Output": "/html/body/div[1]/div[2]/div[2]/div/div[1]/div[1]/div[{current}]/div[2]/div[1]",
    }
    assert MistralChrome(driver_config=[], email="wrong_email", password="wrong_password")._model_url == "https://chat.mistral.ai/chat"


def test_claude_chrome():
    with pytest.raises(ValueError, match="Cannot Login given the credentials"):
        with ClaudeChrome(
            driver_config=[], email="wrong_email", password="wrong_password", retries_attempt=1
        ) as session:  # A single session started with ChartGPT
            pass
    assert ClaudeChrome(driver_config=[], email="wrong_email", password="wrong_password")._elements_identifier == {
        "Email": '//*[@id="email"]',
        "Login_Button": "/html/body/div[2]/div/main/div[1]/div/div[1]/form/button",
        "Login_Code": "/html/body/div[2]/div/main/div[1]/div/div[1]/form/div[3]/input",
        "Login_Code_Confirmation": "/html/body/div[2]/div/main/div[1]/div/div[1]/form/button",
        "Start_Chat_Button": "/html/body/div[2]/div/main/div[1]/div[2]/div[1]/div/div/fieldset/div/div[2]/div[2]/button",
        "Prompt_Text_Area": "/html/body/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/div/fieldset/div[2]/div[1]/div[1]/div/div/div/div/p",  # noqa: E501
        "Prompt_Text_Area_Submit": "/html/body/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div/div/fieldset/div[2]/div[1]/div[2]/div[2]/div/button",  # noqa: E501
        "Prompt_Text_Area_Output": "/html/body/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div[{current}]/div/div/div[1]/div/div",
    }
    assert ClaudeChrome(driver_config=[], email="wrong_email", password="wrong_password")._model_url == "https://claude.ai/login"


def test_langchain_model():
    model = FreeLLMs(model_name="PreplexityChrome", llm_kwargs={"driver_config": [], "email": "email", "password": "password"})
    model.invoke("How are you doing?")
    with pytest.raises(ValueError):
        FreeLLMs(model_name="NewModel", llm_kwargs={"driver_config": [], "email": "email", "password": "password"})
