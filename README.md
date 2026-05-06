# Board Game Recommendations

## Problem Statement

Based on the boardgamegeek rankings dataset, I am creating a system for a boardgame designer.

The idea here is to provide some guidance on mechanics and themes based on what has been successful in the past.

## Dataset

I obtained my dataset from Kaggle:

Kaggle: https://www.kaggle.com/datasets/jvanelteren/boardgamegeek-reviews/data

Primarily using the `games_detailed_info2025.csv`.

## Methodology

My methodology is to extract the mechanics and themes and use them as features to predict ratings for boardgames. Then I use a Neural Network to train and model the complex relationships between the features to predict ratings.

The result is a model which can predict the rating of a boardgame to give designers of ideas of what combination of mechanics and themes are likely to be successful.

## Results

I have created a model which predicts boardgame rating based on mechanics and themes. It is able to predict rating within ~0.3 of the actual rating. Extending this, allows for predicting which mechanic/theme combinations are most likely to be successful.

## About this repo

The repository is this repository which is a monolithic repository containing both the frontend and backend. The frontend is a next.js react app while the backend is a python FastAPI app that serves the model.

The pretrained model was created using Colab and can be found in the `models/` directory.

The Colab notebook within this repo, in the `notebooks/` directory and contains the analysis, training, and my explorations.

## LLM/Agentic usage in this project

I did use an LLM for much of this work, more for the coding specifics and debugging.

My data processing script was primarily written with Antigravity/Gemini 3.1 Pro. I used a spec for it (`SPEC_PARSER.md`), and modified to regenerate the parser multiple times as I explored more about my data and refined my approach.

My EDA was primarily my own exploration, using code snippets and light guidance from the GEMINI 2.5 Flash built into Co-lab.

My backend API code was mostly hand-written, with light Antigravity/Gemini 3.1 Pro usage.

My frontend Next.JS/React code was primarily generated using Antigravity/Gemini 3.1 Pro, with me providing the high level structure and the LLM filling in the details.

## MVP/Deployment

I have deployed an application: https://frontend-ui-production-1ab7.up.railway.app

It is deployed via Railway (https://railway.app). It contains 2 notes, the backend and frontend ui, using this repo as a base for each of those nodes (with different build/run commands).
