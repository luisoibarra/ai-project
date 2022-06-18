from pipelines.corpus_pipelines import full_corpus_processing_pipeline
from projector.projector import SelfLanguageProjector
from projector.aligner import SelfLanguageAligner

from corpus_parser.bret_parser import BretParser
from pathlib import Path

def corpus_processing_example():
    """
    This example is the one that creates the `data/**/testing/` files, except the ones in `data/corpus/testing`
    """

    corpus_parser = BretParser()

    corpus_dir = Path(".", "data", "corpus", "testing")

    exported_conll_dir = Path(".", "data", "parsed_to_conll", "testing")

    aligner = SelfLanguageAligner()

    sentences_alignment_dir = Path(".", "data", "sentence_alignment", "testing")
    bidirectional_alignment_dir = Path(".", "data", "bidirectional_alignment", "testing")

    projector = SelfLanguageProjector()

    projection_dir = Path(".", "data", "projection", "testing")

    full_corpus_processing_pipeline(
        corpus_dir, 
        exported_conll_dir, 
        sentences_alignment_dir, 
        bidirectional_alignment_dir, 
        projection_dir, 
        corpus_parser, 
        aligner, 
        projector)

if __name__ == "__main__":
    corpus_processing_example()
