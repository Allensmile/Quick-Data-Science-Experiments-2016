"""WRONG"""
"""
39 44074.0
"""
import numpy as np
import input_data
import tensorflow as tf
import math
import matplotlib
import matplotlib.pyplot as plt


mnist_width = 28
n_visible = mnist_width * mnist_width
n_hidden_1 = 500
n_hidden_2 = 250
corruption_level = 0.2

# create node for input data
X = tf.placeholder("float", [None, n_visible], name='X')

# create node for curruption mask
mask = tf.placeholder("float", [None, n_visible], name='mask')

# create nodes for hidden variables
W_1_init_max = 4 * np.sqrt(6. / (n_visible + n_hidden_1))
W_1_init = tf.random_uniform(shape=[n_visible, n_hidden_1],
                           minval=-W_1_init_max,
                           maxval=W_1_init_max)

W_1 = tf.Variable(W_1_init, name='W_1')
b_1 = tf.Variable(tf.zeros([n_hidden_1]), name='b_1')

W_2_init_max = 4 * np.sqrt(6. / (n_hidden_1 + n_hidden_2))
W_2_init = tf.random_uniform(shape=[n_hidden_1, n_hidden_2],
                           minval=-W_2_init_max,
                           maxval=W_2_init_max)

W_2 = tf.Variable(W_2_init, name='W_2')
b_2 = tf.Variable(tf.zeros([n_hidden_2]), name='b_2')

W_1_prime = tf.transpose(W_1)
b_1_prime = tf.Variable(tf.zeros([n_visible]), name='b_1_prime')
W_2_prime = tf.transpose(W_2)
b_2_prime = tf.Variable(tf.zeros([n_hidden_1]), name='b_2_prime')

def model(X, mask, W_1, b_1, W_1_prime, b_1_prime, W_2, b_2, W_2_prime, b_2_prime):
    tilde_X = mask * X # corrupted X

    Y_1 = tf.nn.sigmoid(tf.matmul(tilde_X, W_1) + b_1)
    Y_2 = tf.nn.sigmoid(tf.matmul(Y_1, W_2) + b_2)
    Z_2 = tf.nn.sigmoid(tf.matmul(Y_2, W_2_prime) + b_2_prime)
    Z_1 = tf.nn.sigmoid(tf.matmul(Z_2, W_1_prime) + b_1_prime)
    return Z_1

# build model graph
Z = model(X, mask, W_1, b_1, W_1_prime, b_1_prime, W_2, b_2, W_2_prime, b_2_prime)

# create cost function
cost = tf.reduce_sum(tf.pow(X - Z, 2)) # minimize squared error
train_op = tf.train.RMSPropOptimizer(0.002, 0.9).minimize(cost)

# load MNIST data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
trX, trY, teX, teY = mnist.train.images, mnist.train.labels, mnist.test.images, mnist.test.labels

sess = tf.Session()
init = tf.initialize_all_variables()
sess.run(init)

minibatch_size = 50

for i in range(40):
    for start, end in zip(range(0, len(trX), minibatch_size), range(minibatch_size, len(trX), minibatch_size)):
        input_ = trX[start:end]
        mask_np = np.random.binomial(1, 1 - corruption_level, input_.shape)
        sess.run(train_op, feed_dict={X: input_, mask: mask_np})

    mask_np = np.random.binomial(1, 1 - corruption_level, teX.shape)
    print i, sess.run(cost, feed_dict={X: teX, mask: mask_np})

def plot_mnist_digit(image1, image2):
    """ Plot a single MNIST image."""
    fig = plt.figure()
    ax = fig.add_subplot(1, 2, 1)
    image = np.reshape(image1, (28, 28))
    ax.matshow(image, cmap = matplotlib.cm.binary)
    plt.xticks(np.array([]))
    plt.yticks(np.array([]))
    ax = fig.add_subplot(1, 2, 2)
    image = np.reshape(image2, (28, 28))
    ax.matshow(image, cmap = matplotlib.cm.binary)
    plt.xticks(np.array([]))
    plt.yticks(np.array([]))
    plt.show()

mask_np = np.random.binomial(1, 1 - corruption_level, teX.shape)
myy = sess.run(Z, feed_dict={X: teX, mask:mask_np})
plot_mnist_digit(teX[0], myy[0])
