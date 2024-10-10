from fastapi import FastAPI

app = FastAPI()

items = []

@app.get("/")
def root():
    return {"Hello": "World"}

@app.pos("/items")
def create_item(item: str):
    items.append(item)
    return items