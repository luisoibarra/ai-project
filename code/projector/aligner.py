from utils.console_utils import make_command, run_bash_command
from projector.translator import Translator
from corpus_parser.conll_parser import ConllParser
from typing import Callable, List, Dict, Optional, Tuple, Union
from nltk import sent_tokenize, word_tokenize
import logging as log

from pathlib import Path

class Aligner:
    """
    Abstract class that makes the sentence to sentence alignment process and the bidirectional alignment.
    """
    
    SEPARATOR = " ||| "
    
    def __init__(self, translator: Translator) -> None:
        """
        Initialize aligner
        
        translator: Class in charge of sentence translation
        """
        self.translator = translator
    
    def sentence_alignment_dir(self, corpus_address:Path, sentence_dest:Path, **kwargs):
        """
        Read all cropus files from `corpus_address` and write the respective sentences 
        aligned in `sentence_dest`. The written files will have .align suffix.
        
        corpus_address: Corpus address
        corpus_dest: Path to save the processed corpus
        sentence_dest: Where to save the sentence alignment
        """
        parser = ConllParser() # TODO GENERAL PARSER GOES HERE
        df_representations = parser.parse_dir(corpus_address) # CONVERT TO MIDDLE TRANSOFMATION
        
        if not sentence_dest.exists(): sentence_dest.mkdir()
        
        bio_parser = ConllParser()
        tags = bio_parser.from_dataframes(df_representations, get_tags=True, **kwargs)
        
        for key, (annotated_tags_info, text) in tags.items():
            sentence_sentence_text = self.make_sentence_sentence_text(text, **kwargs)
            dest_file = sentence_dest / (Path(key).name + ".align")
            dest_file.write_text(sentence_sentence_text)
            # for sentence_sentence in sentence_sentence_text.split("\n"):
            #     source, target = sentence_sentence.split(kwargs.get("separator", self.SEPARATOR))

    def bidirectional_align_dir(self, sentence_alignment_dir: Path, align_dest: Path, **kwargs):
        """
        Read the `.align` files in `sentence_alignment_dir` and write in `align_dest` the
        bidirectional alignments. The files have the suffix `.bidirectional`
        
        sentence_alignment_dir: Address of the aligned sentences
        align_dest: Destination directory for the bidirectional alignments
        """
        
        if not align_dest.exists(): align_dest.mkdir()
        
        for file in sentence_alignment_dir.iterdir():
            if file.is_file() and file.name.endswith(".align"):
                dest_file = align_dest / (file.name + ".bidirectional")
                self.do_bidirectional_align_file(file, dest_file, **kwargs)

    def make_sentence_sentence_text(self, text: str, word_tokenizer: Callable[[str,],List[str]]=word_tokenize, 
                                    sent_tokenizer: Callable[[str,],List[str]]=sent_tokenize, 
              source_language: str="english", target_language: str="spanish", separator: str=SEPARATOR) -> str:
        """
        Split the given `text` sentence by sentence using the given `sent_tokenizer`. The
        split is made by placing in each line the sentence in `source_language`
        followed by `separator` and then the sentence in `target_language`  
        
        text: Text to be splitted
        word_tokenizer: Function that receives a text and a language and returns a list with
        the tokens present in text
        sent_tokenizer: Function that receives a text and a language and returns a list with
        the sentences present in text
        source_language: text's language
        target_language: Language to be translated
        separator: Text separating the sentences in source language and target language
        
        returns: The aligned text, tokens are separated by spaces
        """
        
        sentences = sent_tokenizer(text, language=source_language)
        result = ""
        for sentence in sentences:
            # Result is the sentence's tokens separated by spaces
            source_sentence_with_spaces = " ".join(word_tokenizer(sentence, language=source_language))
            target_sentence = self.translate(sentence, source_language=source_language, target_language=target_language)
            target_sentence_with_spaces = " ".join(word_tokenizer(target_sentence, language=target_language))
            
            result += source_sentence_with_spaces + \
                      separator + \
                      target_sentence_with_spaces + \
                      "\n"
        return result
    
    def translate(self, sentence: str, source_language="english", target_language="spanish") -> str:
        """
        Translate given `sentence` in `source_language` into `target_language`
        
        sentence: Sentence to translate
        source_language: Language of given sentence
        target_language: Language to translate the sentence
        
        returns: The translated sentence
        """
        return self.translator.translate(sentence, source_language, target_language)
    
    def do_bidirectional_align_file(self, sentence_align_dir: Path, alignment_dest: Path, **kwargs):
        """
        Get the alignment from the text in `sentence_align_dir`. The alignment will match the line with sentence,
        the format will be a list of `tok_source_index-tok_dest_index` representing
        the token alignment.
        
        sentence_align_dir: File were the sentences in source and target languages. The 
        tokens within sentences must be separated by spaces
        alignment_dest: Destination file to save the word alignment.
        """
        raise NotImplementedError()


