import json
import pandas as pd


def load_prompt_config(config_name: str) -> dict:
    """
    Load a prompting configuration file.
    :param config_name: Name of the prompting configuration file.
    :return: Dictionary prompting configuration of the given task.
    """
    with open(config_name, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    return config


class Prompter(object):
    """
    Class to build full prompts based on a prompting configuration.
    """
    def __init__(self, prompt_cfg_filename: str):
        """
        Initialize Prompter instance using a prompting configuration file.
        :param prompt_cfg_filename: Name of the prompting configuration file.
        :param task: Task name to be prompting configuration file.
        """
        super().__init__()
        # load prompting configuration:
        self.cfg = load_prompt_config(prompt_cfg_filename)

    def __call__(self, dialogue):
        """
        Convenience method passing all arguments to build_prompt() method.
        :param footer_idx: Sample index for prompt footer data.
        :return: Fully built prompt string based on prompting configuration.
        """
        return self.build_prompt(dialogue=dialogue)

    # not sure if this is needed here
    def build_one_shot_prompt(self):
        prompt = str()
        if 'one_shot_instruction' in self.cfg:
            prompt += self.cfg['one_shot_instruction']
        return prompt

    def build_prompt(self,
                     dialogue: str,
                     topic: str = '',
                     explainer: str = ' teacher',
                     explainee: str = ' student',
                     instruction: str = '') -> str:
        """
        Build full prompt based on prompting configuration and footer sample index.
        :param topic: Mentioning topic of explanatory dialogue in the prompt (optional).
        :param explainer: Description of the explaner participating in the dialogue.
        :param explainee: Description of the explanee participating in the dialogue.
        :param instruction: Perturbation for tuning model-generated dialogue.
        :return: Fully built prompt string based on prompting configuration.
        """
        
        prompt = str()
        
        # add header
        prompt += self.cfg['header']
        
        prompt = prompt.replace('{topic}', topic)
        prompt = prompt.replace('{explainer}', explainer)
        prompt = prompt.replace('{explainee}', explainee)
        
        prompt += f'{dialogue}\n'

        #TODO: prompt += instruction

        # add footer:
        prompt += self.cfg['footer']
        print(prompt)
        return prompt


if __name__ == "__main__":
    pass