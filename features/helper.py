class Helper:
    def get_probability(self, occurrences: int, word_count: int):
        return round(occurrences / word_count, 4)

    def words_pairs_model(self, before: str, word: str, probability: float):
        return {
            'before': before,
            'word': word,
            'probability': probability
        }

    def clear_texts_model(self, headings: list, text: str):
        return {
            'headings': headings,
            'text': text
        }

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
