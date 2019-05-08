# keras model
from keras.layers import Dense, Input, LSTM, Embedding, Activation, GRU
from keras.layers import Dropout, SpatialDropout1D
from keras.layers import Bidirectional,TimeDistributed, concatenate
from keras.layers import GlobalMaxPool1D, GlobalAvgPool1D, Masking
from keras.models import Model,Sequential
from layers import AttentionLayer
from keras import initializers, regularizers, constraints, optimizers, layers
from keras import backend as K
from keras import metrics


from data_util import DATE_INTERVAL_NEWS,MAX_NEWS_NUM,EMBEDDING_SIZE

numerical_timestep = 20 # correspond to the 'size' of  the window
attribute_num = 5 # Open/High/Low/AdjClose/Volume


# numerical model
def build_numerical_model():
    numerical_input = Input(shape=(numerical_timestep,attribute_num))
    x = GRU(100, return_sequences=True)(numerical_input)
    x = Dropout(0.5)(x)
    x = GRU(100)(x)
    x = Dropout(0.5)(x)
    x = Dense(10, activation='relu')(x)
    x = Dense(2, activation='softmax')(x)
    model = Model(inputs=numerical_input,outputs=x)
    model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
    return model


# textual model
def build_textual_model(emb_size=EMBEDDING_SIZE):
    news_input = Input(shape=(DATE_INTERVAL_NEWS, MAX_NEWS_NUM, emb_size))

    x = news_input
    x = TimeDistributed(Masking(mask_value=0.))(x)
    x = TimeDistributed(AttentionLayer())(x)
    x = TimeDistributed(Dense(100, activation='relu'))(x)

    x = Bidirectional(GRU(50, return_sequences=True))(x)
    x = AttentionLayer()(x)
    x = Dropout(0.5)(x)
    x = Dense(10, activation='relu')(x)
    x = Dense(2, activation='softmax')(x)
    model = Model(inputs=news_input, outputs=x)
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


# hybrid model using both textual features and numerical features
def build_hybrid_model(emb_size=EMBEDDING_SIZE):
    numerical_input = Input(shape=(numerical_timestep, attribute_num))
    textual_input = Input(shape=(DATE_INTERVAL_NEWS, MAX_NEWS_NUM, emb_size))

    x1 = textual_input
    x1 = TimeDistributed(Masking(mask_value=0.))(x1)
    x1 = TimeDistributed(AttentionLayer())(x1)
    x1 = TimeDistributed(Dropout(0.2))(x1)
    x1 = TimeDistributed(Dense(100, activation='relu'))(x1)
    x1 = Bidirectional(GRU(50, return_sequences=True))(x1)
    x1 = AttentionLayer()(x1)
    x1 = Dropout(0.5)(x1)
    x1 = Dense(10, activation='relu')(x1)

    x2 = numerical_input
    x2 = GRU(100, return_sequences=True)(x2)
    x2 = Dropout(0.5)(x2)
    x2 = GRU(100)(x2)
    x2 = Dropout(0.5)(x2)
    x2 = Dense(10, activation='relu')(x2)

    x = concatenate([x1, x2])
    x = Dense(2, activation='softmax')(x)
    model = Model(inputs=[textual_input, numerical_input], outputs=x)
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model



