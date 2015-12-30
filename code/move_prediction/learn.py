import go_dataset
import tensorflow as tf
import time

TRAIN_FILE_PATH = "/home/justin/Programming/GoAI/MovePredictionCNN/data/input/train_samples.dat"
TEST_FILE_PATH = "/home/justin/Programming/GoAI/MovePredictionCNN/data/input/test_samples.dat"
data_set = go_dataset.GoDataset(TRAIN_FILE_PATH)
test_set = go_dataset.GoDataset(TEST_FILE_PATH)

x_ = tf.placeholder("float", shape=[None, 19,19,7])
move_ = tf.placeholder("float", shape=[None, 19 * 19])
 
def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)
 
def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)
 
def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')
 
 
W_conv1 = weight_variable([5, 5, 7, 64])
b_conv1 = bias_variable([64])
h_conv1 = tf.nn.relu(conv2d(x_, W_conv1) + b_conv1)
 
W_conv2 = weight_variable([5, 5, 64, 64])
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(conv2d(h_conv1, W_conv2) + b_conv2)
 
W_conv3 = weight_variable([5, 5, 64, 64])
b_conv3 = bias_variable([64])
h_conv3 = tf.nn.relu(conv2d(h_conv2, W_conv3) + b_conv3)
 
W_conv4 = weight_variable([5, 5, 64, 48])
b_conv4 = bias_variable([48])
h_conv4 = tf.nn.relu(conv2d(h_conv3, W_conv4) + b_conv4)
 
W_conv5 = weight_variable([5, 5, 48, 48])
b_conv5 = bias_variable([48])
h_conv5 = tf.nn.relu(conv2d(h_conv4, W_conv5) + b_conv5)
 
# Final outputs from layer 5
W_convm5 = weight_variable([5, 5, 48, 1])
b_convm5 = bias_variable([1])
h_convm5 = conv2d(h_conv5, W_convm5) + b_convm5
 
pred_move5 = tf.nn.softmax(tf.reshape(h_convm5,[-1, 19 * 19]))

move_f = tf.to_float(move_)

cross_entropy5 = -tf.reduce_sum(move_f*tf.log(pred_move5+1e-5))

error_function = cross_entropy5
train_step = tf.train.AdamOptimizer(1e-4).minimize(error_function)
 
correct_prediction = tf.equal(tf.argmax(pred_move5,1), tf.argmax(move_f,1))
move_accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
 
sess = tf.InteractiveSession()

saver = tf.train.Saver()
sess.run(tf.initialize_all_variables())
saver.restore(sess, tf.train.latest_checkpoint('.'))
print "latest checkpoint: ", tf.train.latest_checkpoint('.')
step = 0

start_time = time.time()
for i in xrange(100000000):
  batch = data_set.next_batch(100)
  train_step.run(feed_dict={x_: batch[0], move_: batch[1]})
  if (i % 1000 == 0):
    train_move_accuracy = move_accuracy.eval(feed_dict={
      x_: batch[0], move_: batch[1]})
    train_cross_entropy5 = cross_entropy5.eval(feed_dict={
      x_: batch[0], move_: batch[1]})
    print 'step: %d, epoch: %d, index_in_epoch: %d accuracy: %4.2f move_entropy5: %6.2f , total time (s): %s' %\
         (i, data_set.num_epochs, data_set.index_in_epoch, train_move_accuracy, train_cross_entropy5, \
            time.time() - start_time)
    saver.save(sess, 'move_pred19x19_5layers', global_step = step)
    step += 1