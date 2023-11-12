from fastapi import FastAPI
from pydantic import BaseModel
from navec import Navec
from slovnet import Syntax
from ipymarkup import show_dep_ascii_markup as show_markup
from ipymarkup import format_dep_ascii_markup
from razdel import sentenize, tokenize
from starlette.middleware.cors import CORSMiddleware

if __name__ == "__main__":
    navec = Navec.load('navec_news_v1_1B_250K_300d_100q.tar')
    syntax = Syntax.load('slovnet_syntax_news_v1.tar')
    syntax.navec(navec)
    text = "Последнее время мне стало жить тяжело"
    chunk = []
    for sent in sentenize(text):
        tokens = [_.text for _ in tokenize(sent.text)]
    chunk.append(tokens)
    markup = next(syntax.map(chunk))
    print(chunk[:1])
    words, deps = [], []
    for token in markup.tokens:
        words.append(token.text)
        source = int(token.head_id) - 1
        target = int(token.id) - 1
        if source > 0 and source != target:  # skip root, loops
            deps.append([source, target, token.rel])
    show_markup(words, deps)
    mas=[]
    for line in format_dep_ascii_markup(words,deps):
        mas.append(line)
    print(mas)


def fake_answer_to_everything_ml_model():
    navec = Navec.load('navec_news_v1_1B_250K_300d_100q.tar')
    syntax = Syntax.load('slovnet_syntax_news_v1.tar')
    syntax.navec(navec)
    return syntax

syntaxObj = fake_answer_to_everything_ml_model()



app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Item(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"message": "This is Slovnet SaaS by Victor Ershov"}

@app.post("/analyze/")
async def analyze(req: Item):
    global syntaxObj
    syntax = syntaxObj
    chunk = []
    for sent in sentenize(req.text):
        tokens = [_.text for _ in tokenize(sent.text)]
    chunk.append(tokens)
    markup = next(syntax.map(chunk))
    print(chunk[:1])
    words, deps = [], []
    for token in markup.tokens:
        words.append(token.text)
        source = int(token.head_id) - 1
        target = int(token.id) - 1
        if source > 0 and source != target:  # skip root, loops
            deps.append([source, target, token.rel])
    if len(deps) == 0:
        return "ошибка анализа"
    show_markup(words, deps)
    mas = []
    for line in format_dep_ascii_markup(words, deps):
        mas.append(line)
    return mas

