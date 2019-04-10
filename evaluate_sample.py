import numpy as np
import tensorflow as tf
import os
import cv2
from model import cnn_model_fn


tf.logging.set_verbosity(tf.logging.INFO)

def load(dimension, directory = "new_chair_bmp/"):

    imagesTop = []
    imagesSide = []
    imagesFront = []

    ls = 0
    folder = directory

    length = len(os.listdir(folder)) // 3
    ls += length

    fileList = os.listdir(folder)
    fileList.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    print(fileList)


    # for filename in os.listdir(folder):
    for i in range(len(fileList)):
        filename = fileList[i]
    #     print(i)

        view = int(filename.split(".")[0])
        print(view)
        view = view % 3
        img = cv2.imread(folder+filename)
        if dimension < 224:
            img = cv2.resize(img, dsize=(dimension, dimension), interpolation=cv2.INTER_CUBIC)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = np.nan_to_num(img)


        if img is not None:
            if view == 1:
                imagesSide.append(1. - img / 255.)
            elif view == 2:
                imagesTop.append(1. - img / 255.)
            else:
                imagesFront.append(1. - img / 255.)


    imagesTop = np.array(imagesTop)
    imagesFront = np.array(imagesFront)
    imagesSide = np.array(imagesSide)

    #flatten the images
    imagesTop = np.reshape(imagesTop, (ls, dimension * dimension))
    imagesFront = np.reshape(imagesFront, (ls, dimension * dimension))
    imagesSide = np.reshape(imagesSide, (ls, dimension * dimension))

    return imagesTop, imagesFront, imagesSide

def main(*argv):
    directory = "new_chair_bmp/"
    if len(argv) > 0 and argv[0][-1:] == "/":
        directory = argv[0]

    #load chairs dataset
    imagesTop, imagesFront, imagesSide = load(56, directory)

    test_images = []
    #then the rest are test images and labels
    test_images.append(imagesTop)
    test_images.append(imagesFront)
    test_images.append(imagesSide)

    test_evaluations = [[],[],[]]

    for view in ["Top", "Front", "Side"]:
        id = ["Top", "Front", "Side"].index(view)


        classifier = tf.estimator.Estimator(model_fn=cnn_model_fn, model_dir="checkpoint/"+view+"/")

        eval_input_fn = tf.estimator.inputs.numpy_input_fn(x={"x": test_images[id]},
                                                           num_epochs=1,
                                                           shuffle=False)

        #The line below returns a generator that has the probability that the tested samples are Positive cases or Negative cases
        eval_results = classifier.predict(input_fn=eval_input_fn)

        #You need to iterate over the generator returned above to display the actual probabilities
        #This line should print something like {'classes': 0, 'probabilities': array([0.91087427, 0.08912573])}
        #the first element of 'probabilities' is the correlation of input with the Negative samples. The second element means positive.
        #If you evaluate multiple samples, just keep iterating over the eval_results generator.
        # eval_instance = next(eval_results)
        # print("eval_instance: ")
        # print(eval_instance)

        # This is how you extract the correlation to the positive class of the first element in your evaluation folder
        for eval in eval_results:
            #print("probability that this instance is positive is %3.2f " % eval['probabilities'][1])
            test_evaluations[id].append(eval['probabilities'][1])

    #the probability that the chair is a positive example is given by the minimum of the probabilities from each of the three views
    #in the default configuration sent, the first ten chairs should be negatives (low value) and the ten last chairs should be positives (high value)
    #as can be seen in this quick evaluation, there is roon for inprovement in the algorithm
    evaluation_chairs = np.amin(test_evaluations, axis=0)
    print(evaluation_chairs)
    print("done!")

    return evaluation_chairs


if __name__ == "__main__":
    # Add ops to save and restore all the variables.
    # saver = tf.train.Saver()
    tf.app.run()
