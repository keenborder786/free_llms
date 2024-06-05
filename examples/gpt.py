from free_llms.models import GPTChrome
driver_config = [] # pass in selnium driver config except for the following ["--disable-gpu", f"--window-size=1920,1080"]
with GPTChrome(driver_config=driver_config,
               email = 'email',
               password = 'password') as session: # A single session started with ChartGPT
    data = session.send_prompt("""Write an SQL Query which shows how to get third highest salary
    """) # First Message
    data1 = session.send_prompt('Now convert it into python') # Second message
    print(session.messages) # Messages in the current session in pair of <Human,AI>