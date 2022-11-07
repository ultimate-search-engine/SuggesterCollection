from components.management import Management
from features.counter import Counter
from features.helper import Helper
from features.text_editor import TextEditor
import features.constatnts as constants
import time
from datetime import datetime

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
        loaded_docs = self.manager.show_index(INDEX)['hits']['total']['value']
        while loaded_docs < len(list_of_data):
            print(f'Wait! Loaded only {loaded_docs} of {len(list_of_data)} documents!')
            time.sleep(5)
            loaded_docs = self.manager.show_index(INDEX)['hits']['total']['value']
        return self.create_model()

    def insert_searchable_texts(self, data_list: dict):
        data = data_list.get('_source')
        structured = self.text_editor.format_and_words(data['headings'], data['text'])
        new_index_data = self.helper.clear_texts_model(structured[0], structured[1])
        self.manager.import_record_to_index(INDEX, new_index_data)
        return structured[2]

    def calculate_words(self):
        docs = self.manager.get_words_occurrences(INDEX)
        print(f'Counting words occurrences in documents started {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}!')
        counted_docs = 0
        words_lists = []
        while counted_docs < (len(docs) - 250):
            words_lists.append(self.counter.count_all_words_in_docs(docs[counted_docs:counted_docs + 250]))
            counted_docs += 250
            print(f'Counted words in {counted_docs} of {len(docs)} documents')
        remaining = len(docs) - counted_docs
        print(f'{remaining} remaining')
        words_lists.append(self.counter.count_all_words_in_docs(docs[counted_docs:len(docs)]))
        return self.counter.count_all_words(words_lists)

    def create_model(self):
        occurrences = self.calculate_words()
        print(f'Counting words occurrences in documents is done {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}!')
        x = 0
        for field in occurrences:
            before = field['word']
            found = 0
            dependant_words = self.manager.get_phrase_count(INDEX, before)
            for word in dependant_words:
                probability = self.helper.get_probability(self.manager.get_phrase_count(
                    INDEX, f"{before} {word}"), field['count'])
                if (probability > 0) and (probability < 1.01):
                    found += 1
                    data_to_import = self.helper.words_pairs_model(before, word if word != 'eeeee' else '.',
                                                                   probability)
                    self.manager.import_record_to_index(INDEX_IMPORT, data_to_import)
                    print(data_to_import)
                    if found == int(field['count']):
                        break
            print(f'Word {before} ({x} of {len(occurrences)}) is inserted to database')
        return self.manager.show_index(INDEX_IMPORT)
