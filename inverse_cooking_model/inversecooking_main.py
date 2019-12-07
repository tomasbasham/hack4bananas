import os
import pickle
import random
import time
from collections import Counter
from io import BytesIO

import h5py
import matplotlib.pyplot as plt
import numpy as np
import requests
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms

from inversecooking.args import get_parser
from inversecooking.model import get_model
from inversecooking.utils.output_utils import prepare_output


data_dir = './data'
use_gpu = False
device = torch.device('cuda' if torch.cuda.is_available() and use_gpu else 'cpu')
map_loc = None if torch.cuda.is_available() and use_gpu else 'cpu'



def load_vocabularies():
    ingrs_vocab = pickle.load(open(os.path.join(data_dir, 'ingr_vocab.pkl'), 'rb'))
    vocab = pickle.load(open(os.path.join(data_dir, 'instr_vocab.pkl'), 'rb'))

    ingr_vocab_size = len(ingrs_vocab)
    instrs_vocab_size = len(vocab)
    output_dim = instrs_vocab_size
    return ingr_vocab_size, instrs_vocab_size, ingrs_vocab, vocab


def load_model():
    t = time.time()
    import sys; sys.argv=['']; del sys
    args = get_parser()
    args.maxseqlen = 15
    args.ingrs_only=False
    model = get_model(args, ingr_vocab_size, instrs_vocab_size)
    # Load the trained model parameters
    model_path = os.path.join(data_dir, 'modelbest.ckpt')
    model.load_state_dict(torch.load(model_path, map_location=map_loc))
    model.to(device)
    model.eval()
    model.ingrs_only = False
    model.recipe_only = False
    print ('loaded model')
    print ("Elapsed time:", time.time() -t)
    return model


def generate_img_transforms():
    transf_list_batch = []
    transf_list_batch.append(transforms.ToTensor())
    transf_list_batch.append(transforms.Normalize((0.485, 0.456, 0.406), 
                                                (0.229, 0.224, 0.225)))
    to_input_transf = transforms.Compose(transf_list_batch)
    return to_input_transf


def set_data_source(use_urls):
    if not use_urls:
        demo_imgs = os.listdir(image_folder)
        random.shuffle(demo_imgs)

    demo_urls = ['https://food.fnr.sndimg.com/content/dam/images/food/fullset/2013/12/9/0/FNK_Cheesecake_s4x3.jpg.rend.hgtvcom.826.620.suffix/1387411272847.jpeg',
                'https://www.196flavors.com/wp-content/uploads/2014/10/california-roll-3-FP.jpg']

    demo_files = demo_urls if use_urls else demo_imgs
    return demo_files


def print_output(outs, valid):
    

    print ('RECIPE', num_valid)
    num_valid+=1
    #print ("greedy:", greedy[i], "beam:", beam[i])

    BOLD = '\033[1m'
    END = '\033[0m'
    print (BOLD + '\nTitle:' + END,outs['title'])

    print (BOLD + '\nIngredients:'+ END)
    print (', '.join(outs['ingrs']))

    print (BOLD + '\nInstructions:'+END)
    print ('-'+'\n-'.join(outs['recipe']))

    print ('='*20)

    

if __name__ == "__main__":

    ingr_vocab_size, instrs_vocab_size, ingrs_vocab, vocab = load_vocabularies()

    model = load_model()

    to_input_transf = generate_img_transforms()

    greedy = [True, False, False, False]
    beam = [-1, -1, -1, -1]
    temperature = 1.0
    numgens = len(greedy)

    use_urls = False # set to true to load images from demo_urls instead of those in test_imgs folder
    show_anyways = False #if True, it will show the recipe even if it's not valid
    image_folder = os.path.join(data_dir, 'demo_imgs')

    demo_files = set_data_source(use_urls)


    for img_file in demo_files:
    
        if use_urls:
            response = requests.get(img_file)
            image = Image.open(BytesIO(response.content))
        else:
            image_path = os.path.join(image_folder, img_file)
            image = Image.open(image_path).convert('RGB')
        
        transf_list = []
        transf_list.append(transforms.Resize(256))
        transf_list.append(transforms.CenterCrop(224))
        transform = transforms.Compose(transf_list)
        
        image_transf = transform(image)
        image_tensor = to_input_transf(image_transf).unsqueeze(0).to(device)
        
        plt.imshow(image_transf)
        plt.axis('off')
        plt.show()
        plt.close()
        
        num_valid = 1
        for i in range(numgens):
            with torch.no_grad():
                outputs = model.sample(image_tensor, greedy=greedy[i],
                                    temperature=temperature, beam=beam[i], true_ingrs=None)
                
            ingr_ids = outputs['ingr_ids'].cpu().numpy()
            recipe_ids = outputs['recipe_ids'].cpu().numpy()
                
            outs, valid = prepare_output(recipe_ids[0], ingr_ids[0], ingrs_vocab, vocab)
            

            if valid['is_valid'] or show_anyways:

                print_output(outs, valid)
            
            else:
                print ("Not a valid recipe!")
                print ("Reason: ", valid['reason'])
