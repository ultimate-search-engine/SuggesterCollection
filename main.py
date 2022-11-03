from components.modelating import Modelator
from fastapi import FastAPI
from components.management import Management
from datetime import datetime

app = FastAPI()
elastic = Management()
modelator = Modelator()


@app.get("/")
async def root():
    return elastic.root()


@app.get("/suggest/{value}")
async def suggest(value: str):
    return elastic.suggest(value)


@app.get("/run_full_setup")
async def full_setup():
    print('Full setup started!')
    elastic.clean()
    hits = elastic.initial_import()
    print(f'Dump imported - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    modelator.initial_setup()
    print(f'Model created - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    elastic.delete_index('texts')
    elastic.delete_index('sites')
    return elastic.show_index('words_pairs')

@app.get("/import")
async def import_initial():
    return elastic.initial_import()


@app.get("/import/{index}")
async def importing(index: str):
    return elastic.import_texts_from_html(index)


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
    phs = elastic.get_phrase_count('text_for_calc', 'freexian sarl')
    # elastic.get_phrase_count('text_for_calc', 'test')
    return phs