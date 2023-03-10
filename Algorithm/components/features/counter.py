from components.features.helper import Helper
import components.features.constants as constants
from components.features.multiprocessor import Multiprocess


class Counter:
    helper = Helper()

    def count_words(self, documents: list):
        raw_documents_bundles_for_multiprocessing = self.helper.prepare_bundles_for_multiprocessing(constants.NUMBER_OF_PROCESSES, documents)
        counted_raw_documents = Multiprocess(constants.NUMBER_OF_PROCESSES, self.count_words_occurences_in_raw_documents,
                         raw_documents_bundles_for_multiprocessing).run()
        processed_documents = counted_raw_documents
        while len(processed_documents) > 1:
            processed_documents = self.helper.prepare_mixes_bundles(processed_documents)
            after_processing = Multiprocess(len(processed_documents), self.count_processed_words_occurrences,
                             processed_documents).run()
            processed_documents = after_processing
        return processed_documents[0]

        # counted_documents = 0
        # words_lists = []
        # while counted_documents < (len(documents) - COUNTING_AMOUNT if len(documents) > COUNTING_AMOUNT else len(documents)):
        #     end = (counted_documents + COUNTING_AMOUNT) if COUNTING_AMOUNT < len(documents) else len(documents)
        #     words_lists.append(self.count_words_occurences_in_raw_documents(documents[counted_documents:end]))
        #     counted_documents = end
        #     print(f'Counted words in {counted_documents} of {len(documents)} documents')
        # print(f'{len(documents) - counted_documents} remaining')
        # words_lists.append(self.count_words_occurences_in_raw_documents(documents[counted_documents:len(documents)]))

    def count_processed_words_occurrences(self, documents: list):
        list_of_words = []
        for document in documents:
            existed = [x for x in list_of_words if x['word'] == document['word']]
            insert_val = {'word': document['word'], 'count': document['count'] + (existed[0]['count'] if existed else 0)}
            if existed:
                list_of_words.remove(existed[0])
            list_of_words.append(insert_val)
        print(f'Updated word {document["word"]}')
        return list_of_words

    def count_words_occurences_in_raw_documents(self, documents: list):
        list_of_words = []
        for document in documents:
            all_words = {}
            term_vectors = document['term_vectors']
            for key in term_vectors.keys():
                all_words.update(term_vectors[key]['terms'])
            for key, value in all_words.items():
                existed = [x for x in list_of_words if x['word'] == key]
                insert_val = {'word': key, 'count': value['term_freq'] + (existed[0]['count'] if existed else 0)}
                if existed:
                    list_of_words.remove(existed[0])
                list_of_words.append(insert_val)
            print(f'Processed document {document["_id"]}')
        return list_of_words

    # def count_all_words(self, word_lists: list):
    #     counted_words = word_lists[0]
    #     list_now = 1
    #     for words in word_lists:
    #         if list_now == 1:
    #             print(f'{list_now}. list/s of {len(word_lists)} is counted!')
    #             list_now += 1
    #             continue
    #         for word in words:
    #             existed = [x for x in counted_words if x['word'] == word['word']]
    #             insert_val = {'word': word['word'],
    #                           'count': word['count'] + (existed[0]['count'] if existed else 0)}
    #             if existed:
    #                 counted_words.remove(existed[0])
    #             counted_words.append(insert_val)
    #         print(f'{list_now}. list/s of {len(word_lists)} is counted!')
    #         list_now += 1
    #     return counted_words
