# FREE_LLMs
<img src="assets/logo.jpeg" alt="Logo" width="10%">

## 🤔 What is Free_LLMs?
- Free LLMs is a framework allowing you to use browser based interface of large language models such as ChatGPT in an API like style.
- Free LLMs is just an easier way to interact with the Browser Based LLMs and nothing else. All ownerships belongs to the original owners of respective LLMs.

## Quick Install

With pip:
```bash
pip install free_llms
```

## Usage

```python

from free_llms.models import GPTChrome
driver_config = ["--disable-gpu", "--window-size=1920,1080"] # pass in selnium driver config
with GPTChrome(driver_config,'21110290@lums.edu.pk','') as session: # A single session started with ChatGPT. Put in your email and password for ChatGPT account.
    data = session.send_prompt('Tell me a horror story in 150 words') # First Message
    data1 = session.send_prompt('Now make it funny') # Second message
    print(session.messages) # Messages in the current session in pair of <Human,AI>
        
```