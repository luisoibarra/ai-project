
from pathlib import Path
import pandas as pd
import nltk

all_words = set()
all_tags = set()
all_chars = set()

def convert_to_tuples(data:Path, bioes=True, meta_tags_level=99, meta_tags_separator="-"):
    tags = []
    current_paragraph_tags = []
    current_paragraph_words = []
    for line in data.read_text().splitlines():
        if not line: # Empty line dataset
            if bioes:
                current_paragraph_tags = convert_bio_to_bioes(current_paragraph_tags)
            all_tags.update(current_paragraph_tags) 
            tags.append([x for x in zip(current_paragraph_words, current_paragraph_tags)])
            current_paragraph_tags = []
            current_paragraph_words = []
            continue
        word, annotation = line.split("\t")

        if len(word) >= 3 and word[-3] == "_": # word with _LN tag
            word = word[:-3]

        all_words.add(word)
        all_chars.update(word)

        tag = meta_tags_separator.join(annotation.split(meta_tags_separator)[:meta_tags_level+1])
        current_paragraph_tags.append(tag)
        current_paragraph_words.append(word)
    if current_paragraph_words:
        if bioes:
            current_paragraph_tags = convert_bio_to_bioes(current_paragraph_tags)
        all_tags.update(current_paragraph_tags) 
        tags.append([x for x in zip(current_paragraph_words, current_paragraph_tags)])
    return tags

def convert_bio_to_bioes(bio_tags: list):
    bioes_tags = []
    current_entity_tags = []
    for full_tag in bio_tags:
        tag = full_tag[0]
        meta = full_tag[1:]
        if tag == "O":
            if len(current_entity_tags) == 0:
                bioes_tags.append("O" + meta) # Empty current entity and outside
            elif len(current_entity_tags) == 1:
                last_meta = current_entity_tags[-1][1:]
                bioes_tags.append("S" + last_meta) # Single tag entity and outside
                bioes_tags.append("O" + meta) # Add current tag
                current_entity_tags.clear()
            else:
                last_meta = current_entity_tags[-1][1:]
                current_entity_tags[-1] = "E" + last_meta # Multiple tag entity and outside
                bioes_tags.extend(current_entity_tags) # Add all entity tags
                bioes_tags.append("O" + meta) # Add current tag
                current_entity_tags.clear()
        elif tag == "B":
            if len(current_entity_tags) == 0:
                current_entity_tags.append("B" + meta) # Empty current entity and begin a new one
            elif len(current_entity_tags) == 1:
                last_meta = current_entity_tags[-1][1:]
                bioes_tags.append("S" + last_meta) # Sinlge tag entity and begining
                current_entity_tags.clear()
                current_entity_tags.append("B" + meta) # New current entity
            else:
                last_meta = current_entity_tags[-1][1:]
                current_entity_tags[-1] = "E" + last_meta # Multiple tag entity and begin
                bioes_tags.extend(current_entity_tags) # Add all entity tags
                current_entity_tags.clear()
                current_entity_tags.append("B" + meta) # New current entity
        elif tag == "I":
            if len(current_entity_tags) == 0:
                raise Exception("Invalid BIO format, I tag can be at the begining of a segment")
            else:
                current_entity_tags.append("I" + meta) # Continue the entity
        else:
            raise Exception(f"Unsupported {tag} in BIO tagset")

    if len(current_entity_tags) == 1: # Resiual tags
        meta = current_entity_tags[0][1:]
        bioes_tags.append("S" + meta) # Single tag entity and outside
    elif len(current_entity_tags) > 1:
        meta = current_entity_tags[-1][1:]
        current_entity_tags[-1] = "E" + meta # Multiple tag entity and outside
        bioes_tags.extend(current_entity_tags)
  
    return bioes_tags

def build_df(tuples):
    return pd.DataFrame({
        "Paragraph": [i for i,sentence in enumerate(tuples) for _ in sentence],
        "Tag": [tag for sentence in tuples for word, tag in sentence],
        "Word": [word for sentence in tuples for word, tag in sentence],
    })

