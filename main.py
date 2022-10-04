from fastapi import FastAPI
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import json


app = FastAPI()
es = Elasticsearch([{"host": "localhost", "port": 9200, "scheme": "index"}])

@app.get("/")
async def root():
    file = open('sites.json', 'r')
    json_data = json.load(file)
    # for data in json_data:
    #     es.index(index="sites", body=data)
    return {"message": es.info()}


@app.get("/{index}")
async def say_hello(index: str):
    hits = []
    for hit in es.search(index=index, body={"query": {"match_all": {}}}).get('hits').get('hits'):
        html = hit.get('_source').get('content')
        text = BeautifulSoup(html, features="html.parser").get_text().replace("\n", " ").strip()
        headings = BeautifulSoup(html, features="html.parser").find_all([f'h{i}' for i in range(1, 4)])
        headings_arr = []
        for head in headings:
            if len(head) > 1:
                for h in head:
                    headings_arr.append(h.get_text().replace("\n", " ").strip()) if len(h.get_text().replace("\n", " ").strip()) > 1 else None
            else:
                headings_arr.append(head.get_text().replace("\n", " ").strip()) if len(head.get_text().replace("\n", " ").strip()) > 1 else None

        hits.append({
            "headings": headings_arr,
            "text": text
        })
    # for hit in hits:
    #     print(es.index(index="texts", body=hit))
    return {"message": json.dumps(hits)}
