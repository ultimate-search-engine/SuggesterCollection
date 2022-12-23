from decouple import config

DEFAULT_INDEX = 'ency'
SOURCE_TEXTS = 'sites' if 'prod' not in config('ENVIRONMENT') else DEFAULT_INDEX
CLEAN_TEXTS = 'texts'
TEXTS_FOR_CALCULATION = 'text_for_calc'
WORDS_PAIRS = 'words_pairs'
FIELDS = ['finalUrl', 'content']
ALL_FIELDS = ['headings.h1', 'headings.h2', 'headings.h3', 'headings.h4',
              'headings.h5', 'headings.h6', 'title', 'text',
              'description',
              'keywords', 'anchors', 'boldText']

text_mapping = {
    "settings": {
        "number_of_shards": 4
    },
    "mappings": {
        'properties': {
            'content': {
                "type": "nested",
                #     'title': {
                #         'type': 'text',
                #         "analyzer": "english",
                #
                #         "fielddata": True,
                #         "term_vector": "with_positions_offsets"
                #     },
                #     'description': {
                #         'type': 'text',
                #         "analyzer": "english",
                #
                #         "fielddata": True,
                #         "term_vector": "with_positions_offsets"
                #     },
                #     'keywords': {
                #         'type': 'text',
                #         "analyzer": "english",
                #
                #         "fielddata": True,
                #         "term_vector": "with_positions_offsets"
                #     },
                #     'anchors': {
                #         'type': 'text',
                #         "analyzer": "english",
                #
                #         "fielddata": True,
                #         "term_vector": "with_positions_offsets"
                #     },
                #     'boldText': {
                #         'type': 'text',
                #         "analyzer": "english",
                #
                #         "fielddata": True,
                #         "term_vector": "with_positions_offsets"
                #     },
                #     'text': {
                #         'type': 'text',
                #         "analyzer": "english",
                #
                #         "fielddata": True,
                #         "term_vector": "with_positions_offsets"
                #     },
                #     'headings': {
                #         'h1': {
                #             'type': 'text',
                #             "analyzer": "english",
                #
                #             "fielddata": True,
                #             "term_vector": "with_positions_offsets"
                #         },
                #         'h2': {
                #             'type': 'text',
                #             "analyzer": "english",
                #
                #             "fielddata": True,
                #             "term_vector": "with_positions_offsets"
                #         },
                #         'h3': {
                #             'type': 'text',
                #             "analyzer": "english",
                #
                #             "fielddata": True,
                #             "term_vector": "with_positions_offsets"
                #         },
                #         'h4': {
                #             'type': 'text',
                #             "analyzer": "english",
                #
                #             "fielddata": True,
                #             "term_vector": "with_positions_offsets"
                #         },
                #         'h5': {
                #             'type': 'text',
                #             "analyzer": "english",
                #
                #             "fielddata": True,
                #             "term_vector": "with_positions_offsets"
                #         },
                #         'h6': {
                #             'type': 'text',
                #             "analyzer": "english",
                #
                #             "fielddata": True,
                #             "term_vector": "with_positions_offsets"
                #         }
                #     }
            }
        }
    }
}
words_pairs_mapping = {
    "settings": {
        "number_of_shards": 4
    },
    "mappings": {
        'properties': {
            'word': {
                'type': 'keyword',
            },
            'before': {
                'type': 'keyword'
            },
            'probability': {
                'type': 'float'
            }
        }
    }
}
suggest_basic_query = {
    "size": 0,
    "aggregations": {
        "autocomplete": {
            "filter": {
                "prefix": {
                    "autocomplete": ""
                }
            },
            "aggregations": {
                "autocomplete": {
                    "terms": {
                        "field": "autocomplete",
                        "include": ""
                    }
                }
            }
        }
    }
}
suggest_next_query = {
    "size": 6,
    "query": {
        "term": {
            "before": ""
        }
    },
    "sort": {
        "probability": "desc"
    }
}
suggest_autocomplete_query = {
    "size": 6,
    "query": {
        "multi_match": {
            "query": "",
            "type": "bool_prefix",
            "fields": ["before", "word"]
        }
    },
    "sort": {
        "probability": "desc"
    }
}
search_query = {
    "query": {
        "bool": {
            "must": {
                "query_string": {
                    "query": ""
                }
            }
        }
    }
}
sentence_query = {
    'query': {
        "multi_match": {
            'query': '',
            'fields': ALL_FIELDS
        }
    },
    "highlight": {
        "require_field_match": False,
        "fields": {
            "*": {
                "fragment_size": 50,
                "number_of_fragments": 0
            }
        },
    },
}
