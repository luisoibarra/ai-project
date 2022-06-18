

class Translator:

    def translate(self, source_sentence: str, source_language:str, target_language: str) -> str:
        """
        Translate given `sentence` in `source_language` into `target_language`
        
        sentence: Sentence to translate
        source_language: Language of given sentence
        target_language: Language to translate the sentence
        
        returns: The translated sentence
        """
        raise NotImplementedError()


class SelfTranslator(Translator):
    
    def translate(self, source_sentence: str, source_language:str, target_language: str) -> str:
        return source_sentence