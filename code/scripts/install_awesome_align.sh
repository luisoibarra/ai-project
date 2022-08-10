# Install and build awesome-align

git clone https://github.com/neulab/awesome-align ./../projector/awesome-align

cd ./../projector/awesome-align

echo "Building..."

pip install -r requirements.txt
python setup.py install

echo "Completed"

echo "Downloading corpus"
awesome-align --model_name_or_path bert-base-multilingual-cased --data_file $(realpath ./../data/sentence_alignment/testing/essay001.ann.conll.align) --output_file $(realpath ./../data/bidirectional_alignment/testing/essay001.ann.conll.align.bidirectional) --batch_size 32 --extraction softmax