class SelfLanguageAligner(Aligner):
    """
    Aligner that only takes into account the source language and performs a self annotation.
    
    Its main purpose is testing.
    """

    def do_bidirectional_align_file(self, sentence_align_dir: Path, alignment_dest: Path, **kwargs):
        sentence_aligment = sentence_align_dir.read_text().splitlines()
        bidirectional_alignment_text = ""
        for sentence_pair in sentence_aligment:
            source_sentence, target_sentence = sentence_pair.split(Aligner.SEPARATOR)
            bidirectional_alignment_text += " ".join(f"{i}-{i}" for i,tok in enumerate(source_sentence.split(" "))) + "\n"
        alignment_dest.write_text(bidirectional_alignment_text)

class FastAlignAligner(Aligner):
    """
    Aligner using the fast_align algorithm. 
    """
    
    def __init__(self, translator: Translator, fast_align_path: Optional[Path] = None) -> None:
        super().__init__(translator)
        self.fast_align_path = fast_align_path if fast_align_path else Path(__file__, "..", "fast_align", "build", "fast_align").resolve()
    
    def do_bidirectional_align_file(self, sentence_align_dir: Path, alignment_dest: Path, atools_opt: bool=True, **kwargs):
        """
        Uses the fast_align algorithm to provide the bidirectional alignment for the
        sentences in `sentence_align_dir`. 
        
        sentence_align_dir: File were the sentences in source and target languages. The 
        tokens within sentences must be separated by spaces
        alignment_dest: Destination file to save the word alignment.
        atools_opt: If the atools optimizations are performed
        """
        # ./fast_align -i {sentence_align_dir} -d -o -v > {alignment_dest}
        fast_align_cmd = f'"{Path(self.fast_align_path).relative_to(Path().resolve())}"'
        atools_cmd = f'"{Path(self.fast_align_path, "..", "atools").resolve().relative_to(Path().resolve())}"'
        
        forward_command = make_command( 
            fast_align_cmd, 
            "-i", 
            str(sentence_align_dir), 
            "-d",
            "-o",
            "-v",
            ">",
            str(alignment_dest)
        )
        run_bash_command(forward_command)
        
        reverse_alignment_dest = alignment_dest / ".." / (alignment_dest.name + ".reverse.bidirectional")
        reverse_alignment_dest = reverse_alignment_dest.resolve().relative_to(Path().resolve())
        
        backward_command = make_command( 
            fast_align_cmd, 
            "-i", 
            str(sentence_align_dir), 
            "-d",
            "-o",
            "-v",
            "-r",
            ">",
            str(reverse_alignment_dest)
        )
        run_bash_command(backward_command)
        

        if atools_opt:
            revised_alignment_dest = alignment_dest / ".." / (alignment_dest.name + ".revised.bidirectional")
            revised_alignment_dest = revised_alignment_dest.resolve().relative_to(Path().resolve())
            improvement_command = make_command(
                atools_cmd, 
                "-i", 
                str(alignment_dest), 
                "-j",
                str(reverse_alignment_dest), 
                "-c",
                "grow-diag-final-and",
                ">",
                str(revised_alignment_dest)
            )
            
            run_bash_command(improvement_command)
            
            copy_command = make_command(
                "cp", 
                str(revised_alignment_dest),
                str(alignment_dest), 
            )
            
            run_bash_command(copy_command)
            
class AwesomeAlignAligner(Aligner):
    """
    Aligner using awesome-align algorithm.
    """

    SUPPORTED_KEYS = {
        "model_name_or_path",
        "data_file"
        "output_files",
        "extraction",
        "batch_size"
    }
    
    def __init__(self, translator: Translator, awesome_align_path: Optional[Path] = None) -> None:
        super().__init__(translator)
        self.awesome_align_path = awesome_align_path if awesome_align_path else Path(__file__, "..", "awesome-align", "awesome_align").resolve().relative_to(Path())
    
    def do_bidirectional_align_file(self, sentence_align_dir: Path, alignment_dest: Path, **kwargs):
        kwargs = kwargs.copy()
        
        kwargs.setdefault("model_name_or_path", "bert-base-multilingual-cased")
        kwargs.setdefault("output_file", str(alignment_dest))
        kwargs.setdefault("data_file", str(sentence_align_dir))
        kwargs.setdefault("batch_size", 32)
        kwargs.setdefault("extraction", "softmax")
        
        awesome_align_cmd = make_command(
            'python3',
            f'{self.awesome_align_path / "run_align.py"}',
            *[f"--{key}={value}" for key,value in kwargs.items() if key in self.SUPPORTED_KEYS]
        )
        run_bash_command(awesome_align_cmd)
        
        