import sys
sys.path.insert(0,'/Users/mac/free_llms/src')
from free_llms.models import PreplexityChrome

driver_config = []  # pass in selnium driver config except for the following ["--disable-gpu", f"--window-size=1920,1080"]
with PreplexityChrome(
    driver_config=driver_config,
    email="",  # for preplexity we do not need email
    password="",  # for preplexity we do not need password
) as session:  # A single session started with Preplexity
    data = session.send_prompt("""Make the following sentence correct:
    I did went to Lahore.                           
    """)  # First Message
    data = session.send_prompt("""Who is george hotz?""")  # Second Message, right now each message is independent in preplexity ai
    print(session.messages)  # Messages in the current session in pair of <Human,AI>
