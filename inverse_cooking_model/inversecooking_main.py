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

from inverse_cooking_model.inversecooking.args import get_parser
from inverse_cooking_model.inversecooking.model import get_model
from inverse_cooking_model.inversecooking.utils.output_utils import prepare_output


data_dir = './data'
use_gpu = False
device = torch.device('cuda' if torch.cuda.is_available()
                      and use_gpu else 'cpu')
map_loc = None if torch.cuda.is_available() and use_gpu else 'cpu'
image_folder = os.path.join(data_dir, 'demo_imgs')


def load_vocabularies():
    ingrs_vocab = pickle.load(
        open(os.path.join(data_dir, 'ingr_vocab.pkl'), 'rb'))
    vocab = pickle.load(
        open(os.path.join(data_dir, 'instr_vocab.pkl'), 'rb'))

    ingr_vocab_size = len(ingrs_vocab)
    instrs_vocab_size = len(vocab)
    output_dim = instrs_vocab_size
    return ingr_vocab_size, instrs_vocab_size, ingrs_vocab, vocab


def load_model(ingr_vocab_size, instrs_vocab_size):
    t = time.time()
    import sys
    sys.argv = ['']
    del sys
    args = get_parser()
    args.maxseqlen = 15
    args.ingrs_only = False
    model = get_model(args, ingr_vocab_size, instrs_vocab_size)
    # Load the trained model parameters
    model_path = os.path.join(data_dir, 'modelbest.ckpt')
    model.load_state_dict(torch.load(model_path, map_location=map_loc))
    model.to(device)
    model.eval()
    model.ingrs_only = False
    model.recipe_only = False
    print ('loaded model')
    print ("Elapsed time:", time.time() - t)
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


def transf2image(image):
    transf_list = []
    transf_list.append(transforms.Resize(256))
    transf_list.append(transforms.CenterCrop(224))
    transform = transforms.Compose(transf_list)

    image_transf = transform(image)
    return image_transf


def get_default_generation_params():
    greedy = [True, False, False, False]
    beam = [-1, -1, -1, -1]
    temperature = 1.0
    return greedy, temperature, beam


def viz_image(image_url):
    image = url2Image(img_url)
    image_transf = transf2image(image)
    plt.imshow(image_transf)
    plt.axis('off')
    plt.show()
    plt.close()


def predict(model, ingrs_vocab, vocab, image_url, temperature=1.0, beam=[-1, -1, -1, -1], greedy=[True, False, False, False]):
    to_input_transf = generate_img_transforms()
    image = url2Image(image_url)
    image_transf = transf2image(image)
    image_tensor = to_input_transf(image_transf).unsqueeze(0).to(device)

    # numgens = len(greedy)
    results = []
    for i in range(len(greedy)):
        with torch.no_grad():
            outputs = model.sample(image_tensor, greedy=greedy[i],
                                   temperature=temperature, beam=beam[i], true_ingrs=None)

        ingr_ids = outputs['ingr_ids'].cpu().numpy()
        recipe_ids = outputs['recipe_ids'].cpu().numpy()

        outs, valid = prepare_output(
            recipe_ids[0], ingr_ids[0], ingrs_vocab, vocab)

        result = {'output': outs, 'validity': valid}
        if valid['is_valid']:
            results.append(result)
            return results

        else:
            print ("Not a valid recipe! Trying for the {} time".format(i+1))



def url2Image(img_file):
    response = requests.get(img_file)
    image = Image.open(BytesIO(response.content))
    return image


def path2Image(img_file):
    global image_folder
    image_path = os.path.join(image_folder, img_file)
    image = Image.open(image_path).convert('RGB')
    return image
