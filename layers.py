from keras.layers import Layer
from keras import backend as K


class AttentionLayer(Layer):
    def __init__(self, num=10):
        self.supports_masking = True
        self.mlp_num = num
        super(AttentionLayer, self).__init__()

    def compute_mask(self, inputs, mask=None):
        return None

    def build(self, input_shape):
        assert len(input_shape) == 3
        self.W = self.add_weight(name='mlp_w_of_'+self.name,
                                 shape=(input_shape[-1], self.mlp_num),
                                 trainable = True,
                                 initializer='uniform',
                                 )
        self.b = self.add_weight(name='mlp_b_of_'+self.name,
                                 shape=(self.mlp_num,),
                                 trainable = True,
                                 initializer='uniform',
                                 )
        self.us = self.add_weight(name='content_vec_of_'+self.name,
                                  shape=(self.mlp_num, 1),
                                  trainable=True,
                                  initializer='uniform'

        )
        super(AttentionLayer, self).build(input_shape)

    def call(self, inputs, mask=None, **kwargs):
        # input_shape = (batch_size,time_steps,seq_len)
        if mask is not None:
            mask = K.cast(mask, K.floatx())

            u = K.tanh(K.dot(inputs, self.W) + self.b)
            utu = K.dot(u, self.us)

            utu_exp = K.exp(utu-K.max(utu, axis=-2, keepdims=True))
            utu_exp = mask*utu_exp
            a = utu_exp/K.sum(utu_exp, axis=-2, keepdims=True)

            outputs = a * inputs
            outputs = K.sum(outputs, axis=-2)
        else:
            u = K.tanh(K.dot(inputs, self.W) + self.b)
            a = K.softmax(K.dot(u, self.us), axis=-2)
            outputs = a * inputs
            outputs = K.sum(outputs, axis=-2)
        return outputs

    def compute_output_shape(self, input_shape):
        return input_shape[-3], input_shape[-1]


class MyMeanPool(Layer):
    def __init__(self):
        self.supports_masking = True
        super(MyMeanPool, self).__init__()

    def compute_mask(self, inputs, mask=None):
        return None

    def build(self, input_shape):
        super(MyMeanPool, self).build(input_shape)

    def call(self, inputs, mask=None):
        if mask is not None:
            mask = K.repeat(mask, inputs.shape[-1])
            mask = K.permute_dimensions(mask, (0, 2, 1))
            mask = K.cast(mask, K.floatx())
            inputs = inputs * mask
            return K.sum(inputs, axis=-2) / K.sum(mask, axis=-2)
        else:
            return K.mean(inputs, axis=-2)

    def compute_output_shape(self, input_shape):
        # remove temporal dimension
        return input_shape[-3], input_shape[-1]