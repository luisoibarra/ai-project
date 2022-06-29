from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from .parser import Parser
import re
import logging as log
from nltk.tokenize import word_tokenize

class ConllParser(Parser):
    
    ANNOTATION_REGEX = r"^(?P<token_text>[^\s]+)\s(?P<bio_tag>[BIO])(-(?P<prop_type>\w+))?(-(?P<relation_type>\w+))?(-(?P<relation_distance>-?\d+))?\s*$"
    ANNOTATION_FORMAT = "{tok}\t{bio_tag}-{prop_type}-{relation_type}-{relation_distance}\n"
    
    def __init__(self, *additional_supported_formats) -> None:
        super().__init__((".conll", *additional_supported_formats))
        self.annotation_regex = re.compile(self.ANNOTATION_REGEX)
    
    def parse(self, content:str, file: Optional[Path] = None, **kwargs) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Parse `content` returning DataFrames containing
        the argumentative unit and the relation information.
        
        content: text containing the content to parse
        file: Optional, content's original file
        
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
          
        return: (argumentative_units, relationsm non_argumentative_units)
        """
        
        content = content.splitlines()
        
        line_parse = []
        
        for i,line in enumerate(content):
            match = self.annotation_regex.match(line)
            if match:
                line_parse.append(match.groupdict())
            else:
                if file:
                    log.warning(f"Line {i} file {file.name}. Match not found: {line}")
                else:
                    log.warning(f"Line {i}. Match not found: {line}")

        def extract_proposition(propositions: List[dict], start_index=0):
            """
            Extracts the first proposition in `propositions`.
            
            Raise: IndexOutOfRange if no proposition is found
            """
            current = start_index
            
            def extract_language_tag(word):
                """
                Check if the word is annotated with a language tag i.e. [_es, _en, _de]
                and return the unannotated word.
                """
                if len(word) > 3 and word[-3] == "_":
                    return word[:-3]
                return word

            if propositions[current]["bio_tag"] == "O":
                proposition_text = extract_language_tag(propositions[current]["token_text"])
                current += 1

                # Join all tokens
                while current < len(propositions) and propositions[current]["bio_tag"] == "O":
                    proposition_text += " " + extract_language_tag(propositions[current]["token_text"])
                    current += 1
            else:
                if propositions[current]["bio_tag"] != "B":
                    if file:
                        log.warning(f"File {file.name}. Proposition '{proposition}' doesn't start with a B")
                    else:
                        log.warning(f"Proposition '{proposition}' doesn't start with a B")
                
                # Current should be B
                proposition_text = extract_language_tag(propositions[current]["token_text"])
                current += 1
                
                # Join all tokens
                while current < len(propositions) and propositions[current]["bio_tag"] == "I":
                    proposition_text += " " + extract_language_tag(propositions[current]["token_text"])
                    current += 1
                
            return proposition_text, current
        
        argumentative_units = pd.DataFrame(columns=["prop_id", "prop_type", "prop_init", "prop_end", "prop_text"])
        non_argumentative_units = pd.DataFrame(columns=["prop_init", "prop_end", "prop_text"])
        relations = pd.DataFrame(columns=["relation_id", "relation_type", "prop_id_source", "prop_id_target"])

        current = 0
        accumulative_offset = 0
        while current < len(line_parse):
            
            proposition, current = extract_proposition(line_parse, current)
            prop_info = line_parse[current-1] # All annotations of the argument are equal 
            prop_id = len(argumentative_units) + 1 # 0 is the root node
            
            if prop_info["bio_tag"] == "O":
                non_argumentative_units = non_argumentative_units.append({
                    "prop_init": accumulative_offset,
                    "prop_end": accumulative_offset + len(proposition), 
                    "prop_text": proposition,
                }, ignore_index=True)
            else:
                argumentative_units = argumentative_units.append({
                    "prop_id": prop_id, 
                    "prop_type": prop_info["prop_type"],
                    "prop_init": accumulative_offset,
                    "prop_end": accumulative_offset + len(proposition), 
                    "prop_text": proposition,
                }, ignore_index=True)
                
                if None not in [prop_info["relation_type"], prop_info["relation_distance"]]:
                    relations = relations.append({
                        "relation_id": len(relations), 
                        "relation_type": prop_info["relation_type"],
                        "prop_id_source": prop_id, 
                        "prop_id_target": prop_id + int(prop_info["relation_distance"]),
                    }, ignore_index=True)
            
            accumulative_offset += len(proposition) + 1 # Extra separator when rebuilding text
        
        return argumentative_units, relations, non_argumentative_units
        

    def from_dataframes(self, dataframes: Dict[str, Tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]], language="english", get_tags=False, **kwargs) -> Dict[str, Tuple[Union[str, List[Dict[str,Union[str,int]]]],str]]:
        """
        Creates a CONLL annotated corpus representing the received DataFrames. 
        
        dataframes: The result from calling a parse function in any Parser class
        the keys aren't important, so a mock key can be passed.
        language: Language for tokenization process
        get_tags: If true, returns the tags instead of the annotated text
        
        returns: CONLL annotated string or CONLL annotations, Raw text
        """
        
        results = {}
        default_gap = " "
                
        for file_path_str, (argumentative_units, relations, non_argumentative_units) in dataframes.items():

            result = ""
            tags_info = []
            all_units = argumentative_units.append(non_argumentative_units, sort=True)
            all_units.sort_values(by="prop_init", inplace=True)
            all_units = all_units.reindex(columns=["prop_id", "prop_type", "prop_init", "prop_end", "prop_text"])
            max_length = all_units["prop_end"].max()
            
            text = default_gap*max_length
            
            for index, (prop_id, prop_type, prop_init, prop_end, prop_text) in all_units.iterrows():
                text = text[:prop_init] + prop_text + text[prop_end:]
                prop_tokens = word_tokenize(prop_text, language=language)
                if pd.notna(prop_type):
                    # It's the begining of a proposition
                    for i,tok in enumerate(prop_tokens):

                        bio_tag = "B" if i == 0 else "I"
                        relation = relations[relations["prop_id_source"] == prop_id]
                        if len(relation) == 1:
                            relation_type = relation["relation_type"].values[0]
                            relation_distance = relation["prop_id_target"].values[0] - relation["prop_id_source"].values[0]
                        elif len(relation) == 0:
                            relation_type = "none"
                            relation_distance = "none"
                        else:
                            relation_type = "none"
                            relation_distance = - relation["prop_id_source"].values[0]
                            log.warning(f"File {file_path_str}. Relation '{prop_text}'' with more than one out edge")
                        
                        tags_info.append({
                                "tok": tok,
                                "bio_tag": bio_tag,
                                "prop_type": prop_type,
                                "relation_type": relation_type,
                                "relation_distance": relation_distance
                        })
                        to_write = self.ANNOTATION_FORMAT.format_map(tags_info[-1])
                        to_write = to_write.replace("-none", "") # Remove unnecesary labels
                        result += to_write
                else:
                    # Out of proposition
                    for tok in prop_tokens:
                        # Fill the gap with O until the proposition is found
                        tags_info.append({
                            "tok": tok,
                            "bio_tag": "O",
                            "prop_type": "none",
                            "relation_type": "none",
                            "relation_distance": "none"
                        })
                        to_write = self.ANNOTATION_FORMAT.format_map(tags_info[-1])
                        to_write = to_write.replace("-none", "") # Remove unnecesary labels
                        result += to_write
            
            if get_tags:
                results[file_path_str] = tags_info, text
            else:
                results[file_path_str] = result, text
        
        return results

    def get_text_from_annotation(self, annotations: List[Dict[str, Union[str,int]]]) -> str:
        """
        Maps the anotation to its associated text representation.
        
        annotations: List containig the dictionary that holds the information about the tag
        
        returns: The annotated text representation
        """
        text = ""
        for annotation in annotations:
            to_write = self.ANNOTATION_FORMAT.format_map(annotation)
            to_write = to_write.replace("-none", "") # Remove unnecesary labels
            text += to_write
        return text
