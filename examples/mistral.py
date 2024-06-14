from free_llms.models import MistralChrome

driver_config = []  # pass in selnium driver config except for the following ["--disable-gpu", f"--window-size=1920,1080"]
with MistralChrome(
    driver_config=driver_config,
    email="21110290@lums.edu.pk",  # Mistral Email
    password="",  # Mistral Password
) as session:  # A single session started with Mistral
    session.send_prompt("Write a short long horro story of 100 woirds")
    session.send_prompt("Make it funny")
    print(session.messages)
