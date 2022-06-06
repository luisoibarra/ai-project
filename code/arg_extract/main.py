from pathlib import Path
from ..corpus_parser.bret_parser import BretParser


# Calcular un vector contexto global y otro local, basado en una condensación de las n oraciones previas.
# Usar lo anterior como feature

# Feature extraction
# Token: 
# Chunks:
# Word Embedding:

# Neural end-to-end
# - Dependency parsing
# - Sequence Tagging BIO, Codificando features en el tag.
# - NER con relaciones

def feature_extraction():
    path = Path(__file__) / ".." / ".." / "corpus" / "ArgumentAnnotatedEssays-2.0" / "brat-project-final" / "brat-project-final"
    path = path.resolve()
    
    parser = BretParser()
    result = parser.parse_dir(path)
    