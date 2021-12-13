#import tokenization
import collections

from evaluate2 import f1_score
from evaluate2 import exact_match_score

from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os
import random
import sys
from io import open
import QuestionAnswering
import numpy as np
import torch
from torch.utils.data import (DataLoader, RandomSampler, TensorDataset, SequentialSampler)
from tqdm import tqdm, trange

if sys.version_info[0] == 2:
    import cPickle as pickle
else:
    import pickle

import datasets
class KorQuadDataset(datasets.Dataset):
    def __init__(self, srcData):
        self.srcData = srcData

    def __getitem__(self, idx):
        data = self.srcData[idx]
        items = {
            "input_ids": None,
            "attention_mask": None,
            "input_rows": None,
            "input_cols": None,
            "input_range": None,
        }

        #items["start_ids"] = torch.tensor(data["start_ids"], dtype=torch.int64)
        #items["end_ids"] = torch.tensor(data["end_ids"], dtype=torch.int64)

        ## input_ids
        items["input_ids"] = torch.tensor(data["input_ids"], dtype=torch.int64)

        ## attention_mask
        items["attention_mask"] = torch.tensor(data["attention_mask"], dtype=torch.int64)

        ## token_type_ids
        # segment_ids
        segment_ids_tensor = torch.tensor(data["input_segments"], dtype=torch.int64)

        # column_ids
        column_ids_tensor = torch.tensor(data["input_cols"], dtype=torch.int64)
        items["input_cols"] = column_ids_tensor

        # row_ids
        row_ids_tensor = torch.tensor(data["input_rows"], dtype=torch.int64)
        items["input_rows"] = row_ids_tensor

        # pre_labels - not used (fill with zero)
        # pre_labels_tensor = torch.tensor(np.zeros(512), dtype=torch.int64)

        # column_ranks
        #column_ranks_tensor = torch.tensor(data["col_ranks"][0], dtype=torch.int64)

        # inv_column_ranks
        #inv_column_ranks = torch.flip(column_ranks_tensor, dims=[0])

        # numeric_relations
        # numeric_relation_tensor = torch.tensor(np.zeros(512), dtype=torch.int64)
        # items["token_type_ids"] = torch.column_stack([segment_ids_tensor,
        #                                               column_ids_tensor,
        #                                               row_ids_tensor,
        #                                               pre_labels_tensor,
        #                                               column_ranks_tensor,
        #                                               inv_column_ranks,
        #                                               numeric_relation_tensor])

        # input_range
        items["input_range"] = torch.tensor(data["input_range"], dtype=torch.int64)

        return items

    def __len__(self):
        return len(self.srcData)


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def load_vocab(vocab_path):
    vocab = collections.OrderedDict()
    index = 0
    with open(vocab_path, mode="r", encoding="utf-8") as vf:
        for line in vf.read().splitlines():
            vocab[line.split()[0]] = index
            index += 1
        inv_vocab = {v: k for k, v in vocab.items()}
        return vocab, inv_vocab


