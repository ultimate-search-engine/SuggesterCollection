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

    def es_clean(self, es, texts_index: str, text_mapping: object, words_pairs_index: str, words_pairs_mapping: object):
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

    def list_for_multi(self, proc_amount: int, original_list: list):
        inserted = 0
        new_list = []
        while inserted < len(original_list):
            if (len(original_list) - inserted) >= proc_amount:
                new_list.append(original_list[inserted:inserted + proc_amount])
                inserted += proc_amount
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
