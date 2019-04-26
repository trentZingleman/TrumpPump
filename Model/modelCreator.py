from textgenrnn import textgenrnn
from tqdm import tqdm
from datetime import datetime
import calendar
import time
import random

def makeModel():
    
    textgen = textgenrnn(name='TrumpPump')
    file_path = "../Data/trump_data_full.txt"
    textgen.reset()

    maxLength = 1
    print("maxLength: %d" %(maxLength))
    maxGenLength = 30
    print("maxGenLength: %d" %(maxGenLength))
    rnnLayers = 3
    print("rnnLayers: %d" %(rnnLayers))
    theDropout = 0.026504
    print("theDropout: %f" %(theDropout))
    batchSize = 998
    print("batchSize: %d" %(batchSize))
    rnnSize = 353
    print("rnnSize: %d" %(rnnSize))
    dimEmbeddings = 1464
    print("dimEmbeddings: %d" %(dimEmbeddings))
    maxWords = 16275
    print("maxWords: %d" %(maxWords))
    textgen.train_from_largetext_file(file_path, 
                                        new_model=True,
                                        validation=False,
                                        num_epochs=50,
                                        gen_epochs=1,
                                        word_level=True,
                                        rnn_bidirectional=True,
                                        max_length=maxLength,
                                        max_gen_length=maxGenLength,
                                        rnn_layers=rnnLayers,
                                        dropout=theDropout,
                                        batch_size=batchSize,
                                        rnn_size=rnnSize,
                                        dim_embeddings=dimEmbeddings,
                                        max_words=maxWords)
    print(textgen.model.summary())
    

if __name__ == "__main__":
    makeModel()