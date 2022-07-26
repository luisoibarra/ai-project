from projector.translator import SelfTranslator, FromCorpusTranslator
from corpus_parser.conll_parser import ConllParser
from pipelines.corpus_pipelines import full_corpus_processing_pipeline, parse_corpus_pipeline
from projector.projector import SelfLanguageProjector, CrossLingualAnnotationProjector
from projector.aligner import SelfLanguageAligner, FastAlignAligner

from corpus_parser.bret_parser import BretParser
from pathlib import Path

def corpus_processing_example():
    """
    This example is the one that creates the `data/**/testing/` files, except the ones in `data/corpus/testing`
    """

    base_path = Path("code", "data")
    dataset_name = "testing2"

    corpus_parser = BretParser()

    corpus_dir = Path(base_path, "corpus", dataset_name)

    exported_conll_dir = Path(base_path, "parsed_to_conll", dataset_name)

    # translator = SelfTranslator()
    translator = FromCorpusTranslator(
        Path(base_path, "translation", dataset_name, "testing_en"),
        Path(base_path, "translation", dataset_name, "testing_es"),
        "english",
        "spanish"
    )

    # aligner = SelfLanguageAligner(translator)
    aligner = FastAlignAligner(translator)

    sentences_alignment_dir = Path(base_path, "sentence_alignment", dataset_name)
    bidirectional_alignment_dir = Path(base_path, "bidirectional_alignment", dataset_name)

    # projector = SelfLanguageProjector()
    projector = CrossLingualAnnotationProjector()

    projection_dir = Path(base_path, "projection", dataset_name)

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
    # parse_corpus_pipeline(Path("code", "data", "corpus", "ArgumentAnnotatedEssays-2.0", "train-test-split", "dev"),
    #                       Path("code", "data", "parsed_to_conll", "ArgumentAnnotatedEssays-2.0", "dev"),
    #                       BretParser())
    # parse_corpus_pipeline(Path("code", "data", "corpus", "ArgumentAnnotatedEssays-2.0", "train-test-split", "train"),
    #                       Path("code", "data", "parsed_to_conll", "ArgumentAnnotatedEssays-2.0", "train"),
    #                       BretParser())
    # parse_corpus_pipeline(Path("code", "data", "corpus", "ArgumentAnnotatedEssays-2.0", "train-test-split", "test"),
    #                       Path("code", "data", "parsed_to_conll", "ArgumentAnnotatedEssays-2.0", "test"),
    #                       BretParser())
