if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        print(path)
        sys.path.insert(0, path)

from aligner.aligner import Aligner, AwesomeAlignAligner, FastAlignAligner
import argparse
from pathlib import Path
from utils.argparser_utils import ChoiceArg, OptionalArg, PositionalArg, update_parser

positional_args = [
    PositionalArg(
        name="sentence_alignment_path",
        help="Destination path to save the aligned sentences",
        type=Path
    ),
    PositionalArg(
        name="bidirectional_path",
        help="Destination path to save the sentence's bidirectional alignments",
        type=Path
    ),
]

choice_args = [
    ChoiceArg(
        name="aligner",
        help="Select the alignment algorithm to use",
        type=str,
        values=("fast_align", "awesome_align")
    ),
]

optional_args = [
]

def create_from_args(args) -> Aligner:
    aligner = {
        "fast_align": FastAlignAligner(), 
        "awesome_align": AwesomeAlignAligner(), 
    }[args.aligner]
    return aligner

def handle_from_args(args):
    aligner = create_from_args(args)
    aligner.bidirectional_align_dir(
        args.sentence_alignment_path,
        args.bidirectional_path,
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    update_parser(parser, positional_args, choice_args, optional_args)
    
    args = parser.parse_args()
    
    handle_from_args(args)
    