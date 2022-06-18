

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, Future, wait

import pandas as pd

class Parser:
    
    def __init__(self, accepted_files: Iterable[str]) -> None:
        """
        accepted_files: List of files extensions to be read
        """
        self.accepted_files = tuple(accepted_files)
        
    def _should_read_file(self, file: Path):
        """
        Returns if a file should be read as a corpus file
        """
        return file.is_file() and file.name.endswith(self.accepted_files)

    def parse_dir(self, corpus_path: Path, **kwargs) -> Dict[str,Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]:
        """
        Parse the file
        
        corpus_path: Base corpus address
        
        return: A dictionary mapping file address to its information
        """
        
        results = {}
        futures: List[Future] = []
        max_worker = 20
        
        files = [file for file in corpus_path.iterdir()]
        batch = len(files)//max_worker
        if batch == 0: batch = 1 # At least one must be the batch size
        
        def read(slice):
            for file in files[batch*slice:batch*(slice+1)]:
                if self._should_read_file(file):
                    result = self.parse_file(file, **kwargs)
                    results[str(file)] = result
        
        with ThreadPoolExecutor(max_workers=max_worker) as exe:
            for i in range(max_worker):
                futures.append(exe.submit(read, i))
                # read(i)
        wait(futures)
        exceptions = [future for future in futures if future.exception()]
        
        if exceptions:
            raise Exception(exceptions)
        
        return results

    def parse_file(self, file: Path, **kwargs) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Parse the content of `file` returning two DataFrames containing
        the argumentative unit and the relation information.
        
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
        return self.parse(file.read_text(), file, **kwargs)
    
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
          
        return: (argumentative_units, relations, non_argumentative_units)
        """
        raise NotImplementedError()

    def from_dataframes(self, dataframes: Dict[str, Tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]], language="english", **kwargs) -> Dict[str, Tuple[str,str]]:
        """
        Creates file with annotated corpus representing the received DataFrames. 
        
        dataframes: The result from calling a parse function in any Parser class
        the keys aren't important, so a mock key can be passed.
        language: Language for tokenization process
        
        returns: Annotated string, Raw entire text
        """
        raise NotImplementedError()
        
    def export_from_dataframes(self, dest_address: Path, dataframes: Dict[str, Tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]], **kwargs):
        """
        Saves the corpus to into dest_address, converting the dataframe version into the corresponding representation.
        
        dest_address: Path where to save the corpus. May not exist
        dataframes: DataFrame representation of the corpus
        """
        representation = self.from_dataframes(dataframes, **kwargs)
        Parser.export_corpus_from_files(dest_address, representation, **kwargs)
    
    @staticmethod
    def export_corpus_from_files(dest_address: Path, files: Dict[str,Tuple[str,str]], suffix: str = ".conll"):
        """
        Saves the corpus into dest_address. The files will be named after its key.
        
        dest_addres: Path where to save the corpus. May not exist
        files: Maps file address or file name to its corpus representation and its full text.
        """
        if not dest_address.is_dir():
            dest_address.mkdir()
            
        for filedir, (annotated_text, raw_text) in files.items():
            name = Path(filedir).name
            if suffix: name += suffix
            dest = dest_address / name
            dest.write_text(annotated_text)
            dest = dest_address / (name + ".txt")
            dest.write_text(raw_text)
