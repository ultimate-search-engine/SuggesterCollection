from components.management import Management
import time

INDEX = 'text_for_calc'
INDEX_IMPORT = 'words_pairs'
MAPPING_TEXT = {
    "settings": {
        "number_of_shards": 4
    },
    "mappings": {
        'properties': {
            'headings': {
                'type': 'text',
                "analyzer": "english",

                "fielddata": True,
                "term_vector": "yes"
            },
            'text': {
                'type': 'text',
                "analyzer": "english",

                "fielddata": True,
                "term_vector": "yes"
            }
        }
    }}
MAPPING_PAIRS = {
    "settings": {
        "number_of_shards": 4
    },
    "mappings": {
        'properties': {
            'word': {
                'type': 'keyword',
            },
            'before': {
                'type': 'keyword'
            },
            'probability': {
                'type': 'float'
            }
        }
    }}


class Modelator:
    manager = Management()
    index = ''

    def __init__(self, index: str = 'texts'):
        self.index = index

    def initial_setup(self):
        list_of_data = self.manager.get_index_data(self.index)
        words = []
        self.manager.delete_index('text_for_calc')
        self.manager.create_index('text_for_calc', MAPPING_TEXT)
        self.manager.delete_index('words_pairs')
        self.manager.create_index('words_pairs', MAPPING_PAIRS)
        for data_list in list_of_data:
            words.extend(self.insert_searchable_texts(data_list))
        words = list(dict.fromkeys(words))
        time.sleep(5)
        return self.create_model(words)

    def insert_searchable_texts(self, data_list):
        data = data_list.get('_source')
        structured = self.manager.text_editor.format_and_words(data['headings'], data['text'])
        new_index_data = {
            'headings': structured[0],
            'text': structured[1]
        }
        self.manager.import_record_to_index('text_for_calc', new_index_data)
        return structured[2]

    def sum_all_words(self, docs: list):
        list_of_words = []
        for doc in docs:
            term_vectors = doc['term_vectors']
            all_words = {**term_vectors['text']['terms'], **term_vectors['headings']['terms']}
            for key, value in all_words.items():
                existed = [x for x in list_of_words if x['word'] == key]
                insert_val = {'word': key, 'count': value['term_freq'] + (existed[0]['count'] if len(existed) else 0)}
                if len(existed):
                    list_of_words.remove(existed[0])
                list_of_words.append(insert_val)
        return list_of_words

    def calculate_words(self):
        docs = self.manager.count_occurrences(INDEX)['docs']
        return self.sum_all_words(docs)

    def create_model(self, words: list):
        occurrences = self.calculate_words()
        return occurrences
        #     occurrences.append({'word': word, 'count': self.manager.count_occurrences(INDEX, word)})
        # occurrences.append({'word': '<s>', 'count': self.manager.count_occurrences(INDEX, '<s>')})
        # print(occurrences)
        # for word in words:
        #     for occurrence in occurrences:
        #         if occurrence['count'] and (occurrence['word'].strip != word.strip):
        #             data_to_import = {
        #                 'before': word,
        #                 'word': occurrence['word'],
        #                 'probability': round(
        #                     self.manager.count_occurrences(
        #                         INDEX, f"{occurrence['word']} {word}") / occurrence['count'], 4)
        #             }
        #             self.manager.import_record_to_index(INDEX_IMPORT, data_to_import)
        #             for_check.append(data_to_import)
        #             print(data_to_import)
        # print(for_check)
