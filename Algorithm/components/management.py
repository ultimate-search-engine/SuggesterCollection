from decouple import config
import time
from components.dbconnection import DBConnection
from elasticsearch import Elasticsearch
from components.features.text_editor import TextEditor
from components.features.helper import Helper
import components.features.constants as constants
import json
from components.features.multiprocessor import Multiprocess

ENV = config('ENVIRONMENT')
DEFAULT_HOST = config('ES_HOST')
DEFAULT_PORT = int(config('ES_PORT'))
DEFAULT_SCHEME = 'index'
SENTENCE_QUERY = constants.sentence_query
SEARCH_QUERY = constants.search_query
SUGGEST_BASIC_QUERY = constants.suggest_basic_query
SUGGEST_AUTOCOMPLETE_QUERY = constants.suggest_autocomplete_query
SUGGEST_NEXT_QUERY = constants.suggest_next_query
FIELDS = constants.FIELDS


def multi_import(body: any):
    Elasticsearch([{"host": DEFAULT_HOST, "port": DEFAULT_PORT, "scheme": DEFAULT_SCHEME}]).index(
        index=constants.CLEAN_TEXTS, body=body['_source'])


class Management:
    host = ""
    port = None
    scheme = ""
    es = None
    text_editor = TextEditor()
    helper = Helper()
    db = DBConnection()

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

    def initial_import(self, maximum: int = 300000):
        documents = []
        if ENV == 'dev':
            file = open('./data/sites.json', 'r')
            json_data = json.load(file)
            for data in json_data:
                self.es.index(index=constants.SOURCE_TEXTS, body=data)
            while True:
                length = int(self.show_index(constants.SOURCE_TEXTS).get('hits').get('total').get('value'))
                if length == len(json_data):
                    break
                print(f'Loaded {length} records of {len(json_data)}')
                time.sleep(10)
            documents = self.helper.get_all_documents(es=self, index=constants.SOURCE_TEXTS)
        elif ENV == 'dev_db':
            collections = self.db.get_collection_names()
            for collection in collections:
                documents.extend(self.db.get_collection_data(collection, FIELDS))
                if len(documents) > maximum:
                    break
        else:
            documents = [doc for doc in self.helper.get_all_documents(self, 'ency', maximum)]
            multi_docs = self.helper.prepare_list_for_multiprocessing(constants.NUMBER_OF_PROCESSES, documents)
            for hit in multi_docs:
                done = Multiprocess(len(hit), multi_import, hit).run()
                if len(done) == len(hit):
                    print("Imported")
            return len(documents)
        return len(self.import_texts_from_html(documents))

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

    def put_alias(self, index: str, alias: str):
        return self.es.indices.put_alias(index=index, name=alias)

    def get_words_occurrences(self, index: str):
        ids = [document['_id'] for document in self.helper.get_all_documents(es=self, index=index)]
        print(f'Documents: {len(ids)}')
        position_now = 0
        words_stats = []
        print('Getting vectors...')
        while position_now < len(ids):
            position_old = position_now
            position_now = (position_now + (
                100 if len(ids) - position_now > 100 else
                len(ids) - position_now)) if len(ids) > 100 else len(ids)
            words_stats.extend(self.es.mtermvectors(index=index, fields=constants.ALL_FIELDS,
                                                    term_statistics=True,
                                                    ids=ids[position_old:position_now])[
                                   'docs'])
            print(f'Got {position_now} vectors statistic')
        return words_stats

    def import_texts_from_html(self, documents: list):
        processed = 0
        documents_list = []
        hits = []
        while processed < len(documents):
            for i in range(6):
                documents_list.append(
                    documents[processed:min(processed + 1000, len(documents))])
                processed += 1000
            for done in Multiprocess(6, self.text_editor.html_to_text, documents_list).run():
                hits.extend(done)
            documents_list = []
        for hit in hits:
            self.es.index(index=constants.CLEAN_TEXTS, body=hit)
        return hits

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
        sort = [{}]
        sort.extend({"ranks.pagerank": {"order": "desc"}}) if index == 'ency' else None
        return self.es.search(index=index, size=size, from_=from_doc,
                              body={"sort": sort, "query": {"match_all": {}}}).get(
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

    def clean(self):
        indices = self.root()['indices']
        for index in indices:
            if (index == constants.DEFAULT_INDEX in index) or (constants.WORDS_PAIRS in index):
                continue
            else:
                self.delete_index(index)
        return {'message': 'Všechny indexy byly odstraněny.'}
