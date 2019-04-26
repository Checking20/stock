from keras.callbacks import Callback
from sklearn.metrics import f1_score, precision_score, recall_score, matthews_corrcoef
import numpy as np


class MetricsEx(Callback):

    __score_dict = {
        'mcc': matthews_corrcoef,
        'f1': f1_score,
        'default': precision_score,
    }

    def __init__(self, score):
        super(MetricsEx, self).__init__()
        if score in MetricsEx.__score_dict:
            self.score_func = MetricsEx.__score_dict[score]
        else:
            self.score_func = MetricsEx.__score_dict['default']

    def on_train_begin(self, logs={}):
        self.scores = []

    def on_epoch_end(self, epoch, logs={}):
        val_predict = np.argmax(np.asarray(self.model.predict(self.validation_data[0])), axis=1)
        val_target = np.argmax(self.validation_data[1], axis=1)
        _val_f1 = self.score_func(val_target, val_predict)
        self.scores.append(_val_f1)
        print(' — val_f1:', _val_f1)
        return

