from corpus_parser.conll_parser import ConllParser
from typing import Callable, List, Dict, Tuple, Union
from nltk import sent_tokenize, word_tokenize
import logging as log

from pathlib import Path

class Aligner:
    """
    Abstract class that makes the sentence to sentence alignment process and the bidirectional alignment.
    """
    
    SEPARATOR = " ||| "
    
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
        raise NotImplementedError()
    
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
    
    def translate(self, sentence: str, source_language="english", target_language="spanish") -> str:
        return sentence
    
    def do_bidirectional_align_file(self, sentence_align_dir: Path, alignment_dest: Path, **kwargs):
        sentence_aligment = sentence_align_dir.read_text().splitlines()
        bidirectional_alignment_text = ""
        for sentence_pair in sentence_aligment:
            source_sentence, target_sentence = sentence_pair.split(Aligner.SEPARATOR)
            bidirectional_alignment_text += " ".join(f"{i}-{i}" for i,tok in enumerate(source_sentence.split(" "))) + "\n"
        alignment_dest.write_text(bidirectional_alignment_text)
            