#!/usr/bin/env python3
import os.path
import tensorflow as tf
import helper
import warnings
from distutils.version import LooseVersion
import project_tests as tests


# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


def load_vgg(sess, vgg_path):
    """
    Load Pretrained VGG Model into TensorFlow.
    :param sess: TensorFlow Session
    :param vgg_path: Path to vgg folder, containing "variables/" and "saved_model.pb"
    :return: Tuple of Tensors from VGG model (image_input, keep_prob, layer3_out, layer4_out, layer7_out)
    """
    # TODO: Implement function
    #   Use tf.saved_model.loader.load to load the model and weights
    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'

    tf.saved_model.loader.load(sess, [vgg_tag], vgg_path)
    graph = tf.get_default_graph()

    input_tensor = graph.get_tensor_by_name(vgg_input_tensor_name)
    keep_prob = graph.get_tensor_by_name(vgg_keep_prob_tensor_name)
    layer3_tensor = graph.get_tensor_by_name(vgg_layer3_out_tensor_name)
    layer4_tensor = graph.get_tensor_by_name(vgg_layer4_out_tensor_name)
    layer7_tensor = graph.get_tensor_by_name(vgg_layer7_out_tensor_name)

    return input_tensor, keep_prob, layer3_tensor, layer4_tensor, layer7_tensor

tests.test_load_vgg(load_vgg, tf)


def layers(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  Build skip-layers using the vgg layers.
    :param vgg_layer3_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer7_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """
    # TODO: Implement function
    kernel_regularizer = tf.contrib.layers.l2_regularizer(1e-3)
    kernal_initializer = tf.truncated_normal_initializer(stddev=0.01)

    conv_1x1_7 = tf.layers.conv2d(vgg_layer7_out, num_classes, 1, padding='same', kernel_regularizer=kernel_regularizer, name='fcn_0', kernel_initializer=kernal_initializer)
    up_sample7 = tf.layers.conv2d_transpose(conv_1x1_7, num_classes, 4, 2, padding='same', kernel_regularizer=kernel_regularizer, name='fcn_1', kernel_initializer=kernal_initializer)
    conv_1x1_4 = tf.layers.conv2d(vgg_layer4_out, num_classes, 1, padding='same', kernel_regularizer=kernel_regularizer, name='fcn_2', kernel_initializer=kernal_initializer)
    combine_74 = tf.add(up_sample7, conv_1x1_4, name='fcn_3')
    up_sample74 = tf.layers.conv2d_transpose(combine_74, num_classes, 4, 2, padding='same', kernel_regularizer=kernel_regularizer, name='fcn_4', kernel_initializer=kernal_initializer)
    conv_1x1_3 = tf.layers.conv2d(vgg_layer3_out, num_classes, 1, padding='same', kernel_regularizer=kernel_regularizer, name='fcn_5', kernel_initializer=kernal_initializer)
    combine_374 = tf.add(up_sample74, conv_1x1_3, name='fcn_6')
    up_sample374 = tf.layers.conv2d_transpose(combine_374, num_classes, 16, 8, padding='same', kernel_regularizer=kernel_regularizer, name='fcn_7', kernel_initializer=kernal_initializer)

    return up_sample374

tests.test_layers(layers)


def optimize(nn_last_layer, correct_label, learning_rate, num_classes):
    """
    Build the TensorFLow loss and optimizer operations.
    :param nn_last_layer: TF Tensor of the last layer in the neural network
    :param correct_label: TF Placeholder for the correct label image
    :param learning_rate: TF Placeholder for the learning rate
    :param num_classes: Number of classes to classify
    :return: Tuple of (logits, train_op, cross_entropy_loss)
    """
    # TODO: Implement function
    logits = tf.reshape(nn_last_layer, (-1, num_classes))
    correct_label = tf.reshape(correct_label, (-1, num_classes))
    cross_entropy_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=correct_label))
    l2_loss = tf.losses.get_regularization_loss()
    loss = cross_entropy_loss + l2_loss
    # tvars = tf.trainable_variables()
    #fcn_vars = [var for var in tvars if 'fcn_' in var.name]
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    #train_op = optimizer.minimize(cross_entropy_loss, var_list=fcn_vars)
    train_op = optimizer.minimize(loss)
    tf.summary.histogram("Training loss", loss)
    return logits, train_op, loss
tests.test_optimize(optimize)


def train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image,
             correct_label, keep_prob, learning_rate):
    """
    Train neural network and print out the loss during training.
    :param sess: TF Session
    :param epochs: Number of epochs
    :param batch_size: Batch size
    :param get_batches_fn: Function to get batches of training data.  Call using get_batches_fn(batch_size)
    :param train_op: TF Operation to train the neural network
    :param cross_entropy_loss: TF Tensor for the amount of loss
    :param input_image: TF Placeholder for input images
    :param correct_label: TF Placeholder for label images
    :param keep_prob: TF Placeholder for dropout keep probability
    :param learning_rate: TF Placeholder for learning rate
    """
    # TODO: Implement function
    print("Start to train")
    train_writer = tf.summary.FileWriter( r'.\logs\1\train', sess.graph)
    sess.run(tf.global_variables_initializer())
    counter = 0
    for i in range(epochs):
        print("Epoch " + str(i))
        for image, label in get_batches_fn(batch_size):
            data = {
                input_image: image,
                correct_label: label,
                keep_prob: 0.5,
                learning_rate: 0.0001
            }
            merge = tf.summary.merge_all()
            _, loss, summary = sess.run([train_op, cross_entropy_loss, merge], feed_dict=data)
            train_writer.add_summary(summary, counter)
            counter += 1
            if counter % 10 == 0:
                print("Training loss " + str(loss))

tests.test_train_nn(train_nn)


def run():
    num_classes = 2
    image_shape = (160, 576)
    data_dir = './data'
    runs_dir = './runs'
    tests.test_for_kitti_dataset(data_dir)

    # Download pretrained vgg model
    helper.maybe_download_pretrained_vgg(data_dir)

    # OPTIONAL: Train and Inference on the cityscapes dataset instead of the Kitti dataset.
    # You'll need a GPU with at least 10 teraFLOPS to train on.
    #  https://www.cityscapes-dataset.com/

    epochs = 20
    batch_size = 1 # set batch size to 1 as training on the desktop

    with tf.Session() as sess:
        # Path to vgg model
        vgg_path = os.path.join(data_dir, 'vgg')
        # Create function to get batches
        get_batches_fn = helper.gen_batch_function(os.path.join(data_dir, 'data_road/training'), image_shape)

        # OPTIONAL: Augment Images for better results
        #  https://datascience.stackexchange.com/questions/5224/how-to-prepare-augment-images-for-neural-network

        # TODO: Build NN using load_vgg, layers, and optimize function
        input_image, keep_prob, *vgg_layers = load_vgg(sess, vgg_path)
        output = layers(*vgg_layers, num_classes)
        
        # TODO: Train NN using the train_nn function
        
        correct_label = tf.placeholder(tf.int32, [None, None, None, num_classes])
        learning_rate = tf.placeholder(tf.float32)
        logits, train_op, cross_entropy_loss = optimize(output, correct_label, learning_rate, num_classes)
        train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image,
             correct_label, keep_prob, learning_rate)
        # TODO: Save inference data using helper.save_inference_samples
        helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, keep_prob, input_image)
        # OPTIONAL: Apply the trained model to a video


if __name__ == '__main__':
    run()
