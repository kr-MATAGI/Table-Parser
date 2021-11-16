from transformers import RobertaConfig, RobertaModel



if "__main__" == __name__:
    # Init a RoBERTa configuration
    modelConfig = RobertaConfig()

    # Init Model config
    model = RobertaModel(modelConfig)
    configuration = model.config

    print(configuration)

