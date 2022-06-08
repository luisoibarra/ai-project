from pathlib import Path
import re
from typing import Optional, Tuple
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

    def parse(self, content:str, file: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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
          
        return: (argumentative_units, relationsm non_argumentative_units)
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
                
                argument_dict["prop_init"] = int(argument_dict["prop_init"])
                argument_dict["prop_end"] = int(argument_dict["prop_end"])
                
                argumentative_units = argumentative_units.append(argument_dict, ignore_index=True)
                continue
            relation_match = self.relation_regex.match(line)
            if relation_match:
                relations = relations.append(relation_match.groupdict(), ignore_index=True)
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

if __name__ == "__main__":
    base = Path(__file__) / ".." / ".." / "corpus" / "ArgumentAnnotatedEssays-2.0" / "brat-project-final" / "brat-project-final"
    base = base.resolve()

    parser = BretParser()
    result = parser.parse_dir(base)
    result1, result2, result3 = next(x for x in result.values())
    print(result1.describe())
    print(result2.describe())
    print(result3.describe())