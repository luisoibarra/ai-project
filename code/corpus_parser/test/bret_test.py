import sys
from pathlib import Path

sys.path.append(str((Path(__file__)/".."/".."/"..").resolve()))


from corpus_parser.bret_parser import BretParser


def test_parse():
    base = Path(__file__) / ".." / ".." / ".." / "corpus" / "ArgumentAnnotatedEssays-2.0" / "brat-project-final" / "brat-project-final"
    base = base.resolve()

    parser = BretParser()
    result = parser.parse_dir(base)
    result1, result2, result3 = next(x for x in result.values())
    print(result1.describe())
    print(result2.describe())
    print(result3.describe())

