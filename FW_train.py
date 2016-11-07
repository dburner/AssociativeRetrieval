"""
Fast weights training part.
"""


import tensorflow as tf
import configuration

from FW_model import FW_model

def main():
  config = configuration.ModelConfig(data_filename="input_seqs_train")
  train(config)

def train(config):
  with tf.Graph().as_default():
    model = FW_model(config)
    inputs_seqs_batch, outputs_batch = model.reader.read()
    init_op = tf.group(tf.initialize_all_variables(),
                       tf.initialize_local_variables())

    sess = tf.Session()
    sess.run(init_op)
    saver = tf.train.Saver(tf.all_variables())
    global_steps = 0

    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)

    train_writer = tf.train.SummaryWriter("./log/FW/train", sess.graph)
    validation_writer = tf.train.SummaryWriter("./log/FW/validation", sess.graph)
    try:
      while not coord.should_stop():
        input_data, targets = sess.run([inputs_seqs_batch, outputs_batch])
        cost, _, summary= sess.run([model.cost, model.train_op, model.summary_all], {model.input_data: input_data,
                                                                                     model.targets: targets})
        print("Step %d: cost:%f" % (global_steps,  cost))
        train_writer.add_summary(summary, global_steps)

        global_steps += 1
        if global_steps % 1000 == 0:
          # (accuracy, summary) = sess.run([model.accuracy, model.summary_accuracy], {model.input_data: model.validation_inputs,
          #                                                                           model.targets: model.validation_targets})
          # validation_writer.add_summary(summary, global_steps)
          # print("Accuracy: %f" % accuracy)
          print(saver.save(sess, "./save/FW/save", global_step=global_steps))
        if global_steps > 30000:
          break
    except tf.errors.OutOfRangeError:
      print("Error")
    finally:
      # When done, ask the threads to stop.
      coord.request_stop()
    coord.join(threads)
    sess.close()

if __name__ == "__main__":
  main()
