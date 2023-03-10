import math
from time import sleep

SIZE = 100


class Helper:
    def get_probability(self, occurrences: int, word_count: int):
        return round(occurrences / word_count, 4)

    def words_pairs_model(self, before: str, word: str, probability: float):
        return {
            'before': before,
            'word': word,
            'probability': probability
        }

    def clear_texts_model(self, data, keys):
        return {keys[i]: data[i] for i in range(len(keys))}

    def clean_elasticsearch(self, es, texts_index: str, text_mapping: object, words_pairs_index: str, words_pairs_mapping: object):
        es.delete_index(texts_index)
        es.create_index(texts_index, text_mapping)
        es.delete_index(words_pairs_index)
        es.create_index(words_pairs_index, words_pairs_mapping)
        return True

    def hits_model(self, headings: list, text: str, autocomplete: list):
        return {
            "headings": headings,
            "text": text,
            'autocomplete': autocomplete
        }

    def prepare_mixes_bundles(self, bundles: list):
        if len(bundles) == 2:
            return [bundles[0] + bundles[1]]
        mixes = []
        for i in range(0, len(bundles), 2):
            mixes.append(bundles[i] + bundles[i + 1])
        if len(bundles) % 2 != 0:
            mixes.append(bundles[-1])
        return mixes
    def prepare_bundles_for_multiprocessing(self, process_amount: int, original_list: list):
        quantity_of_documents = math.ceil(len(original_list)/process_amount)
        list_of_bundles = []
        for i in range(process_amount - 1):
            list_of_bundles.append(original_list[i*quantity_of_documents:(i+1)*quantity_of_documents])
        list_of_bundles.append(original_list[(process_amount - 1)*quantity_of_documents:])
        return list_of_bundles

    def prepare_list_for_multiprocessing(self, process_amount: int, original_list: list):
        inserted = 0
        new_list = []
        while inserted < len(original_list):
            if (len(original_list) - inserted) >= process_amount:
                new_list.append(original_list[inserted:inserted + process_amount])
                inserted += process_amount
            else:
                new_list.append(original_list[inserted:])
                inserted = len(original_list)
        return new_list

    def get_all_documents(self, es, index: str, maximum: int = 30000):
        size = es.show_index(index)['hits']['total']['value']
        documents = es.get_index_data(index, SIZE, 0)
        while len(documents) < (size if size < maximum else maximum):
            sleep(5)
            documents.extend(es.get_index_data(index, SIZE, len(documents)))
        return documents

    def create_alias(self, es, alias: str, index: str):
        return es.put_alias(index, alias)

    def delete_indices(self, es, indices: list):
        for index in indices:
            es.delete_index(index)
        return True