def export(conll_file: Path, dest_sentence_file: Path, dest_tag_file: Path, language: str="english", meta_tags_level=99, meta_tags_separator="-"):
    """
    Creates from `conll_file` two files, `dest_sentence_file` and 
    `dest_tag_file`, containing the sentences splitted by `nltk` 
    and its corresponding tags respectively. In each file the tokens
    are separated with a blank space.
    
    conll_file: Original conll file
    dest_sentence_file: File containing the sentences.
    dest_tag_file: File containing the tags.
    with_meta_tags: If the output should conserve the meta tags
    """
    
    conll_paragraph_tuples = convert_to_tuples(conll_file, meta_tags_level=meta_tags_level, meta_tags_separator=meta_tags_separator)

    dest_sentence_content = []
    dest_tag_content = []
    current_sentence = []
    current_tags = []
    token_transforms = {
        "``": ['"', "''"],
        "''": '"'
    }
    for sentence_tuples in conll_paragraph_tuples:
        current_sentence = [word for word, _ in sentence_tuples]
        current_tags = [tag for _, tag in sentence_tuples]
        
        sentences = nltk.sent_tokenize(" ".join(current_sentence), language=language)
        current_tag_index = 0
        current_word_index = 0
        for sent in sentences:
            current_word: str = current_sentence[current_word_index]
            current_tag: str = current_tags[current_tag_index]
            toks = nltk.word_tokenize(sent, language=language)
            dest_sentence_content.append([])
            dest_tag_content.append([])
            for j, tok in enumerate(toks, 1):
                if not current_word.startswith(tok):
                    temp_toks = token_transforms.get(tok, [])
                    if not any(current_word.startswith(temp_tok) for temp_tok in temp_toks):
                        # Add exceptions here
                        start_exceptions = {
                            '"': ["????", "``"],
                        }
                        if not (current_word in start_exceptions and \
                            tok in start_exceptions[current_word]):
                            assert False
                    else:
                        tok = [temp_tok for temp_tok in temp_toks if current_word.startswith(temp_tok)][0]
                        
                current_word = current_word[len(tok):]
                dest_sentence_content[-1].append(tok)
                dest_tag_content[-1].append(current_tag)
                if not current_word:
                    current_word_index += 1
                    current_tag_index += 1
                    if j < len(toks):
                        current_word = current_sentence[current_word_index]
                        current_tag = current_tags[current_tag_index]
        
        assert current_tag_index == len(current_tags)
        assert current_word_index == len(current_sentence)
        assert current_tag_index == current_word_index
        current_sentence.clear()
        current_tags.clear()
    
    dest_sentence_file.write_text("\n".join(" ".join(sentence) for sentence in dest_sentence_content))
    dest_tag_file.write_text("\n".join(" ".join(tags) for tags in dest_tag_content))

def export_vocabs(base_path: Path, all_words, all_chars, all_tags):
    
    with (base_path / 'vocab.words.txt').open('w') as f:
        for w in sorted(all_words):
            f.write(f'{w}\n')
    with (base_path / 'vocab.chars.txt').open('w') as f:
        for w in sorted(all_chars):
            f.write(f'{w}\n')
    with (base_path / 'vocab.tags.txt').open('w') as f:
        for w in sorted(all_tags):
            f.write(f'{w}\n')

def export_from_directory(source_directory: Path, dest_sent_file: Path, dest_tag_file: Path, language: str="english", meta_tags_level=99, meta_tags_separator="-"):
    temp_sent_file = Path("tempsentence16916312639")
    temp_tag_file = Path("temptag16916312639")
    temp_sent_file.touch()
    temp_tag_file.touch()
    
    dest_sent_file.touch()
    dest_tag_file.touch()
    
    with dest_sent_file.open("w") as dest_sent:
        with dest_tag_file.open("w") as dest_tag:
            for file in source_directory.iterdir():
                if file.suffix == ".conll":
                    export(file, temp_sent_file, temp_tag_file, language, meta_tags_level, meta_tags_separator)
                    dest_sent.write(temp_sent_file.read_text().replace("\n", " "))
                    dest_tag.write(temp_tag_file.read_text().replace("\n", " "))
                    dest_sent.write("\n")
                    dest_tag.write("\n")
    
    temp_sent_file.unlink()
    temp_tag_file.unlink()

