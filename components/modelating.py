from components.management import Management
from features.counter import Counter
from features.helper import Helper
from features.text_editor import TextEditor
import features.constatnts as constants
import time

MAIN_INDEX = 'sites'
INDEX = 'text_for_calc'
INDEX_IMPORT = 'words_pairs'
MAPPING_TEXT = constants.text_mapping
MAPPING_PAIRS = constants.words_pairs_mapping


class Modelator:
    manager = Management()
    counter = Counter()
    helper = Helper()
    text_editor = TextEditor()
    index = ''

    def __init__(self, index: str = 'texts'):
        self.index = index

    def initial_setup(self):
        print('Running algorithm...')
        should_be = int(self.manager.show_index(MAIN_INDEX).get('hits').get('total').get('value'))
        list_of_data = self.helper.get_all_documents(self.manager, self.index)
        print('Got data for the algorithm')
        while len(list_of_data) < should_be:
            time.sleep(5)
            list_of_data = self.helper.get_all_documents(self.manager, self.index)
        self.helper.es_clean(Management(), INDEX, MAPPING_TEXT, INDEX_IMPORT, MAPPING_PAIRS)
        print('Elastic has been cleaned')
        for data_list in list_of_data:
            self.insert_searchable_texts(data_list)
        while self.manager.show_index(INDEX)['hits']['total']['value'] < len(list_of_data):
            print(f'Wait! Should be {len(list_of_data)} documents.')
            time.sleep(5)
        return self.create_model()

    def insert_searchable_texts(self, data_list: dict):
        data = data_list.get('_source')
        structured = self.text_editor.format_and_words(data['headings'], data['text'])
        new_index_data = self.helper.clear_texts_model(structured[0], structured[1])
        self.manager.import_record_to_index(INDEX, new_index_data)
        return structured[2]

    def calculate_words(self):
        docs = self.manager.get_words_occurrences(INDEX)
        return self.counter.count_all_words(docs)

    def create_model(self):
        occurrences = self.calculate_words()
        for field in occurrences:
            before = field['word']
            found = 0
            for occurrence in occurrences:
                word = occurrence['word']
                probability = self.helper.get_probability(self.manager.get_phrase_count(
                    INDEX, f"{before} {word}"), field['count'])
                if probability > 0:
                    found += 1
                    data_to_import = self.helper.words_pairs_model(before, word, probability)
                    self.manager.import_record_to_index(INDEX_IMPORT, data_to_import)
                    print(data_to_import, {'phrase': self.manager.get_phrase_count(
                        INDEX, f"{before} {word}"), 'word': field['count']})
                    if found == int(field['count']):
                        break
            print(f'Word {before} is inserted to database')
        return self.manager.show_index(INDEX_IMPORT)


