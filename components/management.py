from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import json


class Management:
    host = ""
    port = None
    scheme = ""
    es = None

    def __init__(self, host: str = 'localhost', port: int = 9200, scheme: str = 'index'):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.es = Elasticsearch([{"host": host, "port": port, "scheme": scheme}])

    def root(self):
        indices = self.es.indices.get_alias()
        indices = [index_name for index_name, value in indices.items()]
        return {"message": self.es.info(),
                'indices': indices}

    def initial_import(self):
        file = open('sites.json', 'r')
        json_data = json.load(file)
        for data in json_data:
            self.es.index(index="sites", body=data)
        return {'message': self.es.search(index='sites')}

    def index_import(self, index: str):
        hits = []
        for hit in self.es.search(index=index, body={"query": {"match_all": {}}}).get('hits').get('hits'):
            html = hit.get('_source').get('content')
            text = BeautifulSoup(html, features="html.parser").get_text().replace("\n", " ").strip()
            headings = BeautifulSoup(html, features="html.parser").find_all([f'h{i}' for i in range(1, 4)])
            headings_arr = []
            autocomplete = []
            for head in headings:
                if len(head) > 1:
                    for h in head:
                        headings_arr.append(h.get_text().replace("\n", " ").strip()) if len(
                            h.get_text().replace("\n", " ").strip()) > 1 else None
                else:
                    headings_arr.append(head.get_text().replace("\n", " ").strip()) if len(
                        head.get_text().replace("\n", " ").strip()) > 1 else None
            for title in headings_arr:
                autocomplete.extend(title.split())
            autocomplete.extend(text.split())
            print(len(autocomplete))
            hits.append({
                "headings": headings_arr,
                "text": text,
                'autocomplete': autocomplete
            })

        for hit in hits:
            print(self.es.index(index="texts", body=hit))

        return {"message": json.dumps(hits)}

    def delete_index(self, index: str):
        return {"message": self.es.indices.delete(index=index)}

    def create_index(self, index: str, mappings: object):
        return {"message": self.es.indices.create(index=index, body=mappings, pretty=True)}

    def show_index(self, index: str):
        return {'message': self.es.search(index=index)}

    def suggest(self, value: str):
        query = {
            "size": 0,
            "aggregations": {
                "autocomplete": {
                    "filter": {
                        "prefix": {
                            "autocomplete": "{}".format(value)
                        }
                    },
                    "aggregations": {
                        "autocomplete": {
                            "terms": {
                                "field": "autocomplete",
                                "include": "{}.*".format(value)
                            }
                        }
                    }
                }
            }
        }
        buckets = self.es.search(index='texts', body=query)['aggregations']['autocomplete']['autocomplete']['buckets']
        return {'message': [suggest['key'] for suggest in buckets]}

