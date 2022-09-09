if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        print(path)
        sys.path.insert(0, path)

import argparse
from pathlib import Path
from segmenter.tf_segmenter import TensorflowArgumentSegmenter
from segmenter.segmenter import ArgumentSegmenter
from utils.argparser_utils import ChoiceArg, OptionalArg, PositionalArg, update_parser

positional_args = [
    PositionalArg(
        name="model_path",
        help="Path to the argument segmentation trained model",
        type=Path
    ),
    PositionalArg(
        name="segmenter_source_path",
        help="Path to the directory containing the files to perform argument segmentation",
        type=Path
    ),
    PositionalArg(
        name="segmenter_export_path",
        help="Path to the save the result of the argument segmentation process",
        type=Path
    ),
]

choice_args = [
    ChoiceArg(
        name="segmenter",
        help="Select the segmentation algorithm to use",
        type=str,
        values=("tensorflow",)
    ),
]

optional_args = [
]

def create_from_args(args) -> ArgumentSegmenter:
    segmenter = {
        'tensorflow': TensorflowArgumentSegmenter(args.model_path), 
    }[args.segmenter]
    return segmenter

def handle_from_args(args):
    argument_segmenter = create_from_args(args)
    argument_segmenter.extract_arguments_dir(
        annotation_dir=args.segmenter_source_path,
        export_dir=args.segmenter_export_path,
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    update_parser(parser, positional_args, choice_args, optional_args)
    
    args = parser.parse_args()
    
    handle_from_args(args)
    