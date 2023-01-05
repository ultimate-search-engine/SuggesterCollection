from components.management import Management
from components.features.counter import Counter
from components.features.helper import Helper
from components.features.text_editor import TextEditor
from components.features.multiprocessor import Multiprocess
import components.features.constants as constants
import time
from datetime import datetime

MAIN_INDEX = constants.SOURCE_TEXTS
INDEX = constants.TEXTS_FOR_CALCULATION
INDEX_IMPORT = f'{constants.WORDS_PAIRS}_{datetime.now().strftime("%Y%m%d")}'
MAPPING_TEXT = constants.text_mapping
MAPPING_PAIRS = constants.words_pairs_mapping
COUNTING_AMOUNT = 200


class Modelator:
    manager = Management()
    counter = Counter()
    helper = Helper()
    text_editor = TextEditor()
    index = ''

    def __init__(self, index: str = constants.CLEAN_TEXTS):
        self.index = index

    def initial_setup(self, should_be: int = 30000):
        print('Running algorithm...')
        list_of_data = self.helper.get_all_documents(self.manager, self.index, should_be)
        print('Got data for the algorithm')
        while len(list_of_data) < should_be:
            time.sleep(5)
            list_of_data = self.helper.get_all_documents(self.manager, self.index, should_be)
        self.helper.es_clean(Management(), INDEX, MAPPING_TEXT, INDEX_IMPORT, MAPPING_PAIRS)
        print('Elastic has been cleaned')
        data_for_process = self.helper.list_for_multi(6, list_of_data)
        for data_list in data_for_process:
            results = Multiprocess(len(data_list), self.insert_searchable_texts, data_list).run()
            if len(results) == len(data_list):
                print("Done another list")
            # self.insert_searchable_texts(data_list)
        loaded_docs = self.manager.show_index(INDEX)['hits']['total']['value']
        while loaded_docs < len(list_of_data):
            print(f'Wait! Loaded only {loaded_docs} of {len(list_of_data)} documents!')
            time.sleep(5)
            loaded_docs = self.manager.show_index(INDEX)['hits']['total']['value']
        return self.create_model()

    def insert_searchable_texts(self, data_list: dict):
        manager = Management()
        data = data_list.get('_source').get('content')
        for_format = [data[key] for key in data.keys()]
        structured = self.text_editor.format_and_words(for_format)
        new_index_data = self.helper.clear_texts_model(structured[0], [key for key in data.keys()])
        manager.import_record_to_index(INDEX, new_index_data)
        return None

    # TODO add to Ktolin

    def calculate_words(self):
        docs = self.manager.get_words_occurrences(INDEX)
        print(f'Counting words occurrences in documents started {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}!')
        counted_docs = 0
        words_lists = []
        while counted_docs < (len(docs) - COUNTING_AMOUNT if len(docs) > COUNTING_AMOUNT else len(docs)):
            end = (counted_docs + COUNTING_AMOUNT) if COUNTING_AMOUNT < len(docs) else len(docs)
            words_lists.append(self.counter.count_all_words_in_docs(docs[counted_docs:end]))
            counted_docs = end
            print(f'Counted words in {counted_docs} of {len(docs)} documents')
        print(f'{len(docs) - counted_docs} remaining')
        words_lists.append(self.counter.count_all_words_in_docs(docs[counted_docs:len(docs)]))
        return self.counter.count_all_words(words_lists)

    def create_model(self):
        occurrences = self.calculate_words()
        print(f'Counting words occurrences in documents is done {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}!')
        x = 0
        for field in occurrences:
            self.helper.create_alias(self.manager, constants.WORDS_PAIRS, INDEX_IMPORT) if (x and x < 2) else None
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
            x += 1
            print(f'Word {before} ({x} of {len(occurrences)}) is inserted to database')
        return INDEX_IMPORT
