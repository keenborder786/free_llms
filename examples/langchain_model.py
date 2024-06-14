from free_llms.langchain_model import FreeLLMs
from langchain.prompts import PromptTemplate

# model name can be any of the following:
model = FreeLLMs(model_name="PreplexityChrome", llm_kwargs={"driver_config": [], "email": "email", "password": ""})

prompt = PromptTemplate.from_template("Write me a joke about {topic}")
chain = prompt | model | str
print(chain.invoke({"topic": "coding"}))
