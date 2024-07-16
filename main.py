import os
import pandas as pd
from tqdm import tqdm
from argparse import ArgumentParser
from data_loader import DataLoader
from prompter import Prompter
from model_loader import ModelLoader



def build_arguments():

    parser = ArgumentParser()

    # parser.add_argument('-d', dest='dataset',
    #                     type=str, required=True,
    #                     help='Dataset name to be loaded and processed.')
    
    parser.add_argument('-l', dest='utterance_len',
                        type=int, default=100,
                        help='Minimum token number of utternace to be filled in. (Default=100)')
    
    parser.add_argument('-r', dest='role',
                        type=str, default='Explainer',
                        help='Target speaker role. (Default=\'Explainer\')')

    parser.add_argument('-w', dest='window',
                        type=int, default=2,
                        help='Number of utterances prior to and following the target utterance. (Default=2)')
    
    parser.add_argument('-m', dest='model',
                        type=str, required=True,
                        help='Name of large language model to be loaded via HuggingFace API.')
    
    parser.add_argument('--local', dest='local',
                        action='store_true',
                        help='Load LLM to local device from HuggingFace API.')

    return parser.parse_args()





if __name__ == "__main__":
    
    args = build_arguments()
    

    prompter = Prompter(prompt_cfg_filename='prompts.json')

    model_loader = ModelLoader(model_name=args.model,
                               local=args.local)



    for root, dirs, files in os.walk('WIRED/data/corpus_dialogs'):
        for file in tqdm(files):
            # print(file)
            # df = pd.read_json(os.path.join(root, file))

            data_loader = DataLoader(path=os.path.join(root, file),
                                     role=args.role,
                                     utterance_len=args.utterance_len,
                                     window=args.window,
                                     replace=True)
            
            index_list = data_loader.filter_utternace()
            for index in index_list:
                diaolgue = data_loader.parse_diaolgue(index=index)
                # print(diaolgue)
                prompt = prompter.build_prompt(diaolgue)



                model_loader.prompt(prompt)
    