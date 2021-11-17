from transformers import AutoModel, AutoTokenizer
from transformers import Trainer

'''
    How to pretrained RoBERTa
    ref: https://github.com/pytorch/fairseq/blob/main/examples/roberta/README.pretraining.md
    https://www.reddit.com/r/LanguageTechnology/comments/gyxwz3/how_to_further_pretrain_bert_or_roberta_model/
'''

if "__main__" == __name__:
    model = AutoModel.from_pretrained("klue/roberta-base")
    tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")
