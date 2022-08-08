CORPUS_NAME=testing

python3 project_corpus.py \
"data/corpus/$CORPUS_NAME" \
"data/parsed_to_conll/$CORPUS_NAME" \
"data/sentence_alignment/$CORPUS_NAME" \
"data/bidirectional_alignment/$CORPUS_NAME" \
"data/projection/$CORPUS_NAME" \
--source_language_sentences "data/translation/$CORPUS_NAME/testing_en" \
--target_language_sentences "data/translation/$CORPUS_NAME/testing_es"