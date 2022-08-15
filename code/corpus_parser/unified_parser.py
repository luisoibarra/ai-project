import re
from corpus_parser.bret_parser import BretParser
from corpus_parser.conll_parser import ConllParser
import logging
from pathlib import Path
from typing import Dict, Iterable, Optional

from .parser import AnnotatedRawTextInfo, ArgumentationInfo, Parser


class UnifiedParser(Parser):
    """
    Automatically selects te propper way to parse a file.
    The selection can be manual by setting the selected_parser property or
    automatic by parsing a file.
    """
    
    
    def __init__(self, accepted_files: Iterable[str] = (".conll", ".ann")) -> None:
        super().__init__(accepted_files)
        self.conll_parser = ConllParser()
        self.bret_parser = BretParser()
        self.selected_parser = None
    
    def __get_parser(self, content: str, file: Optional[Path] = None) -> Parser:
        """
        Return the parser to parse the given content
        """
        if file is not None:
            if file.suffix == ".conll":
                return self.conll_parser
            if file.suffix == ".ann":
                return self.bret_parser
            raise Exception(f"Couldn't guess parser for file {file}")
        line = content.splitlines()[0]
        if self.bret_parser.argumentative_unit_regex.match(line) \
            or self.bret_parser.relation_regex.match(line):
            return self.bret_parser
        if self.conll_parser.annotation_regex.match(line):
            return self.conll_parser
        raise Exception(f"Couldn't guess parser for line {line}")
        
    def parse(self, content: str, file: Optional[Path] = None, **kwargs) -> ArgumentationInfo:
        """
        Parse `content` returning DataFrames containing
        the argumentative unit and the relation information.
        
        content: text containing the content to parse
        file: Content's original file
        
        argumentative_units columns: 
          - `prop_id` Proposition ID inside the document
          - `prop_type` Proposition type
          - `prop_init` When the proposition starts in the original text
          - `prop_end` When the proposition ends in the original text
          - `prop_text` Proposition text
          
        relations columns:
          - `relation_id` Relation ID inside the document
          - `relation_type` Relation type
          - `prop_id_source` Relation's source proposition id 
          - `prop_id_target` Relation's target proposition id
          
        non_argumentative_units columns:
          - `prop_init` When the proposition starts in the original text
          - `prop_end` When the proposition ends in the original text
          - `prop_text` Proposition text
          
        return: (argumentative_units, relations, non_argumentative_units)
        """
        if not self.selected_parser:
            self.selected_parser = self.__get_parser(content, file)
        return self.selected_parser.parse(content, file=file, **kwargs)

    def from_dataframes(self, dataframes: Dict[str, ArgumentationInfo], language="english", **kwargs) -> Dict[str, AnnotatedRawTextInfo]:
        """
        Creates a Bret annotated corpus representing the received DataFrames. 
        
        dataframes: The result from calling a parse function in any Parser class
        the keys aren't important, so a mock key can be passed.
        language: Language for tokenization process
        
        returns: Bret annotated string, Raw text
        """
        if not self.selected_parser:
            raise Exception("No parser has been selected. Parse a file or set selected_parser field to a Parser")
        return self.selected_parser.from_dataframes(dataframes, language, **kwargs)