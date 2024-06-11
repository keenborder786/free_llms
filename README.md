<div align="center">
 <img src="https://github.com/keenborder786/free_llms/blob/ea08f8ef5ae33e57aaff18f28568df426a354a4c/assets/logo.jpeg" alt="Logo" width="10%">
</div>

# FREE_LLMs

![PyPi Published](https://github.com/keenborder786/free_llms/actions/workflows/python-publish.yml/badge.svg?event=release)
![Linter](https://github.com/keenborder786/free_llms/actions/workflows/linter.yml/badge.svg?event=push)

## 🤔 What is Free_LLMs?

Free LLMs is a framework that allows you to use a browser-based interface for large language models such as ChatGPT in an API-like style for FREE!!!. It provides an easier way to interact with browser-based LLMs and nothing else. All ownership belongs to the original owners of the respective LLMs.

## Quick Install

With pip:
```bash
pip install free_llms
```

## Models-Supported:

| Model              | Supported | 
| ------------------ | ------------------------- | 
| ChatGPT            | ✅                        |
| Preplexity ai      | ✅           | 
| Mistral            | ✅           | 
| Claude               | ✅           |



## ChatGPT

```python

from free_llms.models import GPTChrome
driver_config = [] # pass in selnium driver config except for the following ["--disable-gpu", f"--window-size=1920,1080"]
with GPTChrome(driver_config=driver_config,
               email = 'email',
               password = 'password') as session: # A single session started with ChartGPT
    data = session.send_prompt("""Write an SQL Query which shows how to get third highest salary
    """) # First Message
    data1 = session.send_prompt('Now convert it into python') # Second message
    print(session.messages) # Messages in the current session in pair of <Human,AI>
```


## Preplexity AI 

```python

from free_llms.models import PreplexityChrome
driver_config = [] # pass in selnium driver config except for the following ["--disable-gpu", f"--window-size=1920,1080"]
with PreplexityChrome(driver_config=driver_config,
               email = '', # for preplexity we do not need email
               password = '',# for preplexity we do not need password
               ) as session: # A single session started with Preplexity
    data = session.send_prompt("""Make the following sentence correct:
    I did went to Lahore.                           
    """) # First Message
    data = session.send_prompt("""Who is george hotz?""") # Second Message, right now each message is independent in preplexity ai
    print(session.messages) # Messages in the current session in pair of <Human,AI>

```


## Mistral

```python

from free_llms.models import MistralChrome
driver_config = [] # pass in selnium driver config except for the following ["--disable-gpu", f"--window-size=1920,1080"]
with MistralChrome(driver_config=driver_config,
               email = '21110290@lums.edu.pk', # Mistral Email
               password = '',# Mistral Password
               ) as session: # A single session started with Mistral
    session.send_prompt('Write a short long horro story of 100 woirds')
    session.send_prompt('Make it funny')
    print(session.messages)
```


## Claude

```python
from free_llms.models import ClaudeChrome
driver_config = [] # pass in selnium driver config except for the following ["--disable-gpu", f"--window-size=1920,1080"]
with ClaudeChrome(driver_config=driver_config,
               email = 'mohammad.mohtashim78@gmail.com',
               password = '', # password not needed for ClaudeChrome
               ) as session: # A single session started with ClaudeChrome
    # once you login, you will get a code at your email which you need to type in
    session.send_prompt('What is silicon valley?')
    session.send_prompt('How many seasons it had?')
    print(session.messages)

```


## Note:

- Free_LLMs only uses a `Patched Chrome Driver` as it's main driver. The driver can be found [here](https://github.com/ultrafunkamsterdam/undetected-chromedriver/tree/master)