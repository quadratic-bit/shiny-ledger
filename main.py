from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import date

from cli import parse_category_stat, parse_top_level_categories

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root(request: Request):
    today = date.today()
    current_year_month = (today.year, today.month)
    next_year_month: tuple[int, int]
    if today.month == 12:
        next_year_month = (today.year + 1, 1)
    else:
        next_year_month = (today.year, today.month + 1)
    begin_default = date(*current_year_month, 1)
    end_default = date(*next_year_month, 1)
    return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "begin_default": begin_default.isoformat(),
                "end_default": end_default.isoformat()
            })

@app.get("/stat")
async def get_category_stat(category: str, begin: date | None = None, end: date | None = None):
    begin_formatted = None if begin is None else begin.isoformat()
    end_formatted = None if end is None else end.isoformat()
    return parse_category_stat(category, begin_formatted, end_formatted)

@app.get("/categories")
async def get_top_level_categories():
    return parse_top_level_categories()
