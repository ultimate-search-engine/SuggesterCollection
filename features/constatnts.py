text_mapping = {
    "settings": {
        "number_of_shards": 4
    },
    "mappings": {
        'properties': {
            'headings': {
                'type': 'text',
                "analyzer": "english",

                "fielddata": True,
                "term_vector": "with_positions_offsets"
            },
            'text': {
                'type': 'text',
                "analyzer": "english",

                "fielddata": True,
                "term_vector": "with_positions_offsets"
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
suggest_query = {
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
            'fields': ['headings', 'text']
        }
    },
    "highlight": {
        "fields": {
            "*": {}
        },
        "type": "fvh",
        "fragment_size": 20,
        "number_of_fragments": 100
    }
}
