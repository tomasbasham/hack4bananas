# Granma Bot

Facebook messenger chat bot for generating food recipes.

## Inspiration

Not being satisfied with being unable to reproduce culinary experiences had at
restaurants or from images of food found on popular image hosting websites (Instagram
;-))

## What it does

We've created a Facebook Messenger message bot that generates recipes from the
photos that are submitted by our users.

## How we built it

The messenger application consists of a NodeJS server reading in user inputs via a webhook
and responding with messages returned from a backend application that is communicated with
asynchronously.

For the backend we created a small Flask app that integrates a Facebook curated PyTorch
machine learning model [InverseCooking](https://github.com/facebookresearch/inversecooking). We pre-process and
feed these images to the model which then generates:

 - a recipe name
 - set of ingredients
 - set of instructions

## Challenges we ran into

We struggled greatly with the Python module system which has historically been a pain in
the ass.

## Accomplishments that we're proud of

IT WORKS!!!!

## What we learned

How to integrate PyTorch with Facebook messenger through the API.
