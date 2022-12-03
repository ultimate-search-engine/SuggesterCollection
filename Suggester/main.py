from fastapi import FastAPI
from components.management import Management
from pydantic import BaseModel

app = FastAPI()
elastic = Management()


class SuggestRequest(BaseModel):
    whole_search: str
    last_word: str


@app.get("/")
async def root():
    return elastic.root()


@app.post("/suggest")
async def suggest(request_body: SuggestRequest):
    return elastic.suggest(request_body.last_word)


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

@app.get("/clean")
async def clean_elastic():
    return elastic.clean()