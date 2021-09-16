### compute module
import numpy as np

### Hugging Face - transformer
from transformers import AutoTokenizer, AutoModelForMaskedLM

# Tokenizer
tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")


class NamuTokenizer:
    ### VAR ###

    ### PRIVATE ###

    ### PUBLIC ###
    '''
        @Note
            Save Data ?
        @Param
            srcDataList:[
                0: sequence_has_ans
                1: segments_has_ans
                2: masks_has_ans
                3: rows_has_ans
                4: cols_has_ans
                5: label_ids
                6: label_position
                7: label_weight
            ]
    '''
    def SaveTensorDataSet(self, count, maxLen, maxMasking, *srcDataList):
        sequence_has_ans_ = np.zeros(shape=[count, 2, maxLen], dtype=np.int32)
        segments_has_ans_ = np.zeros(shape=[count, 2, maxLen], dtype=np.int32)
        masks_has_ans_ = np.zeros(shape=[count, 2, maxLen], dtype=np.int32)
        cols_has_ans_ = np.zeros(shape=[count, 2, maxLen], dtype=np.int32)
        rows_has_ans_ = np.zeros(shape=[count, 2, maxLen], dtype=np.int32)

        label_ids_ = np.zeros(shape=[count, 2, maxMasking], dtype=np.int32)
        label_position_ = np.zeros(shape=[count, 2, maxMasking], dtype=np.int32)
        label_weight_ = np.zeros(shape=[count, 2, maxMasking], dtype=np.float32)

        for idx in range(count):
            sequence_has_ans_[idx] = srcDataList[0][idx]
            segments_has_ans_[idx] = srcDataList[1][idx]
            masks_has_ans_[idx] = srcDataList[2][idx]
            rows_has_ans_[idx] = srcDataList[3][idx]
            cols_has_ans_[idx] = srcDataList[4][idx]

            label_ids_[idx] = srcDataList[5][idx]
            label_position_[idx] = srcDataList[6][idx]
            label_weight_[idx] = srcDataList[7][idx]

        np.save('sequence_table_pre3', sequence_has_ans_)
        np.save('segments_table_pre3', segments_has_ans_)
        np.save('masks_table_pre3', masks_has_ans_)
        np.save('rows_table_pre3', rows_has_ans_)
        np.save('cols_table_pre3', cols_has_ans_)

        np.save('label_ids3', label_ids_)
        np.save('label_position3', label_position_)
        np.save('label_weight3', label_weight_)