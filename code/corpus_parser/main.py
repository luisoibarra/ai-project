if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        print(path)
        sys.path.insert(0, path)

import argparse
from corpus_parser.parser import Parser
from corpus_parser.conll_parser import ConllParser
from corpus_parser.bret_parser import BretParser
from corpus_parser.unified_parser import UnifiedParser
from pathlib import Path
from utils.argparser_utils import ChoiceArg, OptionalArg, PositionalArg, update_parser

positional_args = [
    PositionalArg(
        name="source_path",
        help="Path that contains the files to be parsed",
        type=Path
    ),
    PositionalArg(
        name="conll_parsed_path",
        help="Destination path to save the conll parsed files",
        type=Path
    ),
]

choice_args = [
    ChoiceArg(
        name="parser",
        help="Select the type of parser to use",
        type=str,
        values=("unified", "bret", "conll")
    ),
]

optional_args = [
    OptionalArg(
        name="source_language",
        help="Source language",
        type=str,
        default="english"
    ),
    OptionalArg(
        name="target_language",
        help="Target language",
        type=str,
        default="spanish"
    ),
]

def create_from_args(args) -> Parser:
    # Get values
    parser = {
        "unified": UnifiedParser(),
        "bret": BretParser(),
        "conll": ConllParser(),
    }[args.parser]
    
    return parser

def handle_from_args(args):
    parser = create_from_args(args)
    parser.parse_dir(args.source_path, 
                     args.conll_parsed_path, 
                     source_language=args.source_language, 
                     target_language=args.target_language)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    update_parser(parser, positional_args, choice_args, optional_args)
    
    args = parser.parse_args()
    
    handle_from_args(args)
    