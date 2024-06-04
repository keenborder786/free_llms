from free_llms.models import GPTChrome
driver_config = ["--disable-gpu", "--window-size=1920,1080"] # pass in selnium driver config
with GPTChrome(driver_config,'21110290@lums.edu.pk','Keenborder@536a') as session: # A single session started with ChartGPT
    data = session.send_prompt('Tell me a horror story in 150 words') # First Message
    data1 = session.send_prompt('Now make it funny') # Second message
    print(session.messages) # Messages in the current session in pair of <Human,AI>
        