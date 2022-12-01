class Counter:
    def count_all_words_in_docs(self, docs: list):
        list_of_words = []
        position = 1
        for doc in docs:
            all_words = {}
            term_vectors = doc['term_vectors']
            all_words.update(term_vectors[key]['terms'] for key in term_vectors.keys())
            for key, value in all_words.items():
                existed = [x for x in list_of_words if x['word'] == key]
                insert_val = {'word': key, 'count': value['term_freq'] + (existed[0]['count'] if existed else 0)}
                if existed:
                    list_of_words.remove(existed[0])
                list_of_words.append(insert_val)
            print(f'{position} document/s of {len(docs)} are counted!')
            position += 1
        return list_of_words

    def count_all_words(self, word_lists: list):
        counted_words = word_lists[0]
        list_now = 1
        for words in word_lists:
            if list_now == 1:
                print(f'{list_now}. list/s of {len(word_lists)} is counted!')
                list_now += 1
                continue
            for word in words:
                existed = [x for x in counted_words if x['word'] == word['word']]
                insert_val = {'word': word['word'],
                              'count': word['count'] + (existed[0]['count'] if existed else 0)}
                if existed:
                    counted_words.remove(existed[0])
                counted_words.append(insert_val)
            print(f'{list_now}. list/s of {len(word_lists)} is counted!')
            list_now += 1
        return counted_words
