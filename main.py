from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Iterable
from datetime import date
import subprocess

LEDGER_UTILITY = ("hledger",)
DEFAULT_ENTRY = "other..."
COMMODITY = "₽"

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

def exec_ledger_command(arguments: Iterable[str]) -> str | None:
    result = subprocess.run([*LEDGER_UTILITY, *arguments], capture_output=True)
    if result.returncode != 0:
        print(result.stderr.decode("utf-8"))
        return None
    return result.stdout.decode("utf-8")

def parse_monthly_expenses(begin: str | None = None, end: str | None = None) -> dict[str, dict[str, float]]:
    command = ["bal", "expenses", "-O", "csv"]
    if begin is not None:
        command.extend(["-b", begin])
    if end is not None:
        command.extend(["-e", end])

    output = exec_ledger_command(command)

    assert output is not None
    lines = output.split("\n")

    accounts: dict[str, dict[str, float]] = {}
    top: str
    secondary: str
    for line in lines[1:-1]:
        account, balance = map(lambda entry: entry.strip("\""), line.split(","))
        split = account.split(":")[1:]
        if len(split) == 0:
            continue
        if len(split) == 1:
            top = split[0]
            secondary = DEFAULT_ENTRY
        else:
            top, secondary = split[:2]
        if top not in accounts:
            accounts[top] = {}
        if secondary not in accounts[top]:
            accounts[top][secondary] = 0
        accounts[top][secondary] += float(balance.lstrip(COMMODITY))

    return accounts

@app.get("/expenses")
async def get_monthly_expenses(begin: date | None = None, end: date | None = None):
    begin_formatted = None if begin is None else begin.isoformat()
    end_formatted = None if end is None else end.isoformat()
    return parse_monthly_expenses(begin_formatted, end_formatted)
