

import logging
import re
from typing import Dict, Tuple
from corpus_parser.conll_parser import ConllParser
from pathlib import Path
from nltk import sent_tokenize

class Translator:

    def translate(self, source_sentence: str, source_language:str, target_language: str) -> str:
        """
        Translate given `sentence` in `source_language` into `target_language`
        
        sentence: Sentence to translate
        source_language: Language of given sentence
        target_language: Language to translate the sentence
        
        returns: The translated sentence
        """
        raise NotImplementedError()


class SelfTranslator(Translator):
    
    def translate(self, source_sentence: str, source_language:str, target_language: str) -> str:
        return source_sentence
    
class FromCorpusTranslator(Translator):
    """
    Translator that maps the sentences in source_dir with target_dir,
    the files must be named in a way that when sorting them by name 
    the order is the same in both directories. The sentences in the
    files must be in the same order and separated by a new line
    """
    
    SEP_REGEX = r"(?P<letter>)\w\n[\n]+"
    
    def __init__(self, source_dir: Path, target_dir: Path, 
                 source_language: str, target_language: str) -> None:
        super().__init__()
        self.source_dir = source_dir
        self.target_dir = target_dir
        # __translation_dict: 
        #   key=source_lang, dest_lang, source_sentence
        #   value=target_sentence
        self.__translation_dict: Dict[Tuple[str,str,str],str] = {}
        self.__sep_regex = re.compile(self.SEP_REGEX)
        self.__initialize(source_language, target_language)
        
    def translate(self, source_sentence: str, source_language: str, target_language: str) -> str:
        try:
            return self.__translation_dict[source_language, target_language, source_sentence]
        except KeyError:
            
            # Replace the \w\n\n match with \w.\n\n
            for match in self.__sep_regex.finditer(source_sentence):
                source_sentence = source_sentence[:match.start()] + \
                                  match.groupdict()["letter"] + ".\n\n" + \
                                  source_sentence[match.end():]
            
            sentences = sent_tokenize(source_sentence, source_language)
            transl = ""
            for sentence in sentences:
                try:
                    transl += \
                        self.__translation_dict[source_language, target_language, sentence] + \
                        " "
                except KeyError:
                    logging.warn(f"Sentence {source_sentence} couldn't be translated")
                    return ""
            return transl[:-1] # Remove las space
    
    def __initialize(self, source_language: str, target_language: str):
        """
        Builds the corpus from the `source_dir` sentences and `target_dir` sentences.
        Both files must be named in a way that by sorting them will yield the 
        corresponding source and target file. 
        
        source_dir: Directory that contains the source target annotation
        target_dir: Directory that contains the source target annotation
        """
        
        source_texts = [(file, file.read_text()) for file in self.source_dir.iterdir()]
        target_texts = [(file, file.read_text()) for file in self.target_dir.iterdir()]
        
        source_texts.sort(key=lambda x: x[0].name)
        target_texts.sort(key=lambda x: x[0].name)

        if len(source_texts) != len(target_texts):
            raise Exception("source_dir and target_dir must have only the source language files with the corresponding target lanuguage files")
        
        for (source_file, source_text), (target_file, target_text) in zip(source_texts, target_texts):
            source_sentences = source_text.split("\n")
            target_sentences = target_text.split("\n")

            if len(source_sentences) != len(target_sentences):
                raise Exception(f"{source_file.name} and {target_file.name} must have the same amount of sentences")

            for source_sentence, target_sentence in zip(source_sentences, target_sentences):
                self.__translation_dict[source_language, target_language, source_sentence] = target_sentence
            
            # Making sentence bigrams
            source_bigrs = [(sentence, source_sentences[i+1]) for i, sentence in enumerate(source_sentences[:-1])]
            target_bigrs = [(sentence, target_sentences[i+1]) for i, sentence in enumerate(target_sentences[:-1])]

            for source_bigr, target_bigr in zip(source_bigrs, target_bigrs):
                self.__translation_dict[source_language, target_language, " ".join(source_bigr)] = " ".join(target_bigr)
                