# Base data directory
DATA_DIR = Path(__file__, "..", "..", "data").resolve()

# Language
LANGUAGE = "english"

# Level of annotation to get: 0: BIOES, 1: BIOES-OtherTag, 2: BIOES-Tag1-Tag2, ...
META_TAGS_LEVEL = 1

META_TAG_SEPARATOR = "-"

def export_files():
    # Destiny data directory
    SEGMENTER_DATA_DIR = Path(__file__, "..", "..", "..", "notebook", "data", "english_no_meta_tags").resolve()

    # Source data directory
    STAGE_DIR = DATA_DIR / "corpus" / "Org_PE_english"

    # Train Block
    train_file = STAGE_DIR / "train_PE.en"
    train_dest_sent_file = SEGMENTER_DATA_DIR / "train.words.txt"
    train_dest_tag_file = SEGMENTER_DATA_DIR / "train.tags.txt"
    export(train_file, train_dest_sent_file, train_dest_tag_file, language=LANGUAGE, with_meta_tags=META_TAGS_LEVEL)

    # Test Block
    testa_file = STAGE_DIR / "test_PE.en"
    testa_dest_sent_file = SEGMENTER_DATA_DIR / "testa.words.txt"
    testa_dest_tag_file = SEGMENTER_DATA_DIR / "testa.tags.txt"
    export(testa_file, testa_dest_sent_file, testa_dest_tag_file, language=LANGUAGE, with_meta_tags=META_TAGS_LEVEL)

    # Validation Block
    testb_file = STAGE_DIR / "dev_PE.en"
    testb_dest_sent_file = SEGMENTER_DATA_DIR / "testb.words.txt"
    testb_dest_tag_file = SEGMENTER_DATA_DIR / "testb.tags.txt"
    export(testb_file, testb_dest_sent_file, testb_dest_tag_file, language=LANGUAGE, with_meta_tags=META_TAGS_LEVEL)

    # Export vocabularies
    export_vocabs(SEGMENTER_DATA_DIR, all_words, all_chars, all_tags)

def export_directory():
    DATASET_DIR = DATA_DIR / "parsed_to_conll" / "ArgumentAnnotatedEssays-2.0"
    # Destiny data directory
    SEGMENTER_DATA_DIR = Path(__file__, "..", "..", "..", "notebook", "data", "english_paragraph").resolve()

    testb_sent_file = SEGMENTER_DATA_DIR / "testb.words.txt"
    testb_tag_file = SEGMENTER_DATA_DIR / "testb.tags.txt"
    export_from_directory(DATASET_DIR / "dev", testb_sent_file, testb_tag_file, LANGUAGE, META_TAGS_LEVEL, META_TAG_SEPARATOR)
    
    testa_sent_file = SEGMENTER_DATA_DIR / "testa.words.txt"
    testa_tag_file = SEGMENTER_DATA_DIR / "testa.tags.txt"
    export_from_directory(DATASET_DIR / "test", testa_sent_file, testa_tag_file, LANGUAGE, META_TAGS_LEVEL, META_TAG_SEPARATOR)

    train_sent_file = SEGMENTER_DATA_DIR / "train.words.txt"
    train_tag_file = SEGMENTER_DATA_DIR / "train.tags.txt"
    export_from_directory(DATASET_DIR / "train", train_sent_file, train_tag_file, LANGUAGE, META_TAGS_LEVEL, META_TAG_SEPARATOR)

    # Export vocabularies
    export_vocabs(SEGMENTER_DATA_DIR, all_words, all_chars, all_tags)

export_directory()