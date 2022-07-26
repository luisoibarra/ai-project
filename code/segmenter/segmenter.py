from pathlib import Path
from typing import List, Tuple

SplittedArgumentInfo = Tuple[str,str]

class ArgumentSegmenter:
    
    def extract_arguments_from_file(self, source_file: Path, dest_directory: Path):
        """
        Read a space separated content from `source_file` and create in `dest_directory`
        the .conll and the .txt file of the argumentative split.
        
        source_file: A file tokenized by whitespaces of the text to extract arguments from
        dest_directory: A destination directory for the conll annotated result
        """
        
        content = source_file.read_text()
        argument_info = self.extract_arguments_from_text(content)
        
        conll_dest_file = dest_directory / f"{source_file.name}.conll"
        text_dest_file = dest_directory / f"{source_file.name}.txt"
        with conll_dest_file.open() as file1:
            with text_dest_file.open() as file2:
                for argument, tag in argument_info:
                    # Write Conll data
                    tokens = argument.split(" ")
                    first_tag = "O"
                    next_tag = "O"
                    if tag:
                        first_tag = "B"
                        next_tag = "I"
                    
                    file1.write(f"{tokens[0]}\t{first_tag}\n")

                    for tok in tokens[1:]:
                        file1.write(f"{tok}\t{next_tag}\n")

                    # Write text data
                    file2.write(argument)

    def extract_arguments_from_text(self, text: str) -> List[SplittedArgumentInfo]:
        """
        Split the text by its argumentative units.
        
        text: Text to be splitted
        
        returns: A list of pairs with the component and its tag in the text.
        """
        raise NotImplementedError()

