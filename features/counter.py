class Counter:
    def count_all_words(self, docs: list):
        print('Counting words occurrences in documents started!')
        list_of_words = []
        position = 1
        for doc in docs:
            term_vectors = doc['term_vectors']
            headings = term_vectors['headings']['terms'] if 'headings' in term_vectors else {}
            text = term_vectors['text']['terms'] if 'text' in term_vectors else {}
            all_words = {**headings, **text}
            for key, value in all_words.items():
                existed = [x for x in list_of_words if x['word'] == key]
                insert_val = {'word': key, 'count': value['term_freq'] + (existed[0]['count'] if len(existed) else 0)}
                if len(existed):
                    list_of_words.remove(existed[0])
                list_of_words.append(insert_val)
            print(f'{position} document of {len(docs)} is counted!')
            position += 1
        return list_of_words