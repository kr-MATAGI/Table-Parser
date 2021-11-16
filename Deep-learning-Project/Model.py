from transformers import RobertaConfig, RobertaModel


'''
    How to pretrained RoBERTa
    ref: https://github.com/pytorch/fairseq/blob/main/examples/roberta/README.pretraining.md
    https://www.reddit.com/r/LanguageTechnology/comments/gyxwz3/how_to_further_pretrain_bert_or_roberta_model/
'''

if "__main__" == __name__:
    # Init a RoBERTa configuration
    modelConfig = RobertaConfig()

    # Init Model config
    model = RobertaModel(modelConfig)
    configuration = model.config

    print(configuration)

