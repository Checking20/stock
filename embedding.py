import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences


def embed_with_Bert():
    pass


def embed_with_avg_Glove():
    pass


def embed_with_avg_Elmo():
    pass


#embed news to vector
def embed_news(url):
    txt_df = pd.read_csv(url)