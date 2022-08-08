import argparse
from projector.aligner import AwesomeAlignAligner, FastAlignAligner
from pipelines.corpus_pipelines import full_corpus_processing_pipeline
from projector.translator import FromCorpusTranslator
from projector.projector import CrossLingualAnnotationProjector
from corpus_parser.bret_parser import BretParser
from corpus_parser.conll_parser import ConllParser
from corpus_parser.parser import Parser
from pathlib import Path

corpus_parser = argparse.ArgumentParser()

# Paths
corpus_parser.add_argument("source_path", 
                    help="Path that contains the files to be parsed",
                    type=Path)
corpus_parser.add_argument("destination_path", 
                    help="Destination path to save the parsed files",
                    type=Path)
corpus_parser.add_argument("sentence_alignment_path", 
                    help="Destination path to save the aligned sentences",
                    type=Path)
corpus_parser.add_argument("bidirectional_path", 
                    help="Destination path to save the sentence's bidirectional alignments",
                    type=Path)
corpus_parser.add_argument("projection_path", 
                    help="Destination path to save the projected sentences",
                    type=Path)

# Algorithm choices
parsers = ["bret", "conll"]
corpus_parser.add_argument("--parser",
                    help="Select the type of parser to use",
                    type=str,
                    # nargs="?",
                    # const=parsers[0],
                    default=parsers[0],
                    choices=parsers)
projectors = ["cross"]
corpus_parser.add_argument("--projector",
                    help="Select the projection algorithm to use",
                    type=str,
                    # nargs="?",
                    # const=projectors[0],
                    default=projectors[0],
                    choices=projectors)
aligners = ["fast_align", "awesome_align"]
corpus_parser.add_argument("--aligner",
                    help="Select the alignment algorithm to use",
                    type=str,
                    # nargs="?",
                    # const=aligners[0],
                    default=aligners[0],
                    choices=aligners)
translators = ["corpus"]
corpus_parser.add_argument("--translator",
                    help="Select the translation process",
                    type=str,
                    # nargs="?",
                    # const=translators[0],
                    default=translators[0],
                    choices=translators)

# Other Args
corpus_parser.add_argument("--source_language_sentences",
                    help="Required if corpus translator is selected: Path for the sentences in source language",
                    type=Path,
                    default=None)
corpus_parser.add_argument("--target_language_sentences",
                    help="Required if corpus translator is selected: Path for the sentences in target language",
                    type=Path,
                    default=None)

corpus_parser.add_argument("--source_language",
                    help="Source language",
                    type=str,
                    default="english")
corpus_parser.add_argument("--target_language",
                    help="Target language",
                    type=str,
                    default="spanish")

# Pasing arguments
args = corpus_parser.parse_args()
print(args)
# Get values
parser = {
    "bret": BretParser(),
    "conll": ConllParser(),
}[args.parser]

projector = {
    "cross": CrossLingualAnnotationProjector(),
}[args.projector]

translator = {
    "corpus": FromCorpusTranslator(args.source_language_sentences, 
                                   args.target_language_sentences, 
                                   args.source_language, 
                                   args.target_language),
}[args.translator]

aligner = {
    "fast_align": FastAlignAligner(translator), 
    "awesome_align": AwesomeAlignAligner(translator), 
}[args.aligner]

full_corpus_processing_pipeline(
    args.source_path,
    args.destination_path,
    args.sentence_alignment_path,
    args.bidirectional_path,
    args.projection_path,
    parser,
    aligner,
    projector,
    source_language = args.source_language,
    target_language = args.target_language,
)