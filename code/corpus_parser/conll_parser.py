from pathlib import Path
from typing import List, Tuple

import pandas as pd
from .parser import Parser
import re
import logging as log

class ConllParser(Parser):
    
    ANNOTATION = r"^(?P<token_text>[^\s]+)\s(?P<bio_tag>[BIO])-(?P<prop_type>\w+)-(?P<relation_type>\w+)-(?P<relation_distance>-?\d+)\s*$"
    
    def __init__(self) -> None:
        super().__init__((".conll",))
        self.annotation_regex = re.compile(self.ANNOTATION)
        
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
        
        line_parse = []
        
        for i,line in enumerate(content):
            match = self.annotation_regex.match(line)
            if match:
                line_parse.append(match.groupdict())
            else:
                log.warning(f"Line {i} file {file.name}. Match not found: {line}")

        def extract_proposition(propositions: List[dict], start_index=0):
            """
            Extracts the first proposition in `propositions`.
            
            Raise: IndexOutOfRange if no proposition is found
            """
            current = start_index
            # Skip all not beginning tags
            while propositions[current]["bio_tag"] != "B":
                current += 1
            
            # Current in B
            proposition_text = propositions[current]["token_text"]
            current += 1
            
            # Skip all not beginning tags
            while current < len(propositions) and propositions[current]["bio_tag"] == "I":
                proposition_text += " " + propositions[current]["token_text"]
                current += 1
            
            return proposition_text, current
        
        argumentative_units = pd.DataFrame(columns=["prop_id", "prop_type", "prop_init", "prop_end", "prop_text"])
        relations = pd.DataFrame(columns=["relation_id", "relation_type", "prop_id_source", "prop_id_target"])

        current = 0
        accumulative_offset = 0
        while current < len(line_parse):
            proposition, current = extract_proposition(line_parse, current)
            prop_info = line_parse[current-1] # All annotations of the argument are equal 
            prop_id = len(argumentative_units) + 1 # 0 is the root node
            
            argumentative_units = argumentative_units.append({
                "prop_id": prop_id, 
                "prop_type": prop_info["prop_type"],
                "prop_init": accumulative_offset,
                "prop_end": accumulative_offset + len(proposition), 
                "prop_text": proposition,
            }, ignore_index=True)
            
            relations = relations.append({
                "relation_id": len(relations), 
                "relation_type": prop_info["relation_type"],
                "prop_id_source": prop_id, 
                "prop_id_target": prop_id + int(prop_info["relation_distance"]),
            }, ignore_index=True)
        
        return argumentative_units, relations


if __name__ == "__main__":
    base = Path(__file__) / ".." / ".." / "corpus" / "scidtb_argmin_annotations"
    base = base.resolve()

    parser = ConllParser()
    result = parser.parse_dir(base)
    result1, result2 = next(x for x in result.values())
    print(result1.describe())
    print(result2.describe())