from cmath import nan
from pathlib import Path
import re
from typing import Dict, Optional, Tuple
from .parser import Parser
import pandas as pd
import logging as log

class BretParser(Parser):
    """
    Parse files annotated with BRET tool. The files must end in .ann for the parser to work out of the box.
    """
    
    # Regex using named groups
    ARGUMENTATIVE_UNIT = r"^T(?P<prop_id>\d+)\s(?P<prop_type>\w+)\s(?P<prop_init>\d+)\s(?P<prop_end>\d+)\s(?P<prop_text>.+)\s*$" # Verify if \n are stripped
    RELATION = r"^R(?P<relation_id>\d+)\s(?P<relation_type>\w+)\sArg1:T(?P<prop_id_source>\d+)\sArg2:T(?P<prop_id_target>\d+)\s*$" # Verify if \n are stripped
    
    def __init__(self) -> None:
        super().__init__((".ann",))
        self.argumentative_unit_regex = re.compile(self.ARGUMENTATIVE_UNIT)
        self.relation_regex = re.compile(self.RELATION)

    def parse(self, content:str, file: Path, **kwargs) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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
        content_lines = content.splitlines()
        original_text_file = (file / ".." / ((".".join(file.name.split('.')[:-1]) if "." in file.name else file.name) + ".txt")).resolve()
        original_text = original_text_file.read_text()

        argumentative_units = pd.DataFrame(columns=["prop_id", "prop_type", "prop_init", "prop_end", "prop_text"])
        non_argumentative_units = pd.DataFrame(columns=["prop_init", "prop_end", "prop_text"])
        relations = pd.DataFrame(columns=["relation_id", "relation_type", "prop_id_source", "prop_id_target"])
        
        for i,line in enumerate(content_lines):
            argument_match = self.argumentative_unit_regex.match(line)
            if argument_match:
                argument_dict = argument_match.groupdict()
                
                argument_dict["prop_id"] = int(argument_dict["prop_id"])
                argument_dict["prop_init"] = int(argument_dict["prop_init"])
                argument_dict["prop_end"] = int(argument_dict["prop_end"])
                
                argumentative_units = argumentative_units.append(argument_dict, ignore_index=True)
                continue
            relation_match = self.relation_regex.match(line)
            if relation_match:
                argument_dict = relation_match.groupdict()
                
                argument_dict["relation_id"] = int(argument_dict["relation_id"])
                argument_dict["prop_id_source"] = int(argument_dict["prop_id_source"])
                argument_dict["prop_id_target"] = int(argument_dict["prop_id_target"])
                
                relations = relations.append(argument_dict, ignore_index=True)
                continue
            log.warning(f"Line {i} file {file.name}. Match not found: {line}")
        
        argumentative_units.sort_values(by="prop_init", inplace=True)
        
        last_match = 0
        for _, (_, _, prop_init, prop_end, _) in argumentative_units.iterrows():
            if last_match < prop_init:
                # Non argumentative gap
                non_argumentative_units = non_argumentative_units.append({
                    "prop_init":last_match,
                    "prop_end":prop_init,
                    "prop_text":original_text[last_match:prop_init],
                }, ignore_index=True)
                # last_match = prop_end
            elif last_match == prop_init:
                # Arguments together
                pass
            else:
                log.warning("Inconsistency gap")
            last_match = prop_end
        
        if last_match != len(original_text):
            # If text ends in a non argumentative gap
            non_argumentative_units = non_argumentative_units.append({
                "prop_init":last_match,
                "prop_end":len(original_text),
                "prop_text":original_text[last_match:len(original_text)],
            }, ignore_index=True)
        
        return argumentative_units, relations, non_argumentative_units

    def from_dataframes(self, dataframes: Dict[str, Tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]], language="english", **kwargs) -> Dict[str, Tuple[str,str]]:
        """
        Creates a Bret annotated corpus representing the received DataFrames. 
        
        dataframes: The result from calling a parse function in any Parser class
        the keys aren't important, so a mock key can be passed.
        language: Language for tokenization process
        
        returns: Bret annotated string, Raw text
        """
        
        results = {}
        default_gap = " "

        argumentative_format = "T{prop_id}\t{prop_type} {prop_init} {prop_end}\t{prop_text}\n"
        relation_format = "R{relation_id}\t{relation_type} Arg:T{prop_id_source} Arg:T{prop_id_target}\n"
        
        for file_path_str, (argumentative_units, relations, non_argumentative_units) in dataframes.items():

            result = ""
            all_units = argumentative_units.append(non_argumentative_units, sort=True)
            all_units.sort_values(by="prop_init", inplace=True)
            all_units = all_units.reindex(columns=["prop_id", "prop_type", "prop_init", "prop_end", "prop_text"])
            max_length = all_units["prop_end"].max()
            
            text = default_gap*max_length
            
            for index, (prop_id, prop_type, prop_init, prop_end, prop_text) in all_units.iterrows():
                text = text[:prop_init] + prop_text + text[prop_end:]
                if pd.notna(prop_id) and pd.notna(prop_type):
                    to_write = argumentative_format.format_map({
                        "prop_id": prop_id,
                        "prop_type": prop_type,
                        "prop_init": prop_init,
                        "prop_end": prop_end,
                        "prop_text": prop_text
                    })
                    result += to_write
            
            relations = relations.reindex(columns=["relation_id", "relation_type", "prop_id_source", "prop_id_target"])
            
            for index, (relation_id, relation_type, prop_id_source, prop_id_target) in relations.iterrows():
                to_write = relation_format.format_map({
                    "relation_id": relation_id,
                    "relation_type": relation_type,
                    "prop_id_source": prop_id_source,
                    "prop_id_target": prop_id_target,
                })
                result += to_write
            
            results[file_path_str] = result, text
        
        return results
    