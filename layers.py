from keras.layers import Layer
from keras import backend as K


class AttentionLayer(Layer):
    def __init__(self):
        self.supports_masking = False
        super(AttentionLayer, self).__init__()

    def compute_mask(self, inputs, mask=None):
        return None

    def build(self, input_shape):
        assert len(input_shape) == 3
        self.W = self.add_weight(name='attention_w',
                                 shape=(input_shape[-1],1),
                                 trainable = True,
                                 initializer='uniform',
                                 )
        self.b = self.add_weight(name='attention_b',
                                 shape=(1,),
                                 trainable = True,
                                 initializer='uniform',
                                 )
        super(AttentionLayer, self).build(input_shape)

    def call(self, inputs, **kwargs):
        # input_shape = (batch_size,time_steps,seq_len)
        a = K.softmax(K.tanh(K.dot(inputs, self.W) + self.b))
        outputs = a * inputs
        outputs = K.sum(outputs, axis=1)
        return outputs

    def compute_output_shape(self, input_shape):
        return input_shape[0], input_shape[-1]