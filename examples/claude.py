from free_llms.models import ClaudeChrome

driver_config = []  # pass in selnium driver config except for the following ["--disable-gpu", f"--window-size=1920,1080"]
with ClaudeChrome(
    driver_config=driver_config,
    email="mohammad.mohtashim78@gmail.com",
    password="Keenborder@0290",  # password not needed for ClaudeChrome
) as session:  # A single session started with ClaudeChrome
    # once you login, you will get a code at your email which you need to type in
    session.send_prompt("What is silicon valley?")
    session.send_prompt("How many seasons it had?")
    print(session.messages)
