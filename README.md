
# Using CNN for Go (Weiqi/Baduk) board evaluation

This is code for training and evaluating a Convolutional Neural Network for board evaluation in Go. This is an ongoing project and I will be adding to it in the coming weeks. The basic idea is motivated from two recent papers which did move prediction by training a network from professional game records ([Clark et. al](http://arxiv.org/abs/1412.3409) and [Maddison et. al](http://arxiv.org/pdf/1412.6564v2.pdf)). In this project instead of predicting the next move given the current board, we instead predict the final state of the board. This is possible due to the nature of the game Go, because pieces do not move during the game, early and midgame board positions are highly predictive of the final ownership. One hope is that a well trained board evaluator can be used for a strong Go playing engine, in particular remove the need for Monte Carlo Tree Search (MTCS) and instead allow for a traditional alpha-beta pruning approach like in the best Chess programs. The model exhibited here would likely perform poorly for such a task (for a number of reasons), but it is still interesting to see what it learned.

##Current Model

The inputs to the model are 8 feature planes containing information about the current state of the board. The target is binary, where 0 indicates the player to move owns the location as either territory or has a stone on the location at the end of the game, 1 indicates the other player. In seki situations we consider both groups alive, and randomly assign spaces in between stones. Because we need to know the final state of the board, we only train on professional games which were played until the end, games ending in resignation are ignored. We train on ~15000 games from the GoGod data set which did not end in resignation. We used GNU-Go to remove dead stones from the board and determine final ownership. Training on only games not ending in resignation has likely introduced unwanted biases to the model (e.g. large groups are more likely to live and games are close), future work should address this issue.

So far I have only tried a single  architecture; namely a 5 layer CNN. It achieves 80% accuracy on a test set (test set consists of entire games not used in training). Once I streamline the munging phase I hope to try more architectures on a larger dataset. The convolution sizes are all 5x5 and the number of filters in each layer are 64, 64, 64, 48, and 48, this gives roughly 350,000 parameters. The final output layer is a single 5x5 convolution. I use rectified linear units for activations in between each layer. The output of the model is a vector of 361 probabilities, one for each space in the board, and is the probability that the player to move will occupy that space at the end of the game. We use a sigmoid activation for the output layer and minimize the sum of squares loss between the predicted probabilities and the actual binary output. 

The features of the model consist of 8 feature planes. 3 planes indicate player to move stones which have 1, 2, or >=3 liberies, 3 places indicate the other player's stones, 1 plane indicates a ko location, the final plane is all 1's so the convolutions can detect the edge of the board. We use an ADAM optimizer with learning rate 10^-4.

## Results

The model achieves 80% test set accuracy after ~4 hours of training on a GTX 970 card. After 12 hours of training accuracy is about 80.5%. Accuracy on the training set is around 81% suggesting we are currently under-fitting. Accuracy greatly varies based on far into the game it is.

![alt-text](http://i.imgur.com/za5fKov.png?1)

For most games the model achieves > 96% accuracy at the end of the game, however sometimes the model will incorrectly assess the status of some groups. 

![alt-text](http://i.imgur.com/Bx7Pkb4.png?1)

##Usage
Current API for the code isn't great, you need to set data_dir variables and other flags within several .py files. Basic pipeline is the following:
1. Create a directory of .sgf files you want to train on (I used the [GoGod dataset](http://senseis.xmp.net/?GoGoD)).
2. Run go_dataset_preprocessor.py, (first set the source and output dirs in main). This step requires [gnugo](https://www.gnu.org/software/gnugo/), which we need in order to remove dead stones and determine the final board position. **Note maybe 1 in 10000 games gnugo gets stuck in an infinite loop**. If so kill the process, remove the bad sgf file and restart the .py file, the .py file will skip over files already processed. This phase takes a while as gnugo is slow, maybe 5hours to process 10000 files. The output of each .sgf file is a binary .dat file containing board features and targets.
3. If desired, split .dat files into train and test folders.
4. Run train.ipynb (requires tensorflow).

##Third party libraries used
* Modified some code from [kgsgo-dataset-preprocessor](https://github.com/hughperkins/kgsgo-dataset-preprocessor) to do data munging.
* [gomill](https://github.com/mattheww/gomill)
* [gnugo](https://www.gnu.org/software/gnugo/)
* [tensorflow](https://www.tensorflow.org/)


##Todo

1. Use GoGui for better visualization of the model.
2. Streamline the install and munging phase so it is easier to replicate on new machines. Currently you will have to fight a lot of dependencies from a fresh clone.
3. Find work around for the issue where GNU-go sometimes gets stuck in infinite loop when removing dead stones (currently I have to delete the bad sgf file and restart go_dataset_preprocessor.py). 
4. Try additional features such as previous moves, turns since move was played.
5. Try different size model architectures.
6. Compare model with existing score evaluation programs.


> Written with [StackEdit](https://stackedit.io/).