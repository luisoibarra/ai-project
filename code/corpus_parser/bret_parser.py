from pathlib import Path
import re
from typing import Tuple
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
        
    def parse(self, file: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Parse the content of `file` returning two DataFrames containing
        the argumentative unit and the relation information.
        
        argumentative_units columns: 
          - `prop_id` Proposition ID inside the document
          - `prop_type` Proposition type
          - `prop_init` When the proposition starts in the original text
          - `prop_end` When the proposition ends in the original text
          
        relations columns:
          - `relation_id` Relation ID inside the document
          - `relation_type` Relation type
          - `prop_id_source` Relation's source proposition id 
          - `prop_id_target` Relation's target proposition id
          
        return: (argumentative_units, relations)
        """
        
        content = file.read_text().splitlines()
        
        argumentative_units = pd.DataFrame(columns=["prop_id", "prop_type", "prop_init", "prop_end", "prop_text"])
        relations = pd.DataFrame(columns=["relation_id", "relation_type", "prop_id_source", "prop_id_target"])
        
        for i,line in enumerate(content):
            argument_match = self.argumentative_unit_regex.match(line)
            if argument_match:
                argumentative_units = argumentative_units.append(argument_match.groupdict(), ignore_index=True)
                continue
            relation_match = self.relation_regex.match(line)
            if relation_match:
                relations = relations.append(relation_match.groupdict(), ignore_index=True)
                continue
            log.warning(f"Line {i} file {file.name}. Match not found: {line}")
        
        return argumentative_units, relations

if __name__ == "__main__":
    base = Path(__file__) / ".." / ".." / "corpus" / "ArgumentAnnotatedEssays-2.0" / "brat-project-final" / "brat-project-final"
    base = base.resolve()

    parser = BretParser()
    result = parser.parse_dir(base)
    result1, result2 = next(x for x in result.values())
    print(result1.describe())
    print(result2.describe())