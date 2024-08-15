import json
import os
import sys
import requests
import torch
from openai import OpenAI
from time import sleep
from transformers import AutoModelForCausalLM, AutoTokenizer


# path for downloading LLMs
os.makedirs('llm_cache', exist_ok=True)
os.environ['HF_HOME'] = 'llm_cache'



def model_to_hf_id(model: str):
    
    supported_models = {
        'mistralai': ['Mistral-7B-Instruct-v0.3', 'Mixtral-8x7B-Instruct-v0.1'],
        'ybelkada': ['Mixtral-8x7B-Instruct-v0.1-bnb-4bit'],
        'openchat': ['openchat-3.5-0106'],
        'meta-llama': ['Meta-Llama-3-8B-Instruct', 'Meta-Llama-3.1-8B-Instruct']
    }
    
    print(f'Supported models: {[value for values in supported_models.values() for value in values]}')
    
    try:
        for key, values in supported_models.items():
            if model in values:
                return f'{key}/{model}'
    except:
        raise ValueError('Invalid model. Please choose among the supported models.')


def load_hf_interface(model_id: str):
    # HF API
    url = f'https://api-inference.huggingface.co/models/{model_id}'
    # accessing HF API
    with open('key.json', 'r') as f:
        key = json.loads(f.read())['HuggingFace']
    
    return url, key


def load_openai_interface(model_id: str):
    # accessing OpenAI API
    with open('key.json', 'r') as f:
        key = json.loads(f.read())['OpenAI']
    return key


def load_hf_llm(model_id: str, api_token: str):

    model = AutoModelForCausalLM.from_pretrained(model_id,
                                                 cache_dir='llm_cache',
                                                 device_map='auto',
                                                 token=api_token)
    tokenizer = AutoTokenizer.from_pretrained(model_id,
                                              cache_dir='llm_cache',
                                              device_map='auto',
                                              token=api_token)
    return model, tokenizer




class HFModelLoader(object):

    def __init__(self,
                 model_name: str,
                 local: bool):
        """
        Initialize HFModelLoader for accessing a designated LLM.
        :param model_name: Name of the LLM to be accessed.
        :param local: Whether to download the LLM to local device.
        """
        super().__init__()

        self.model_id = model_to_hf_id(model_name)
        self.url, self.key = load_hf_interface(self.model_id)
        
        self.local = local
        if self.local:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model, self.tokenizer = load_hf_llm(model_id=self.model_id,
                                                     api_token=self.key)


    def api_query(self,
                  prompt: str,
                  n_tokens: int = 128,
                  retry_delay: int = 2,
                  max_retries: int = 10,
                  verbose: bool = False) -> str:
        """
        Build a payload, send it to the HuggingFace inference API and extract the text generation from the API
        response. Retry if the API response is not as expected.
        :param prompt: The string to prompt the LMM with.
        :param n_tokens: Maximum number of tokens generated. Low or default API values result in incomplete generations. May
        need adjustment depending on prompting configuration.
        :param retry_delay: How many seconds to wait before sending another request to the API. This should be kept low to
        not misuse the API.
        :param max_retries: Maximum number of retries. This should be kept low to not misuse the API.
        :param verbose: If True, information on each individual API request is printed to console.
        :return: The string generated by the LMM.
        """

        # build header and JSON request payload:
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {self.key}'}
        json_request = {'inputs': prompt,
                        'parameters': {'max_new_tokens': n_tokens},
                        'options': {'wait_for_model': True}}
        payload = json.dumps(json_request)

        # handle API response issues:
        proper_response = False
        n_retries = 0

        while not proper_response:
            # API request:
            response = requests.request('POST', self.url, headers=headers, data=payload)
            # check for expected text generation response code:
            if f'{response}' == '<Response [200]>':
                if verbose:
                    print('HF API responding.')
                proper_response = True
            else:
                if verbose:
                    print(f'Improper response from HF API.\nResponse: {response}\nResponse content: {response.content}')
                if n_retries <= max_retries:
                    if verbose:
                        print(f'Waiting {retry_delay}s to retry...')
                    # wait for the specified number of seconds before trying again:
                    sleep(retry_delay)
                    n_retries += 1
                else:
                    sys.exit(f'Maximum number of retries ({n_retries}) reached, stopping API requests.\nCheck API availability and API access token.')

        return json.loads(response.content.decode('utf-8'))[0]['generated_text']
    

    def prompt(self,
               prompt: str):
        
        if self.local:
            model_inputs = self.tokenizer([prompt], return_tensors='pt').to(self.device)
            self.model.to(self.device)
            generated_ids = self.model.generate(**model_inputs, max_new_tokens=512, do_sample=True)
            raw_output = self.tokenizer.batch_decode(generated_ids)[0]
        else:
            raw_output = self.api_query(prompt=prompt)

        return raw_output
    


class OpenAIModelLoader(object):

    def __init__(self,
                 model_name: str):
        """
        Initialize OpanAIModelLoader for accessing a designated LLM.
        :param model_name: Name of the LLM to be accessed.
        """
        super().__init__()

        self.model = model_name
        self.self.key = load_openai_interface()


    def prompt(self,
               prompt: str):
        
        client = OpenAI(api_key=self.key)

        completion = client.chat.completions.create(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}]
        )

        print(completion)



if __name__ == "__main__":
    pass
