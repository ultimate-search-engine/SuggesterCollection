
# Ultimate Search Engine - Suggester

This is a component for project Ultimate Search Engine. This component can run an algorithm to count 
a probability of the given word and also suggest another word. 




## Installation

Install with docker compose:

```bash
  git clone https://github.com/ultimate-search-engine/suggester.git
  cd suggester
  mv .env.example .env
  docker compose up
```

## Environment Variables

You can change the following environment variables in your .env file

`ES_PORT` - default: 9200

`ES_HOST` - default: localhost



## API Reference

#### Get suggestions

```http
  POST http://localhost:8000/suggest
```

| Parameter | Type     | Description                        |
| :-------- | :------- |:-----------------------------------|
| `whole_search` | `string` | **Required**. Whole search text    |
| `last_word` | `string` | **Required**. Last typed word/text |
#### Response JSON example:
```text
    {
    "autocomplete": 
            ["moreuc", "more1240", "morefeb", "more", "more", "moreapp"],
    "next_words": 
            ["secure", "help", "about", "personal", "energy", "useful"]
    }
```

## Used resources

[Formula for algorithm](https://web.stanford.edu/~jurafsky/slp3/3.pdf)

