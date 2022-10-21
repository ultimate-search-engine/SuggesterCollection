from elasticsearch import Elasticsearch
from components.text_editor import TextEditor
import json

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9200
DEFAULT_SCHEME = 'index'
SENTENCE_QUERY = {
    'query': {
        "multi_match": {
            'query': '',
            'fields': ['headings', 'text']
        }
    },
    "highlight": {
        "fields": {
            "*": {}
        },
        "type": "fvh",
        "fragment_size": 20,
        "number_of_fragments": 100
    }
}


class Management:
    host = ""
    port = None
    scheme = ""
    es = None
    text_editor = TextEditor()

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, scheme: str = DEFAULT_SCHEME):
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

    def import_array_to_index(self, index: str, requested: list):
        for data in requested:
            json_data = json.dumps(data)
            self.es.index(index=index, body=json_data)
        return {'message': self.es.search(index=index)}

    def import_record_to_index(self, index: str, requested: object):
        data = json.dumps(requested)
        self.es.index(index=index, body=data)
        return {'message': self.es.search(index=index)}

    def search_text(self, text: str, index: str):
        search_query = {"query": {
            "bool": {
                "must": {
                    "query_string": {
                        "query": "{}".format(text)
                    }
                }
            }
        }}
        return self.es.search(index=index, query=search_query)

    def count_occurrences(self, index: str):
        documents = self.show_index(index)['message']['hits']['hits']
        print(documents)
        return self.es.mtermvectors(index=index, fields=['headings', 'text'],
                                    term_statistics=True, ids=[document['_id'] for document in documents])

    def index_default_import(self, index: str):
        hits = self.text_editor.html_to_text(self.get_index_data(index))
        for hit in hits:
            print(self.es.index(index="texts", body=hit))

        return {"message": json.dumps(hits)}

    def delete_index(self, index: str):
        return {"message": self.es.indices.delete(index=index)}

    def create_index(self, index: str, mappings: object):
        return {"message": self.es.indices.create(index=index, body=mappings, pretty=True)}

    def get_index_data(self, index: str):
        return self.es.search(index=index, body={"query": {"match_all": {}}}).get('hits').get('hits')

    def show_index(self, index: str):
        return {'message': self.es.search(index=index)}

    def get_phrase_count(self, index: str, sentence: str):
        query = SENTENCE_QUERY
        query['query']['multi_match']['query'] = sentence
        resp = self.es.search(index=index, body=query)['hits']['hits']
        words = [w for w in sentence.split(' ')]
        arr = []
        for doc in resp:
            if 'highlight' in doc.keys():
                if 'headings' in doc['highlight'].keys():
                    for h in doc['highlight']['headings']:
                        arr.append(h) if f"<em>{words[0]}</em> <em>{words[1]}</em>" in h else None
                if 'text' in doc['highlight'].keys():
                    for t in doc['highlight']['text']:
                        arr.append(t) if f"<em>{words[0]}</em> <em>{words[1]}</em>" in t else None
        return len(arr)

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
        return {'suggestions': [suggest['key'] for suggest in buckets[:8]]}
