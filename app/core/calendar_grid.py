from __future__ import annotations
from dataclasses import dataclass
from datetime import date
import calendar

@dataclass(frozen=True)
class Cell:
    r: int  # 1..6
    c: int  # 1..7  (SUN..SAT)

def sun0_weekday(d: date) -> int:
    # Python weekday(): Mon=0..Sun=6  -> Sun=0..Sat=6
    return (d.weekday() + 1) % 7

def days_in_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]

def cell_to_day(year: int, month: int, cell: Cell) -> int | None:
    """
    Returns day number (1..N) if this cell belongs to the month, else None.
    Calendar grid columns are SUN..SAT.
    """
    first = date(year, month, 1)
    offset = sun0_weekday(first)  # where day=1 is placed in row1
    idx = (cell.r - 1) * 7 + (cell.c - 1)  # 0..41
    day = idx - offset + 1
    dim = days_in_month(year, month)
    if 1 <= day <= dim:
        return day
    return None
