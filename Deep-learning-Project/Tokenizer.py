from transformers import RobertaTokenizer

class MyTokenizer:
    ### VAR ###

    ### PRIVATE ###
    def __init__(self):
        print("INIT KorTokenizer")
        self.tokenizer = RobertaTokenizer(vocab_file="")

    ### PUBLIC ###
