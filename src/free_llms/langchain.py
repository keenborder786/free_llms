from typing import Any, Dict, List, Optional

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.pydantic_v1 import root_validator

from free_llms.models import ClaudeChrome, GPTChrome, MistralChrome, PreplexityChrome


class FreeLLMs(LLM):
    model_name: Optional[str] = None
    """One of the following model names to choose from: GPTChrome,PreplexityChrome,,ClaudeChrome"""
    llm_kwargs: Dict[str, Any]
    """Keyword arguments to be passed to free_llms.models.LLMChrMistralChromeome"""

    @root_validator()
    def start_model(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""

        models = {"GPTChrome": GPTChrome, "PreplexityChrome": PreplexityChrome, "MistralChrome": MistralChrome, "ClaudeChrome": ClaudeChrome}
        if values["model_name"] not in models:
            raise ValueError(f'The given model {values['model_name']} is not correct. Please pass one of the following {list(models.keys())}')
        values["client"] = models[values["model_name"]](values["llm_kwargs"])
        return values

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        self.client.login()
        self.client.send_prompt(prompt).content
        self.client.driver.quit()
