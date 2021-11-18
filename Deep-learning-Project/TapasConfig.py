import torch
import numpy as np


def rename_state_dict_keys(tapasBinPath:str, klueBinPath:str,
                           targetPath:str):
    print("Rename state dict keys")
    tapasStateDict = torch.load(tapasBinPath)
    klueStateDict = torch.load(klueBinPath)

    tapasKeyList = list(tapasStateDict.keys())
    klueKeyList = list(klueStateDict.keys())

    changeCnt = 0
    notInList = []
    for klueKey in klueKeyList:
        conv_kluekey = klueKey.replace("roberta.", "") # Del front word
        if conv_kluekey in tapasKeyList:
            changeCnt += 1
            tapasStateDict[conv_kluekey] = klueStateDict[klueKey]
        else:
            notInList.append(klueKey)

    # Maybe add
    needAddKeyList = ["roberta.embeddings.word_embeddings.weight",
                      "lm_head.bias", "lm_head.decoder.weight",
                      "lm_head.decoder.bias"]

    for addKey in needAddKeyList:
        if "roberta.embeddings.word_embeddings.weight" == addKey:
            newValue = klueStateDict[addKey]
            tapasStateDict[addKey] = newValue

        if "lm_head.bias" == addKey:
            newValue = klueStateDict[addKey]
            randValue = torch.randn(145150, dtype=torch.double) * 0.01
            newValue = torch.cat([newValue, randValue], dim=0)
            tapasStateDict[addKey] = newValue

        elif "lm_head.decoder.weight" == addKey:
            newValue = klueStateDict[addKey]
            randValue = torch.randn(145150, 768, dtype=torch.double) * 0.01
            newValue = torch.cat([newValue, randValue], dim=0)
            tapasStateDict[addKey] = newValue

        elif "lm_head.decoder.bias" == addKey:
            newValue = klueStateDict[addKey]
            randValue = torch.randn(145150, dtype=torch.double) * 0.01
            newValue = torch.cat([newValue, randValue], dim=0)
            tapasStateDict[addKey] = newValue

    torch.save(tapasStateDict, targetPath)
    print("Complete - TapasKeyListSize:", len(tapasKeyList), "Change Count:", changeCnt)
    print("Not in List:\n", notInList)

if "__main__" == __name__:

    tapas_path = "./ModelBinFiles/tapas.bin"
    tapas_state_dict = torch.load(tapas_path)

    klue_path = "./ModelBinFiles/klue-roberta.bin"
    klue_state_dict = torch.load(klue_path)

    targetPath = "./ModelBinFiles/klue-tapas-base.bin"
    rename_state_dict_keys(tapasBinPath=tapas_path,
                           klueBinPath=klue_path,
                           targetPath=targetPath)