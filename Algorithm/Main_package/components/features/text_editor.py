from bs4 import BeautifulSoup
from components.features.helper import Helper
import re


class TextEditor:
    helper = None

    def __init__(self):
        self.helper = Helper()

    def html_to_text(self, htmls):
        hits = []
        for hit in htmls:
            html = hit.get('_source').get('content') if '_source' in hit.keys() else hit.get('content')
            text = BeautifulSoup(html, features="html.parser").get_text().replace("\n", " ").strip()
            headings = BeautifulSoup(html, features="html.parser").find_all([f'h{i}' for i in range(1, 4)])
            headings_arr = []
            autocomplete = []
            for head in headings:
                if len(head) > 1:
                    for h in head:
                        headings_arr.append(h.get_text().replace("\n", " ").strip()) if len(
                            h.get_text().replace("\n", " ").strip()) > 1 else None
                else:
                    headings_arr.append(head.get_text().replace("\n", " ").strip()) if len(
                        head.get_text().replace("\n", " ").strip()) > 1 else None
            for title in headings_arr:
                autocomplete.extend(title.split())
            autocomplete.extend(text.split())
            hits.append(self.helper.hits_model(headings_arr, text, autocomplete))
        return hits

    def format_and_words(self, source: list):
        words = []
        response = []
        for i in range(0, len(source)):
            sentences = source[i]
            if isinstance(source[i], str):
                better_content = source[i].replace("  ", "~").replace("~ ", ". ").replace("~", "")
                sentences = re.split('\.|\!|\?', better_content)
            if isinstance(source[i], dict):
                data_full = []
                for key in source[i].keys():
                    data = []
                    for sentence in source[i][key]:
                        text = sentence.lower()
                        data.append(self.assign_marks(text))
                        words.extend(self.split_to_words(text))
                    data_full.append({key: data})
                response.append(data_full)
            else:
                data = []
                for sentence in sentences:
                    text = sentence.lower()
                    data.append(self.assign_marks(text))
                    words.extend(self.split_to_words(text))
                response.append(' '.join(data) if isinstance(source[i], str) else data)
        return [response, words]

    def split_to_words(self, text: str):
        word_regex_improved = r"(\w[\w']*\w|\w)"
        word_matcher = re.compile(word_regex_improved)
        return word_matcher.findall(text)

    def assign_marks(self, sentence: str):
        return f' sssss {sentence.strip()} eeeee '

    def search_for_phrase(self, before: str, after: str, resp):
        amount = 0
        for doc in resp:
            if 'highlight' in doc.keys():
                base = doc['highlight']
                for key in base.keys():
                    for item in base[key]:
                        amount += item.count(f"<em>{before}</em> <em>{after}</em>")
                # if 'headings' in doc['highlight'].keys():
                #     for h in doc['highlight']['headings']:
                #         arr.append(h) if f"<em>{before}</em> <em>{after}</em>" in h else None
                # if 'text' in doc['highlight'].keys():
                #     for t in doc['highlight']['text']:
                #         arr.append(t) if f"<em>{before}</em> <em>{after}</em>" in t else None
        return amount

    def find_indices(self, list_to_check: list, item_to_find: any):
        return [idx for idx, value in enumerate(list_to_check) if value == item_to_find]

    def search_for_dependant(self, word: str, resp):
        arr = []
        for doc in resp:
            if 'highlight' in doc.keys():
                base = doc['highlight']
                for key in base.keys():
                    for item in base[key]:
                        words = item.split()
                        if f"<em>{word}</em>" in words:
                            indices = self.find_indices(words, f"<em>{word}</em>")
                            for i in indices:
                               arr.append(words[i + 1]) if (i + 1) < len(words) else None
        return list(set(arr))