def evaluation_torch_start():
    print("Evaluation torch start !")
    f_tokenizer = AutoTokenizer.from_pretrained('klue/roberta-base')

    vocab, inv_vocab = load_vocab("../klue-vocab.txt")

    print(1)
    # print(args.no_cuda)

    device = torch.device("cuda" if torch.cuda.is_available() and not False else "cpu")
    n_gpu = torch.cuda.device_count()

    print('n gpu:', n_gpu)

    adam_epsilon = 1e-8
    seed = 1136
    output_dir = 'output'
    learning_rate = 5e-5
    num_train_epochs = 1.0  # 5
    train_batch_size = 4  # 48
    max_grad_norm = 1.0

    num_label = 2

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if n_gpu > 0:
        torch.cuda.manual_seed_all(seed)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    '''
    modelPath = "./"
    model = QuestionAnswering.QuestionAnswering(modelPath)
    #model = torch.nn.DataParallel(model)

    print(2)
    # model.load_state_dict(torch.load(args.checkpoint))
    num_params = count_parameters(model)
    # logger.info("Total Parameter: %d" % num_params)
    model.to(device)
    

    # Prepare optimizer
    param_optimizer = list(model.named_parameters())
    no_decay = ['bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
         'weight_decay': 0.0},
        {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
    ]
    '''

    input_ids = np.load('./input_ids_test.npy')
    input_segments = np.load('./input_segments_test.npy')
    attention_mask = np.load('./input_masks_test.npy')
    input_rows = np.load('./input_rows_test.npy')
    input_cols = np.load('./input_cols_test.npy')
    input_range = np.array(range(input_ids.shape[0]), dtype=np.int32)

    answer_texts = np.load('./answer_text_test.npy')

    print("input_ids.shape:", input_ids.shape)
    print("input_segments.shape:", input_segments.shape)
    print("attention_mask.shape:", attention_mask.shape)
    print("input_rows.shape:", input_rows.shape)
    print("input_cols.shape:", input_cols.shape)
    print("input_range.shape:", input_range.shape)

    test_data_dict = {
        "input_ids": None,
        "input_segments": None,
        "attention_mask": None,
        "input_rows": None,
        "input_cols": None,
        "input_range": None,
    }

    test_data_dict["input_ids"] = input_ids
    test_data_dict["input_segments"] = input_segments
    test_data_dict["attention_mask"] = attention_mask
    test_data_dict["input_rows"] = input_rows
    test_data_dict["input_cols"] = input_cols
    test_data_dict["input_range"] = input_range

    test_dataset = datasets.Dataset.from_dict(test_data_dict)
    test_dataset = KorQuadDataset(test_dataset)

    test_sampler = SequentialSampler(test_dataset)
    test_dataloader = DataLoader(test_dataset, sampler=test_sampler, batch_size=train_batch_size)

    output_model_file = "../output/sh_korwiki_token_none_redict.bin"

    modelPath = "../SavedModel/sh_korwiki"
    #modelPath = "klue/roberta-base"
    model = QuestionAnswering.QuestionAnswering(modelPath)
    model.load_state_dict(torch.load(output_model_file))
    model = model.cuda()
    model.eval()
    model.zero_grad()

    iter_bar = tqdm(test_dataloader, desc="Test(XX Epoch) Step(XX/XX) (Mean loss=X.X) (loss=X.X)")

    epo = 0
    f1 = 0
    em = 0

    for step, batch in enumerate(iter_bar):
        # if n_gpu == 1:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        input_rows = batch["input_rows"].to(device)
        input_cols = batch["input_cols"].to(device)
        input_range = batch["input_range"].to(device)

        # Check shape
        # print("input_ids.shape:", input_ids.shape)


        # input_ids, input_segments, attention_mask, input_rows, input_cols, input_range = batch
        #start_logits, end_logits = model(input_ids, input_segments, attention_mask, input_rows, input_cols, None, None)
        start_logits, end_logits = model(input_ids=input_ids,
                                         attention_mask=attention_mask,
                                         input_rows=input_rows,
                                         input_cols=input_cols,
                                         start_positions=None,
                                         end_positions=None,
                                         token_type_ids=None)

        input_ids = input_ids.cpu().numpy()
        input_range = input_range.cpu().numpy()
        cols_has_ans = input_rows.cpu().numpy()

        # f_tokenizer = tokenization.FullTokenizer(vocab_file='vocab.txt')

        probs_start = np.array(start_logits.detach().cpu().numpy(), dtype=np.float32)
        probs_stop = np.array(end_logits.detach().cpu().numpy(), dtype=np.float32)

        for j in range(input_ids.shape[0]):
            for k in range(1, input_ids.shape[1]):
                probs_start[j, k] = 0
                probs_stop[j, k] = 0

                if input_ids[j, k] == 2:
                    break

        prob_scores = []
        c_scores = []

        for j in range(input_ids.shape[0]):
            # paragraph ranking을 위한 score 산정기준
            # score2 = ev_values[j, 0]
            score2 = 2 - (probs_start[j, 0] + probs_stop[j, 0])

            prob_scores.append(score2)
            # c_scores.append(self.chuncker.get_chunk_score(sequences[j]))

        if True:
            for j in range(input_ids.shape[0]):
                probs_start[j, 0] = -999
                probs_stop[j, 0] = -999

            # CLS 선택 무효화

            prediction_start = probs_start.argmax(axis=1)
            prediction_stop = probs_stop.argmax(axis=1)

            answers = []
            scores = []
            candi_scores = []

            for j in range(input_ids.shape[0]):
                answer_start_idx = prediction_start[j]
                answer_stop_idx = prediction_stop[j]

                if cols_has_ans[j, answer_start_idx] != cols_has_ans[j, answer_stop_idx]:
                    #print('@@@@@@@@@@@@@@@')
                    answer_stop_idx2 = answer_stop_idx
                    answer_stop_idx = answer_start_idx
                    answer_start_idx2 = answer_stop_idx2

                    for k in range(answer_start_idx + 1, input_ids.shape[1]):
                        if cols_has_ans[j, k] == cols_has_ans[j, answer_start_idx]:
                            answer_stop_idx = k
                        else:
                            break

                    for k in reversed(list(range(0, answer_stop_idx2 - 1))):
                        if cols_has_ans[j, k] == cols_has_ans[j, answer_stop_idx2]:
                            answer_start_idx2 = k
                        else:
                            break

                    prob_1 = probs_start[j, answer_start_idx] + \
                             probs_stop[j, answer_stop_idx]

                    prob_2 = probs_start[j, answer_start_idx2] + \
                             probs_stop[j, answer_stop_idx2]

                    if prob_2 > prob_1:
                        answer_start_idx = answer_start_idx2
                        answer_stop_idx = answer_stop_idx2

                answer = ''

                if answer_stop_idx + 1 >= input_ids.shape[1]:
                    answer_stop_idx = input_ids.shape[1] - 2

                for k in range(answer_start_idx, answer_stop_idx + 1):
                    #tok = f_tokenizer.inv_vocab[input_ids[j, k]]
                    tok = inv_vocab[input_ids[j, k]]
                    if len(tok) > 0:
                        if tok[0] != '#':
                            answer += ' '
                    #answer += str(f_tokenizer.inv_vocab[input_ids[j, k]]).replace('##', '')
                    answer += str(inv_vocab[input_ids[j, k]]).replace('##', '')

                answers.append(answer)
            for k in range(len(answers)):
                epo += 1
                f1 += f1_score(prediction=answers[k], ground_truth=answer_texts[input_range[k]])
                em += exact_match_score(prediction=answers[k], ground_truth=answer_texts[input_range[k]])
                print(answers[k], ',', answer_texts[input_range[k]])
            print(epo, 'f1:', f1 / epo, 'em:', em / epo)



if "__main__" == __name__:
    evaluation_torch_start()

