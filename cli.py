import subprocess
from typing import Iterable

from const import LEDGER_UTILITY, DEFAULT_ENTRY, COMMODITY

def exec_ledger_command(arguments: Iterable[str]) -> str | None:
    result = subprocess.run([*LEDGER_UTILITY, *arguments], capture_output=True)
    if result.returncode != 0:
        print(result.stderr.decode("utf-8"))
        return None
    return result.stdout.decode("utf-8")

def parse_category_stat(category: str, begin: str | None = None, end: str | None = None) -> dict[str, dict[str, float]]:
    command = ["bal", category, "-O", "csv"]
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

def parse_top_level_categories() -> list[str]:
    output = exec_ledger_command(["accounts"])
    assert output is not None
    accounts = output.split("\n")

    return sorted(list(filter(None, set(acc.split(":")[0] for acc in accounts))))
