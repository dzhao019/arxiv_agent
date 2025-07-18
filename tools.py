import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal, Union

class Article:
    def __init__(self):
        self.title = None
        self.paperid = None

    def set_title(self, title):
        self.title = title

    def set_paperid(self, paperid):
        self.paperid = paperid


class Titleabs:
    def __init__(self, title, abstract):
        self.title = title
        self.abstract = abstract


def getid(article, myart, articlelist):
    articlelist.append(myart)
    a = article.find("a", class_="line-clamp-3 cursor-pointer text-balance")
    # /papers/####.#####
    paperid = a["href"][8:]
    myart.set_paperid(paperid)

    # title
    title = a.text
    title = " ".join(title.strip().split())
    myart.title = title


def getarticles_fast(parameters):
    date_id = parameters.date
    r = requests.get(f"https://huggingface.co/papers/date/{date_id}")
    soup = BeautifulSoup(r.content, "html.parser")
    articles = soup.find_all("article")
    articlelist = []

    for article in articles:
        myart = Article()
        getid(article, myart, articlelist)

    if not articlelist:
        return {"tool_name": "PaperListTool", "error": 'No such date'}

    return {"tool_name": "PaperListTool", "papers": articlelist}


def ta_from_paperid(parameters):
    paperid = parameters.paperid
    r = requests.get(f"https://arxiv.org/abs/{paperid}")
    soup = BeautifulSoup(r.content, "html.parser")
    soup1 = soup.find("div", id="abs")

    if soup1 is None:
        return {"tool_name": "AbstractTool", "error": 'No such paper id'}

    title = soup1.find("h1", class_="title mathjax").text.strip()[6:]
    abstract = soup1.find("blockquote", class_="abstract mathjax")
    url = ""

    # replaces "this url" with the linked url
    try:
        url = abstract.find("a")["href"]
        abstract = abstract.text.replace("this https URL", url)
    except TypeError:
        abstract = abstract.text

    abstract = abstract.strip()[9:]

    return {"tool_name": "AbstractTool", "paper": Titleabs(title, abstract)}


class PaperTool(BaseModel):
    date: str


class AbstractTool(BaseModel):
    paperid: str


class ToolReq(BaseModel):
    tool_name: Literal["PaperListTool", "AbstractTool"]
    parameters: Union[PaperTool, AbstractTool]
    request_id: str


app = FastAPI()

@app.post("/call_tool")
def call_tool(tool_req: ToolReq):
    if tool_req.tool_name == "PaperListTool":
        return getarticles_fast(tool_req.parameters)

    elif tool_req.tool_name == "AbstractTool":
        return ta_from_paperid(tool_req.parameters)
