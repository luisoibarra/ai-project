from pathlib import Path
from typing import List
import tensorflow as tf
from tensorflow import keras
from .segmenter import ArgumentSegmenter, SplittedArgumentInfo


class TensorflowArgumentSegmenter(ArgumentSegmenter):
    
    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self._load_model()
    
    def _load_model(self):
        self.model = keras.models.load_model(str(self.model_path.resolve()))
        self.index_to_tag = self.model.vectorizer_tags.get_vocabulary()

    def _decode_tags(self, tags_list):
        result = []
        for tags in tags_list:
            result.append([self.index_to_tag[i] for i in tags])
        return result

    def extract_arguments_from_text(self, text: str) -> List[SplittedArgumentInfo]:
        data = tf.constant([text])
        encoded_tags = self.model(data)
        decoded_tags = self._decode_tags(encoded_tags)
        return list(zip(text.split(" "), decoded_tags[0]))
