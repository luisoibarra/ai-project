
from projector.aligner import Aligner
from corpus_parser.conll_parser import ConllParser
from typing import Dict, List, Union
import logging as log

from pathlib import Path

class Projector:
    """
    Abstract class for projection algorithm
    """
    
    def project_dir(self, annotation_dir: Path, sentence_alignment_dir: Path, bidirectional_alignment_dir: Path,
                    export_dir: Path, **kwargs):
        """
        Creates annotated corpus in `export_dir` containing the projected labels from `annotation_dir`files using
        the sentence alignments from `sentence_alignment_dir` and the bidiectional alignment from `bidirectional_alignment_dir`
        
        annotation_dir: Path that contains the .conll files with the annotations
        sentence_alignment_dir: Path that contains the .align files with the sentence alignments
        bidirectional_alignment_dir: Path that contains the .bidirectional files.
        export_dir: Path to export the projected files in `dest_language`.
        
        """
        
        annotated_files = [file for file in annotation_dir.iterdir() if file.name.endswith(".conll")]
        sentences_aligned_files = [file for file in sentence_alignment_dir.iterdir() if file.name.endswith(".align")]
        bidirectional_alignments_files = [file for file in bidirectional_alignment_dir.iterdir() if file.name.endswith(".bidirectional")]
        
        parser = ConllParser()
        
        for annotated_file in annotated_files:
            
            try:
                sentence_aligned_file = [
                    file for file in sentences_aligned_files 
                        if annotated_file.name in file.name and file.name.endswith(".align")
                ][0] # Find the associated .align file
            except IndexError as e:
                raise IndexError(f"No aligned sentence found for {annotated_file}. Expected like {annotated_file}.align")
            try:
                bidirectional_alignment_file = [
                    file for file in bidirectional_alignments_files 
                        if annotated_file.name in file.name and file.name.endswith(".bidirectional")
                ][0] # Find the associated .bidirectional file
            except IndexError as e:
                raise IndexError(f"No bidirectional alignment found for {annotated_file}. Expected like {annotated_file}.bidirectional")
            
            # Reading files. BIO annotations, Sentence alignment, Bidirectional alignment
            annotation_df = parser.parse_file(annotated_file)
            key = str(annotated_file)
            annotation = parser.from_dataframes({key : annotation_df }, get_tags=True, **kwargs)[key][0]
            sentences_aligned = sentence_aligned_file.read_text().splitlines()
            bidirectional_alignments = bidirectional_alignment_file.read_text().splitlines()
            
            # Checking that the sentence amount is the same
            if len(sentences_aligned) != len(bidirectional_alignments):
                raise Exception(f"Sentences aligned and bidirectional aligments amount doesn't match for {annotated_file}")
            
            file_target_projection = []
            
            current_annotation_offset = 0
            
            for sentence_aligned, bidirectional_alignment in zip(sentences_aligned, bidirectional_alignments):
                # Reading and parsing text
                source_sentence, target_sentence = sentence_aligned.split(kwargs.get("separator", Aligner.SEPARATOR))
                source_sentence_tokens, target_sentence_tokens = source_sentence.split(" "), target_sentence.split(" ")
                bidirectional_alignment_dict = self._parse_bidirectional_alignment(bidirectional_alignment)
                
                # Updating offset
                next_annotation_offset = current_annotation_offset + len(source_sentence_tokens)
                
                current_annotations = annotation[current_annotation_offset:next_annotation_offset]
                
                # Sanity check. 
                assert len(source_sentence_tokens) == len(current_annotations), "Tokens and tags amounts aren't equal"
                assert tuple(source_sentence_tokens) == tuple(tag_info["tok"] for tag_info in current_annotations), "Tokens and tags lexeme aren't equal"

                
                target_projection = self.project_sentence(source_sentence_tokens, target_sentence_tokens,
                                                          bidirectional_alignment_dict, current_annotations)
                file_target_projection.extend(target_projection)
                
                current_annotation_offset = next_annotation_offset
            
            if current_annotation_offset != len(annotation):
                raise Exception(f"Missing annotations to be used in {annotated_file}: {annotation[current_annotation_offset:]}")
            
            if not export_dir.exists():
                export_dir.mkdir()
            
            target_annotated_file = export_dir / (annotated_file.name + ".exported.conll")
            
            final_projection_text = parser.get_text_from_annotation(file_target_projection)
            
            target_annotated_file.write_text(final_projection_text)
            
    def project_sentence(self, sentence_source_tokens:List[str], sentence_target_tokens:List[str],
                         alignment:Dict[int, List[int]], tags_info: List[Dict[str,Union[str,int]]]) -> List[Dict[str,Union[str,int]]]:
        """
        Projects the `sentence_source_tokens`'s annotations annotated in `tags_info` into `sentence_target_tokens`
        using the bidirectional `alignment` information.
        
        sentence_source_tokens: Tokens of the sentence in source language.
        sentence_target_tokens: Tokens of the `sentence_source` translated into the target language 
        alignment: Bidirectional alignment information
        tags_info: sentence_source's annotations
        
        returns: The projected tags in the target language
        """
        raise NotImplementedError()
        
    def _parse_bidirectional_alignment(self, bidirectional_alignment: str) -> Dict[int, List[int]]:
        """
        Parse the single line `bidirectional_alignment` in .bidirectional format
        
        bidirectional_alignment: Sinlge line of a .bidirectional format file. i.e. "1-2 2-1 3-3 4-3"
        
        returns: A dictionary mapping the index to the respective index in the target languages
        """
        alignments = bidirectional_alignment.split(" ")
        
        # Parsing alignments: id1-id2 id3-id4 ...
        alignment_dict: Dict[int, List[int]] = {}
        for align_tuple in alignments:
            source, target = tuple(map(int, align_tuple.split("-")))
            if source not in alignment_dict:
                alignment_dict[source] = []
            alignment_dict[source].append(target)
        
        return alignment_dict
    
class SelfLanguageProjector(Projector):
    """
    Projector that only takes into account the source language and performs a self projection.
    
    Its main purpose is testing.
    """
    
    def project_sentence(self, sentence_source_tokens: List[str], sentence_target_tokens: List[str], 
                         alignment: Dict[int, List[int]], tags_info: List[Dict[str, Union[str, int]]]) -> List[Dict[str, Union[str, int]]]:
        assert len(sentence_source_tokens) == len(tags_info), "Tokens and tags amounts aren't equal"
        assert tuple(sentence_source_tokens) == tuple(tag_info["tok"] for tag_info in tags_info), "Tokens and tags lexeme aren't equal"
        return tags_info
    