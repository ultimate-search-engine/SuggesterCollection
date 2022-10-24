class Counter:
    def count_all_words(self, docs: list):
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