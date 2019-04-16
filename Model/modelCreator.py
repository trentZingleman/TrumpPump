from textgenrnn import textgenrnn
from tqdm import tqdm
from datetime import datetime
import calendar
import time

def makeModel():
    textgen = textgenrnn(name="first_try")
    file_path = "../Data/trump_data_full.txt"
    textgen.reset()
    textgen.train_from_largetext_file(file_path, 
                                        new_model=True, 
                                        num_epochs=20,
                                        gen_epochs=5,
                                        word_level=True,
                                        rnn_bidirectional=True,
                                        max_length=5,
                                        max_gen_length=50,
                                        rnn_layers=4,
                                        train_size=0.85,
                                        rnn_size=256,
                                        dim_embeddings=400,
                                        max_words=30000)
    print(textgen.model.summary())

if __name__ == "__main__":
    makeModel()