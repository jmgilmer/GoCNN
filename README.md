
# Using CNN for Go (Weiqi/Baduk) board evaluation with tensorflow

This is code for training and evaluating a Convolutional Neural Network for board evaluation in Go. This is an ongoing project and I will be adding to it in the coming weeks. The basic idea is motivated from two recent papers which did move prediction by training a network from professional game records ([Clark et. al](http://arxiv.org/abs/1412.3409) and [Maddison et. al](http://arxiv.org/pdf/1412.6564v2.pdf)). In this project instead of predicting the next move given the current board, we instead predict the final state of the board. As a result we obtain a model which is able to estimate territory and identify dead stones and weak groups. The model, however is not great at life and death

##Current Model

The inputs to the model are 8 feature planes containing information about the current state of the board. The target is a 19x19 binary matrix, where 1 indicates the player to move owns the location as either territory or has a stone on the location at the end of the game, 0 indicates the other player. In seki situations we consider both groups alive, and randomly assign spaces in between stones. Because we need to know the final state of the board, we only train on professional games which were played until the end, games ending in resignation are ignored. We train on ~15000 games from the Go4Go data set. We used GNU-Go to remove dead stones from the board and determine final ownership. Training on only games not ending in resignation has likely introduced unwanted biases to the model (e.g. large groups are more likely to live and all games are close), future work should address this issue.

So far I have only tried a single  architecture; namely a 5 layer CNN. It achieves 80% accuracy on a test set (test set consists of 150 games not used in training, resulting in roughly 150*250 = 37500 samples). The convolution sizes are all 5x5 and the number of filters in each layer are 64, 64, 64, 48, and 48, this gives roughly 350,000 parameters. The final output layer is a single 5x5 convolution. I use rectified linear units for activations in between each layer. The output of the model is a vector of 361 probabilities, one for each space in the board, and is the probability that the player to move will occupy that space at the end of the game. We use a sigmoid activation for the output layer and minimize the sum of squares loss between the predicted probabilities and the actual binary target. 

The input to the model consist of 8 feature planes. 3 planes indicate player to move stones which have 1, 2, or >=3 liberies, 3 places indicate the other player's stones, 1 plane indicates a ko location, the final plane is all 1's so the convolutions can detect the edge of the board. We use an ADAM optimizer with learning rate 10^-4.

## Results

The model achieves 80% test set accuracy after ~4 hours of training on a GTX 970 card. After 12 hours of training accuracy is about 80.5%. Accuracy on the training set is around 81% suggesting we are currently under-fitting. Accuracy greatly varies based on far into the game it is.

![alt-text](http://i.imgur.com/za5fKov.png?1)

For most games the model achieves > 96% accuracy at the end of the game. Note that accuracy is measured the average over all 361 spaces, which include neutral spaces that may exist between two live groups, these spaces were randomly assigned when gnugo finished the games and so it would be unreasonable to expect 100% accuracy even at the last move. 

It is a lot of fun to visualize the model with gogui. Because the model has to make a prediction for all 361 board spaces,
we get a more detailed picture of what the model's understanding of the game is than if the model was just predicting the next move.

![alt-text](http://i.imgur.com/pJnsdty.png)

Above is the model's prediction halfway through a game, w has just played G13. The color of each square indicates which player the model believes will occupy that square at the end of the game. The size of the square indicates how confident the model is about that square. It has correctly determined the status of the black stones at B11 and the white stones at D4. It is unsure (as am I) as to who will occupy the top side of the board as well as the area around N3.

It is interesting to see what sort of game knowledge the model as learned. As a small easy example consider an early game below and note the how the model treats a 4-4 (Q16) stone differently than a 3-4 (R4). One of the first things one learns about Go is the 3-4 stone has a much firmer grasp on the corner and the 4-4 is more about influence. The model also seems more sure about black's hold on the bottom left than whites on the top left (I could be wrong but I think the 2 space jump can be invaded?)

![alt-text](http://i.imgur.com/iNLLBNH.png)

## Future Improvements to the Model
There are a lot of potential ways to improve the model. Current features are very minimal, only containing liberty information and ko information. The following additional features should make the model much more predictive, in particular with life and death situations:

1. Locations of recent moves
2. Age of stones

It is unclear though whether or not previous move locations is a good idea if the model is to be used in a go engine, but it should certainly help improve accuracy.

**Chain Pooling**
One interesting tweak I would like to try is what I call "chain pooling". To motivate chain pooling, consider the game below (black has just played a sacrificial stone at T11):

![alt-text](http://i.imgur.com/K06c91S.png)

Note the connected black stones at G16. The model is confident (and correct) that the upper part of the group will live at G18 and G17, yet it is unsure what will happen to G16, H16, and G15. However, even beginner Go players will agree that all stones in a connected group should share the same fate. As another example look at the white stones around S9. It would make sense to encourage the model to make the same predictions about connected stones, it would also make sense for the model to have the same internal representation for connected stones in the intermediate layers. 

To fix these issues I propose internal pooling layers where one takes a max pool along connected groups of stones. This is a little more complicated than traditional max pooling because the **shape of the max pools depends on the input**. I believe the resulting model space should be differentiable, it's more of a question of how to implement this computationally. 

##Usage

First install dependencies:

`$pip install gomill`

Download "gogui-1.4.9.zip" and following the install instructions for [gogui](http://sourceforge.net/projects/gogui/files/gogui/1.4.9/)

Install [tensorflow](https://www.tensorflow.org/)

**Training**

Current API for the code isn't great, you need to set data_dir variables and other flags within several .py files. Basic pipeline is the following:

1. Create a directory of .sgf files you want to train on (I used the [Go4Go dataset](http://www.go4go.net/go/)).
2. Run go_dataset_preprocessor.py, (first set the source and output dirs in main). This step requires [gnugo](https://www.gnu.org/software/gnugo/), which we need in order to remove dead stones and determine the final board position. **Note maybe 1 in 10000 games gnugo gets stuck in an infinite loop**. If so kill the process, remove the bad sgf file and restart the .py file, the .py file will skip over files already processed. This phase takes a while as gnugo is slow, maybe 5hours to process 10000 files. The output of each .sgf file is a binary .dat file containing board features and targets.
3. If desired, split .dat files into train and test folders.
4. Run train.ipynb (requires tensorflow).

**Visualization**

For visualization see the README under code/visualiation. You can use a saved checkpoint of the model which is located in data/working, also a single sgf file which is located in data/sgf_files.
##Third party libraries/software used
* Modified some code from [kgsgo-dataset-preprocessor](https://github.com/hughperkins/kgsgo-dataset-preprocessor) to do data munging.
* [gomill](https://github.com/mattheww/gomill)
* [gnugo](https://www.gnu.org/software/gnugo/)
* [tensorflow](https://www.tensorflow.org/)
* [gogui](http://gogui.sourceforge.net/)


##Todo


1. Streamline the install and munging phase so it is easier to replicate on new machines. Currently you will have to fight a lot of dependencies from a fresh clone.
2. Find work around for the issue where GNU-go sometimes gets stuck in infinite loop when removing dead stones (currently I have to delete the bad sgf file and restart go_dataset_preprocessor.py). 
3. Try additional features such as previous moves, turns since move was played.
4. Try different size model architectures.
5. Compare model with existing score evaluation programs.

##License

MIT License 


> Written with [StackEdit](https://stackedit.io/).