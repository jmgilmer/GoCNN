# Visualizing the trained model
## Usage

Set the MODEL_PATH and SGF_DIRECTORY variables in main.py. If you cloned this repo a trained model .ckpt file
should be in data/working. 

Start gogui, then goto Program -> Attach and enter "python /path/to/main.py" for the command.
This should load a random sgf file in SGF_DIRECTORY. You can walk through the file in gogui
by clicking the "make program play" button. You can visualize the output of the model or
load a new sgf file by going to Tools -> Analyze Commands. Note after you load a new sgf make
sure to click the 'clear board' button to tell gogui to reset the board as well.