import sys
from pathlib import Path

sys.path.append(str((Path(__file__)/".."/".."/"..").resolve()))

from corpus_parser.conll_parser import ConllParser


def test_parse():
    base = Path(__file__) / ".." / ".." / ".." / "corpus" / "scidtb_argmin_annotations"
    base = base.resolve()

    parser = ConllParser()
    result = parser.parse_dir(base)
    result1, result2, result3 = next(x for x in result.values())
    print(result1.describe())
    print(result2.describe())
    print(result3.describe())

def test_from_dataframe():
    base = Path(__file__) / ".." / ".." / ".." / "corpus" / "scidtb_argmin_annotations"
    base = base.resolve()

    parser = ConllParser()
    result = parser.parse_dir(base)
    result2 = parser.from_dataframes(result)
    key = next(iter(result2.keys()))
    result3 = parser.parse(result2[key], file=key)
    print(result3)