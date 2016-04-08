import numpy as np
import input_data
import tensorflow as tf
import math
import matplotlib
import matplotlib.pyplot as plt


mnist_width = 28
n_visible = mnist_width * mnist_width
n_hidden = 500
corruption_level = 0.3

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

# create node for input data
X = tf.placeholder("float", [None, n_visible], name='X')

# create node for curruption mask
mask = tf.placeholder("float", [None, n_visible], name='mask')

# create nodes for hidden variables
W_init_max = 4 * np.sqrt(6. / (n_visible + n_hidden))
W_init = tf.random_uniform(shape=[n_visible, n_hidden],
                           minval=-W_init_max,
                           maxval=W_init_max)

W = tf.Variable(W_init, name='W')
b = tf.Variable(tf.zeros([n_hidden]), name='b')

W_prime = tf.transpose(W) # tight weights between encoder and decoder
b_prime = tf.Variable(tf.zeros([n_visible]), name='b_prime')

def model(X, mask, W, b, W_prime, b_prime):
    tilde_X = mask * X # corrupted X

    Y = tf.nn.sigmoid(tf.matmul(tilde_X, W) + b) # hidden state
    Z = tf.nn.sigmoid(tf.matmul(Y, W_prime) + b_prime) # reconstructed input
    return Z

# build model graph
Z = model(X, mask, W, b, W_prime, b_prime)

# create cost function
cost = tf.reduce_sum(tf.pow(X - Z, 2)) # minimize squared error
train_op = tf.train.GradientDescentOptimizer(0.02).minimize(cost) # construct an optimizer

# load MNIST data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
trX, trY, teX, teY = mnist.train.images, mnist.train.labels, mnist.test.images, mnist.test.labels

sess = tf.Session()
init = tf.initialize_all_variables()
sess.run(init)


zeros = trX[trY[:,0] == 1]
nines = trX[trY[:,9] == 1]
for i in range(20):
    for start, end in zip(range(0, len(zeros), 100), range(100, len(zeros), 100)):
        input_ = zeros[start:end]
        mask_np = np.random.binomial(1, 1 - corruption_level, input_.shape)
        sess.run(train_op, feed_dict={X: input_, mask: mask_np})

    mask_np = np.random.binomial(1, 1 - corruption_level, teX.shape)
    print i, sess.run(cost, feed_dict={X: teX, mask: mask_np})

print "\n\nOk, now let's get the normal construction error of 0s: "
for start, end in zip(range(0, len(zeros), 1000), range(100, len(zeros), 1000)):
    input_ = zeros[start:end]
    mask_np = np.random.binomial(1, 1 - corruption_level, input_.shape)
    print sess.run(cost, feed_dict={X: input_, mask: mask_np})
"""
703.538
687.05
719.769
709.988
711.977
720.274
"""

print "\n\nOk, now let's get the normal construction error of 9s: "
for start, end in zip(range(0, len(nines), 1000), range(100, len(nines), 1000)):
    input_ = nines[start:end]
    mask_np = np.random.binomial(1, 1 - corruption_level, input_.shape)
    print sess.run(cost, feed_dict={X: input_, mask: mask_np})
"""
2144.66
2022.27
2004.07
2147.4
2125.98
2003.02
"""
