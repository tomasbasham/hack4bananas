# Granma Bot

Facebook messenger chat bot for generating food recipes.

## Inspiration

Not being satisfied with being unable to reproduce culinary experiences had at
restaurannts or from images of food found on popular image hosting websites (Instagram
;-)), we've created a Facebook Messenger message bot that generates from recipes from the
photos that are submitted by our users.

## Implementation details

The messenger application consists of a nodejs server reading in user inputs via a webhook
and responding with messages returned from a backend application that is communicated with
asynchronously.

For the backend we created a small Flask app that integrates a Facebook curated PyTorch
machine learning model [InverseCooking](https://github.com/facebookresearch/inversecooking). We preprocess and
feed these images to the model which then generates:

 - a recipe name
 - set of ingredients
 - set of instructions
