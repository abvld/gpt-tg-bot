import openai
from typing import Dict, List, Tuple


class GPTApi:
    def __init__(self):
        pass
    
    def message(self, messages: List[Dict[str, str]]) -> Tuple[str, int]:

        try:
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        except openai.error.InvalidRequestError as e:
            return "Reached the max context length of 4096 tokens. Please restart end the chat and start a new one.", 0
        
        if hasattr(completion, 'choices') and len(completion.choices) > 0:
            gpt_reply = completion.choices[0].message.content
            total_tokens = completion.usage["total_tokens"]
        
            return gpt_reply, total_tokens
        
        return "There was an error trying to contact the OpenAI API", 0