from components.modelating import Modelator
from fastapi import FastAPI
from components.management import Management

app = FastAPI()
elastic = Management()
modelator = Modelator()


@app.get("/")
async def root():
    return elastic.root()


@app.get("/suggest/{value}")
async def suggest(value: str):
    return elastic.suggest(value)


@app.get("/import")
async def import_initial():
    return elastic.initial_import()


@app.get("/import/{index}")
async def importing(index: str):
    return elastic.index_default_import(index)


@app.get("/create/{index}")
async def creating(index: str):
    mapping = {}
    return elastic.create_index(index, mapping)


@app.get("/delete/{index}")
async def deleting(index: str):
    return elastic.delete_index(index)


@app.get("/show/{index}")
async def show(index: str):
    return elastic.show_index(index)


@app.get("/run_algorithm")
async def show_data():
    return elastic.get_sentence('social impact')
    # return modelator.initial_setup()
    # te = TextEditor()
    # te.show(data['headings'], data['text'])
    # return data
