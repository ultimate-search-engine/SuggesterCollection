from bs4 import BeautifulSoup
import re


class TextEditor:
    def __init__(self):
        pass

    def html_to_text(self, htmls):
        hits = []
        for hit in htmls:
            html = hit.get('_source').get('content')
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
            print(len(autocomplete))
            hits.append({
                "headings": headings_arr,
                "text": text,
                'autocomplete': autocomplete
            })
        return hits

    def format_and_words(self, headings: list, content: str):
        words = []
        new_headings = []
        new_sentences = []
        better_content = content.replace("  ", "~").replace("~ ", ". ").replace("~", "")
        sentences = re.split('\.|\!|\?', better_content)
        for head in headings:
            text = head.lower()
            new_headings.append(self.assign_marks(text))
            words.extend(self.split_to_words(text))
        for sentence in sentences:
            text = sentence.lower()
            new_sentences.append(self.assign_marks(text))
            words.extend(self.split_to_words(text))
        new_content = ' '.join(new_sentences)
        return [new_headings, new_content, words]

    def split_to_words(self, text: str):
        word_regex_improved = r"(\w[\w']*\w|\w)"
        word_matcher = re.compile(word_regex_improved)
        return word_matcher.findall(text)

    def assign_marks(self, sentence: str):
        return f' sssss {sentence.strip()} eeeee '
