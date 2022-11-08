from components.modelating import Modelator
from fastapi import FastAPI
from components.management import Management
from pydantic import BaseModel

app = FastAPI()
elastic = Management()
modelator = Modelator()


class SuggestRequest(BaseModel):
    whole_search: str
    last_word: str


@app.get("/")
async def root():
    return elastic.root()


@app.post("/suggest")
async def suggest(request_body: SuggestRequest):
    return elastic.suggest(request_body.last_word)


@app.get("/import")
async def import_initial():
    return elastic.initial_import()


@app.post("/import/{index}")
async def importing(index: str):
    return elastic.import_texts_from_html(index)


@app.post("/create/{index}")
async def creating(index: str):
    mapping = {}
    return elastic.create_index(index, mapping)


@app.delete("/delete/{index}")
async def deleting(index: str):
    return elastic.delete_index(index)


@app.get("/show/{index}")
async def show(index: str):
    return elastic.show_index(index)


@app.get("/show_data/{index}")
async def show(index: str):
    return elastic.get_index_data(index)


@app.get("/run_algorithm")
async def show_data():
    return modelator.initial_setup()


@app.get("/clean")
async def clean_elastic():
    return elastic.clean()


@app.get("/test")
async def test():
    return elastic.delete_index('words_pairs')
