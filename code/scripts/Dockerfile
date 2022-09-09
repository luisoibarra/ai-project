FROM tensorflow/tensorflow:2.9.1-jupyter

RUN pip install tensorflow-addons \
 && pip install nltk && python -m nltk.downloader popular \
 && pip install pandas \
 && pip install scikit-learn