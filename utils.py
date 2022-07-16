import re
from typing import Iterable, List, Callable, Dict

from flask import abort


def map_(iter_obj: Iterable, col_num: str) -> Iterable:
    """Returns column by column number"""
    col_patterns = {
        '0': r'(?:\d{1,3}\.){3}\d{1,3}',
        '1': r'\s-\s',
        '2': r'\B\s-\s',
        '3': r"\[.+\]",
        '4': r"\".+HTTP/[12]\.\d*\"",
        '5': r"\s\d{3}\s",
        '6': r"(?:\b\s\d{1,}\s| - [^\[-])",
        "7": r"(?:\"http[s]*:.+\" |\s\"-\"\s)",
        "8": r"(?:\s\"[^\"]{1,}\"$|\s\"-\"\s$)"
    }
    try:
        # col_data = [re.search(col_patterns[col_num], line).group() for line in iter_obj if re.search(col_patterns[col_num], line)]
        # Чтобы обойти ошибку mypy Item "None" of "Optional[Match[str]]" has no attribute "group"
        # пришлось использовать цикл вместо list comprehensions
        col_data = []
        for line in iter_obj:
            match = re.search(col_patterns[col_num], line)
            if match:
                col_data.append(match.group())
        col_data_stripped = map(lambda column: column.strip(' " ') + '\n', col_data)
        return col_data_stripped
    except (KeyError, AttributeError, TypeError):
        abort(400, f'Column {col_num} cannot be found or does not exist')


def unique(iter_obj: Iterable, value: str = "") -> Iterable:
    """Returns unique elements"""
    return set(iter_obj)


def sort_(iter_obj: Iterable, order: str = 'asc') -> Iterable:
    """Sorts by ascending/descending order"""
    sort_order = {
        'asc': False,
        'desc': True,
    }
    try:
        return sorted(iter_obj, reverse=sort_order[order])
    except KeyError:
        abort(400, "Requested data cannot be sorted")


def filter_(iter_obj: Iterable, pattern: str) -> Iterable:
    """Returns data with by matched pattern"""
    filtered_by_pattern = [line for line in iter_obj if pattern.lower() in line.lower()]
    return filtered_by_pattern


def limit(iter_obj: Iterable, limit_num: str | int) -> Iterable:
    """Returns data rows limited by limit_num"""
    try:
        limit_num = int(limit_num)
        counter = 1
        data = []
        for el in iter_obj:
            if limit_num >= counter:
                data.append(el)
                counter += 1
            else:
                break
        return data
    except (TypeError, ValueError):
        abort(400, 'Invalid limit number')


def regexp(iter_obj: Iterable, regexp: str) -> List[str]:
    """Returns rows with matched regexp pattern"""
    regexp_ = re.compile(regexp)
    result = [line for line in iter_obj if regexp_.search(line)]
    return result


def process_request(file_path: str, cm_1: str, val_1: str, cm_2: str, val_2: str) -> Iterable:
    """Filters data based on commands and values"""
    commands: Dict[str, Callable] = {
        "filter": filter_,
        "map": map_,
        "unique": unique,
        "sort": sort_,
        "limit": limit,
        "regexp": regexp,
    }
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = commands[cm_1](f, val_1)
            if cm_2:
                data = commands[cm_2](data, val_2)
            return data
    except KeyError:
        abort(400, 'Command does not exist')


if __name__ == '__main__':
    pass

