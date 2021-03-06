import collections

import torch
import numpy as np


def rename_state_dict_keys(tapasBinPath:str, klueBinPath:str, targetPath:str):
    print("Rename state dict keys")

    tapasStateDict = torch.load(tapasBinPath)
    klueStateDict = torch.load(klueBinPath)

    tapasKeyList = list(tapasStateDict.keys())
    klueKeyList = list(klueStateDict.keys())

    changeCnt = 0
    notInList = []
    for klueKey in klueKeyList:
        conv_kluekey = klueKey.replace("roberta.", "tapas.") # Del front word
        if conv_kluekey in tapasKeyList:
            changeCnt += 1
            tapasStateDict[conv_kluekey] = klueStateDict[klueKey]
        else:
            notInList.append(klueKey)

    # Maybe add
    needAddKeyList = ["roberta.embeddings.word_embeddings.weight",
                      "lm_head.bias",
                      "lm_head.dense.weight",
                      "lm_head.dense.bias",
                      "lm_head.layer_norm.weight",
                      "lm_head.layer_norm.bias",
                      "lm_head.decoder.weight",
                      "lm_head.decoder.bias"]

    needAddkeyCount = 0
    for addKey in needAddKeyList:
        klueVal = klueStateDict[addKey]
        if "roberta.embeddings.word_embeddings.weight" == addKey:
            needAddkeyCount += 1
            tapasStateDict["tapas.embeddings.word_embeddings.weight"] = klueVal

        elif "lm_head.bias" == addKey:
            needAddkeyCount += 1
            tapasStateDict["cls.predictions.bias"] = klueVal

        elif "lm_head.dense.weight" == addKey:
            needAddkeyCount += 1
            tapasStateDict["cls.predictions.transform.dense.weight"] = klueVal

        elif "lm_head.dense.bias" == addKey:
            needAddkeyCount += 1
            tapasStateDict["cls.predictions.transform.dense.bias"] = klueVal

        elif "lm_head.layer_norm.weight" == addKey:
            needAddkeyCount += 1
            tapasStateDict["cls.predictions.transform.LayerNorm.weight"] = klueVal

        elif "lm_head.layer_norm.bias" == addKey:
            needAddkeyCount += 1
            tapasStateDict["cls.predictions.transform.LayerNorm.bias"] = klueVal

        elif "lm_head.decoder.weight" == addKey:
            needAddkeyCount += 1
            tapasStateDict["cls.predictions.decoder.weight"] = klueVal

        elif "lm_head.decoder.bias" == addKey:
            needAddkeyCount += 1
            tapasStateDict["cls.predictions.decoder.bias"] = klueVal

    # re-init
    curVal = tapasStateDict["tapas.embeddings.position_embeddings.weight"]
    randVal = torch.randn(510, 768, dtype=torch.double) * 0.01
    newVal = torch.cat([curVal, randVal], dim=0)
    tapasStateDict["tapas.embeddings.position_embeddings.weight"] = newVal

    torch.save(tapasStateDict, targetPath)
    print("Complete - TapasKeyListSize:", len(tapasKeyList), "Change Count:", changeCnt)
    print("Not in List:\n", notInList)
    print("NeedAddListSize:", len(needAddKeyList), "Need Add Key Count:", needAddkeyCount)

def CheckModelKeyShape(path_1, path_2, key):
    path_1_dict = torch.load(path_1)
    path_2_dict = torch.load(path_2)

    print("key :", key)
    print("{ masklm -", path_1_dict[key].shape, " : mybin -", path_2_dict[key].shape, "}")

def PrintStateDictKeyValueLen(dictPath):
    stateDict = torch.load(dictPath)

    for key, val in stateDict.items():
        print(key, "-", len(val))

def RemoveWordInStateDict(bin_path, remove_word, target_path):
    origin_dict = torch.load(bin_path)

    origin_key_list = list(origin_dict.keys())

    # remove word
    new_dict = collections.OrderedDict()
    for ori_key in origin_key_list:
        remove_key = ori_key.replace(remove_word+".", "")
        new_dict[remove_key] = origin_dict[ori_key]

    torch.save(new_dict, target_path)
    print("Made:", target_path)

if "__main__" == __name__:
    tapas_path = "./ModelBinFiles/tapas.bin"
    tapas_mask_lm_path = "./ModelBinFiles/tapas-base-masklm.bin"
    klue_path = "./ModelBinFiles/klue-roberta.bin"
    targetPath = "./pytorch_model.bin"
    # rename_state_dict_keys(tapasBinPath=tapas_mask_lm_path,
    #                        klueBinPath=klue_path,
    #                        targetPath=targetPath)

    print("\n-----------------------------------------\n")


    # CheckModelKeyShape(tapas_mask_lm_path, targetPath, "tapas.embeddings.word_embeddings.weight")
    # CheckModelKeyShape(tapas_mask_lm_path, targetPath, "tapas.embeddings.position_embeddings.weight")
    # CheckModelKeyShape(tapas_mask_lm_path, targetPath, "cls.predictions.bias")
    # CheckModelKeyShape(tapas_mask_lm_path, targetPath, "cls.predictions.decoder.weight")
    # CheckModelKeyShape(tapas_mask_lm_path, targetPath, "cls.predictions.decoder.bias")



    '''
        klue - roberta.embeddings.position_embeddings.weight - 514
        tapas-mask-lm - tapas.embeddings.position_embeddings.weight - 1024
        target - tapas.embeddings.position_embeddings.weight - 1024
    '''
    # PrintStateDictKeyValueLen("./output/korwiki_1.bin")


    # fin-tuning remove 'module.'
    origin_file = "./output/korquad_1.bin"
    remove_word = "module"
    target_path = "output/sh_korwiki_token_none_redict.bin"
    RemoveWordInStateDict(origin_file, remove_word, target_path)
    PrintStateDictKeyValueLen(target_path)
