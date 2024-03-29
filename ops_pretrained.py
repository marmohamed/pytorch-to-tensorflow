import tensorflow as tf
import tensorflow.contrib as tf_contrib
import numpy as np


def conv2d(c,**kwargs):
    padding = 'VALID' if c.padding[0] is 0 else 'SAME'

    x = kwargs['inp']
    if c.padding[0] > 0:
        x = tf.keras.layers.ZeroPadding2D(padding=(c.padding[0], c.padding[1]))(x)

    padding = 'valid'
    
    W = c.weight.data.numpy().transpose([2, 3, 1, 0])
    if c.bias:
        b = c.bias.data.numpy()

    if c.bias:
        x = tf.keras.layers.Conv2D(c.out_channels, c.kernel_size, 
                                    strides=[c.stride[0], c.stride[1]],
                                    padding=padding,
                                    kernel_initializer=tf.constant_initializer(W),
                                    bias_initializer=tf.constant_initializer(b), use_bias=c.bias)(x)
    else:
        x = tf.keras.layers.Conv2D(c.out_channels, c.kernel_size, 
                                    strides=[c.stride[0], c.stride[1]],
                                    padding=padding,
                                    kernel_initializer=tf.constant_initializer(W), use_bias=c.bias)(x)

    return x

def relu(**kwargs):
    return tf.nn.relu(kwargs['inp'])
    
def max_pool(c,**kwargs):
    padding = 'VALID' if c.padding is 0 else 'SAME'
    x = tf.nn.max_pool(kwargs['inp'],[1,c.kernel_size,c.kernel_size,1],strides=[1,c.stride,c.stride,1],padding=padding)
    return x

def avg_pool(c,**kwargs):
    padding = 'VALID' if c.padding is 0 else 'SAME'
    x = tf.nn.avg_pool(kwargs['inp'],[1,c.kernel_size,c.kernel_size,1],strides=[1,c.stride,c.stride,1],padding=padding)
    return x

def flatten(**kwargs):
    x = tf.keras.layers.GlobalAveragePooling2D()(kwargs['inp'])
    return x

def fc(c, **kwargs):
    W = c.weight.data.numpy().transpose([1, 0])
    b = c.bias.data.numpy()
    if c.bias is not None:
        x = tf.keras.layers.Dense(c.out_features, 
                                    kernel_initializer=tf.constant_initializer(W),
                                    bias_initializer=tf.constant_initializer(b),
                                    use_bias=True)(kwargs['inp'])
    else:
        x = tf.keras.layers.Dense(c.out_features, 
                                kernel_initializer=tf.constant_initializer(W),
                                use_bias=False)(kwargs['inp'])
    return x

def fully_conneted_not_trained(x, units, use_bias=True, scope='fully_0'):
    with tf.variable_scope(scope):
        weight_init = tf.contrib.layers.xavier_initializer()
        weight_regularizer = tf_contrib.layers.l2_regularizer(0.0001)

        x = tf.layers.dense(x, units=units, kernel_initializer=weight_init, kernel_regularizer=weight_regularizer, use_bias=use_bias)

        return x

def dropout(c,**kwargs):
    return kwargs['inp']

def batch_norm(c, **kwargs):
    # parameters = [p for p in c.parameters()]
    beta = tf.constant_initializer(c.bias.data.numpy())
    gamma = tf.constant_initializer(c.weight.data.numpy())
    running_mean = tf.constant_initializer(c.running_mean.data.numpy())
    running_var = tf.constant_initializer(c.running_var.data.numpy())
    x = tf.layers.batch_normalization(kwargs['inp'], epsilon=c.eps, momentum=c.momentum,
                                    beta_initializer=beta,
                                    gamma_initializer=gamma,
                                    moving_mean_initializer = running_mean,
                                    moving_variance_initializer = running_var
                                    )
    return x

def resblock(x_init, parameters, bns, scope='resblock', downsample=False) :
    with tf.variable_scope(scope) :

        x = conv2d(parameters[0], inp=x_init)
        x = batch_norm(bns[0], inp=x)
        x = relu(inp=x)
    
        x = conv2d(parameters[2], inp=x)
        x = batch_norm(bns[2], inp=x)

        if downsample :
            x_init = conv2d(parameters[1], inp=x_init)
            x_init = batch_norm(bns[1], inp=x_init)

        x = x + x_init
        x = relu(inp = x)

        return x
