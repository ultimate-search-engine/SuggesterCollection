import time

from elasticsearch import Elasticsearch
from features.text_editor import TextEditor
from features.helper import Helper
import features.constatnts as constants
import json
import sys

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9200
DEFAULT_SCHEME = 'docker_cluster'
SENTENCE_QUERY = constants.sentence_query
SEARCH_QUERY = constants.search_query
SUGGEST_BASIC_QUERY = constants.suggest_basic_query
SUGGEST_AUTOCOMPLETE_QUERY = constants.suggest_autocomplete_query
SUGGEST_NEXT_QUERY = constants.suggest_next_query
ARG_HOST = None if len(sys.argv) < 2 else sys.argv[1]
ARG_PORT = None if len(sys.argv) < 3 else sys.argv[2]


class Management:
    host = ""
    port = None
    scheme = ""
    es = None
    text_editor = TextEditor()
    helper = Helper()

    def __init__(self, host: str = ARG_HOST if ARG_HOST else DEFAULT_HOST,
                 port: int = ARG_PORT if ARG_PORT else DEFAULT_PORT, scheme: str = DEFAULT_SCHEME):
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
        while True:
            length = int(self.show_index('sites').get('hits').get('total').get('value'))
            if length == len(json_data):
                break
            print(f'Loaded {length} records of {len(json_data)}')
            time.sleep(10)
        return len(self.import_texts_from_html('sites'))

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
        search_query = SEARCH_QUERY
        search_query['query']['bool']['must']['query_string']['query'] = text
        return self.es.search(index=index, query=search_query)

    def get_words_occurrences(self, index: str):
        ids = [document['_id'] for document in self.helper.get_all_documents(es=self, index=index)]
        print(f'Documents: {len(ids)}')
        position_now = 0
        words_stats = []
        print('Getting vectors...')
        while position_now < len(ids):
            words_stats.extend(self.es.mtermvectors(index=index, fields=['headings', 'text'],
                                                    term_statistics=True,
                                                    ids=ids[position_now:position_now + (
                                                        100 if len(ids) - position_now > 100 else
                                                        len(ids) - position_now)])['docs'])
            position_now += (100 if len(ids) - position_now > 100 else
                             len(ids) - position_now)
            print(f'Got {position_now} vectors statistic')
        return words_stats

    def import_texts_from_html(self, index: str):
        hits = self.text_editor.html_to_text(self.helper.get_all_documents(es=self, index=index))
        for hit in hits:
            print(self.es.index(index="texts", body=hit)['_id'] + ' document created')
        return hits

    def delete_index(self, index: str):
        return {"message": self.es.options(ignore_status=[400, 404]).indices.delete(index=index)}

    def create_index(self, index: str, mappings: object):
        return {"message": self.es.indices.create(index=index, body=mappings, pretty=True)}

    def get_index_data(self, index: str, size: int = 100, from_doc: int = 0):
        return self.es.search(index=index, size=size, from_=from_doc, body={"query": {"match_all": {}}}).get(
            'hits').get('hits')

    def show_index(self, index: str):
        return self.es.search(index=index)

    def get_phrase_count(self, index: str, sentence: str):
        query = SENTENCE_QUERY
        query['query']['multi_match']['query'] = sentence
        resp = self.es.search(index=index, body=query)['hits']['hits']
        words = [w for w in sentence.split(' ')]
        return (self.text_editor.search_for_phrase(words[0], words[1], resp) if len(
            words) > 1 else self.text_editor.search_for_dependant(words[0], resp))

    def suggest(self, value: str):
        query_complete = SUGGEST_AUTOCOMPLETE_QUERY
        query_next = SUGGEST_NEXT_QUERY
        query_next['query']['term']['before'] = value.lower()
        query_complete['query']['multi_match']['query'] = value
        next_docs = self.es.search(index='words_pairs', body=query_next)['hits']['hits']
        next_words = [doc['_source']['word'] for doc in next_docs]
        autocomplete_docs = self.es.search(index='words_pairs', body=query_complete)['hits']['hits']
        autocomplete_words = [word['_source']['before' if value in word['_source']['before'] else 'word'] for word in
                              autocomplete_docs]
        return {
            'autocomplete': autocomplete_words,
            'next_words': next_words
        }

    def clean(self):
        indices = self.root()['indices']
        for index in indices:
            self.delete_index(index)
        return {'message': 'Všechny indexy byly odstraněny.'}
