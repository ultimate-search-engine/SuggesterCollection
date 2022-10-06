from typing import Dict, Union

from fastapi import FastAPI
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import json
from components.management import Management

app = FastAPI()
elastic = Management()


@app.get("/")
async def root():
    return elastic.root()


@app.get("/suggest/{value}")
async def suggest(value: str):
    return elastic.suggest(value)


@app.get("/import")
async def import_initial():
    return elastic.initial_import()


@app.get("/import/{index}")
async def importing(index: str):
    return elastic.index_import(index)


@app.get("/create/{index}")
async def creating(index: str):
    mapping = {
        "settings": {
            "number_of_shards": 4
        },
        "mappings": {
            'properties': {
                'autocomplete': {
                    'type': 'keyword'
                },
                'headings': {
                    'type': 'text'
                },
                'text': {
                    'type': 'text'
                }
            }
        }
    }
    return elastic.create_index(index, mapping)


@app.get("/delete/{index}")
async def deleting(index: str):
    return elastic.delete_index(index)


@app.get("/show/{index}")
async def show(index: str):
    return elastic.show_index(index)
