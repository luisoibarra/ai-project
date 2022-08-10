import logging
from projector.translator import Translator
from typing import Callable, Dict, List, Optional, Tuple
from corpus_parser.conll_parser import ConllParser
from pathlib import Path
from nltk import sent_tokenize, word_tokenize

class SentenceAligner:
    
    SEPARATOR = " ||| "
    
    def __init__(self, translator: Translator) -> None:
        """
        Initialize aligner
        
        translator: Class in charge of sentence translation
        """
        self.translator = translator

    def sentence_alignment_dir(self, corpus_address:Path, sentence_dest:Path, sentences_splitted=True, **kwargs):
        """
        Read all cropus files from `corpus_address` and write the respective sentences 
        aligned in `sentence_dest`. The written files will have .align suffix.
        
        corpus_address: Corpus address
        corpus_dest: Path to save the processed corpus
        sentence_dest: Where to save the sentence alignment
        sentences_splitted: If in the conll file the sentence are splitted by an empty line 
        """
        parser = ConllParser()
        df_representations = parser.parse_dir(corpus_address) # CONVERT TO MIDDLE TRANSOFMATION
        
        if not sentence_dest.exists(): sentence_dest.mkdir()
        
        bio_parser = ConllParser()
        tags = bio_parser.from_dataframes(df_representations, get_tags=True, **kwargs)
        
        for key, (annotated_tags_info, text) in tags.items():
            if sentences_splitted:
                text = " ".join(tok["tok"] for tok in annotated_tags_info)
            sentence_sentence_text = self.make_sentence_sentence_text(text, sentences_splitted=sentences_splitted, **kwargs)
            dest_file = sentence_dest / (Path(key).name + ".align")
            dest_file.write_text(sentence_sentence_text)

    def make_sentence_sentence_text(self, text: str, sentences_splitted=True, word_tokenizer: Callable[[str,],List[str]]=word_tokenize, 
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
        sentences_splitted: If the text is already splitted by sentences separated with newlines
        
        returns: The aligned text, tokens are separated by spaces
        """
        
        sentences = sent_tokenizer(text, language=source_language) if not sentences_splitted else text.splitlines()
        result = ""
        with self.translator as translator:
            for sentence in sentences:
                # Result is the sentence's tokens separated by spaces
                source_sentence_with_spaces = " ".join(word_tokenizer(sentence, language=source_language)).strip()
                target_sentence = translator.translate(source_sentence_with_spaces, source_language=source_language, target_language=target_language)
                target_sentence_with_spaces = " ".join(word_tokenizer(target_sentence, language=target_language)).strip()
                
                result += source_sentence_with_spaces + \
                        separator + \
                        target_sentence_with_spaces + \
                        "\n"
        return result