from decouple import config
from elasticsearch import Elasticsearch
import components.features.constants as constants

DEFAULT_HOST = config('ES_HOST')
DEFAULT_PORT = int(config('ES_PORT'))
DEFAULT_SCHEME = 'index'
SENTENCE_QUERY = constants.sentence_query
SEARCH_QUERY = constants.search_query
SUGGEST_BASIC_QUERY = constants.suggest_basic_query
SUGGEST_AUTOCOMPLETE_QUERY = constants.suggest_autocomplete_query
SUGGEST_NEXT_QUERY = constants.suggest_next_query
FIELDS = constants.FIELDS
MAX_FIELDS = 30000


class Management:
    host = ""
    port = None
    scheme = ""
    es = None

    def __init__(self,
                 host: str = DEFAULT_HOST,
                 port: int = DEFAULT_PORT,
                 scheme: str = DEFAULT_SCHEME):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.es = Elasticsearch([{"host": host, "port": port, "scheme": scheme}])

    def root(self):
        indices = self.es.indices.get_alias()
        indices = [index_name for index_name, value in indices.items()]
        return {"message": self.es.info(),
                'indices': indices}

    def delete_index(self, index: str):
        by_alias = None
        if index == constants.WORDS_PAIRS:
            if self.es.indices.exists_alias(name=index):
                by_alias = list(self.es.indices.get(index=index).keys())[0]
        return {
            "message": self.es.options(ignore_status=[400, 404]).indices.delete(index=by_alias or index)}

    def create_index(self, index: str, mappings: object):
        return {"message": self.es.indices.create(index=index, body=mappings, pretty=True)}

    def get_index_data(self, index: str, size: int = 100, from_doc: int = 0):
        return self.es.search(index=index, size=size, from_=from_doc, body={"query": {"match_all": {}}}).get(
            'hits').get('hits')

    def show_index(self, index: str):
        return self.es.search(index=index)

    def suggest(self, value: str):
        query_complete = SUGGEST_AUTOCOMPLETE_QUERY
        query_next = SUGGEST_NEXT_QUERY
        query_next['query']['term']['before'] = value.lower()
        query_complete['query']['multi_match']['query'] = value
        next_docs = self.es.search(index=constants.WORDS_PAIRS, body=query_next)['hits']['hits']
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
            if constants.WORDS_PAIRS not in index:
                self.delete_index(index)
        return {'message': 'Všechny indexy byly odstraněny.'}
