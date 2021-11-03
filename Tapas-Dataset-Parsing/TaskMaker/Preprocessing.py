import re
import numpy as np

from random import random
import tokenization

if "__main__" == __name__:
    file = open('SplitedTapasData/splited_tapas_3.txt', 'r', encoding='ISO-8859-1')
    lines = file.read().split('\n')

    for l_, line in enumerate(lines):
        if len(line) < 5:
            continue

        tks = line.split('en.wikipedia.org/wiki/')[1].split('" table { ')[0].split('_')
        tks.pop(-1)

        doc_name = ''

        for tk in tks:
            doc_name += tk + ' '
        doc_name = doc_name.strip()

        pattern = "questions {(.*)}"
        questions = line.split('questions {')
        try:
            table_text = questions.pop(0).split('table {')[1]
        except:
            continue
            # print('error')
            # print('line:', line)
            # input()

        row_chunks = table_text.split('rows {')
        col_text = row_chunks.pop(0)

        head_chunks = col_text.split('text: \"')
        head_chunks.pop(0)

        heads = []
        for chunk in head_chunks:
            heads.append(chunk.split('\" }')[0])

        rows = []

        for chunk in row_chunks:
            row = []

            cell_chunks = chunk.split('text: \"')
            cell_chunks.pop(0)

            for cell_text in cell_chunks:
                row.append(cell_text.split('\" }')[0])

            rows.append(row)

        text_chunks = line.split('original_text: \"')

        texts = []
        for text in text_chunks:
            text_lines = text.split('" }')[0].split('. ')
            for text_ in text_lines:
                texts.append(text_ + '.')

        if len(rows) == 1:
            heads.insert(0, 'name')
            rows[0].insert(0, doc_name)

        rows.insert(0, heads)

        texts.pop(0)
        for text in texts:
            if len(text) < 20:
                continue

            table_data = [row[:] for row in rows]

            query_tokens = tokenizer.tokenize(text)
            query_tokens.insert(0, '[CLS]')
            query_tokens.insert(-1, '[SEP]')

            tokens = []
            segments = []
            row_ids = []
            col_ids = []
            row_ranks = []
            row_ranks_inv = []
            rtds = []

            ranks = []
            rank_invs = []
            # print(table_data)
            for _ in range(len(table_data)):
                ranks.append([0] * len(table_data[0]))
                rank_invs.append([0] * len(table_data[0]))

            for j in range(len(table_data[0])):
                cols = []

                is_number, _ = is_num(table_data[1][j])
                if is_number is False:
                    continue

                for r in range(1, len(table_data)):
                    is_number, num_word = is_num(table_data[r][j])
                    if is_number is True:
                        cols.append(int(num_word))
                    else:
                        cols.append(0)

                arg_idx = argsort(cols)
                arg_inv = list(reversed(argsort(cols)))

                for r in range(1, len(table_data)):
                    ranks[r][j] = arg_idx[r - 1] + 1
                    rank_invs[r][j] = arg_inv[r - 1] + 1

            is_rtd = 0

            for t, token in enumerate(query_tokens):
                if token == '[' or token == ']':
                    continue

                if 0 < t < len(query_tokens) - 1:
                    if query_tokens[t - 1] == '[' and token == 's':
                        is_rtd = 1
                        continue
                    if query_tokens[t + 1] == ']' and token == '/':
                        is_rtd = 0
                        continue
                tokens.append(token)
                segments.append(0)
                row_ids.append(0)
                col_ids.append(0)
                row_ranks.append(0)
                row_ranks_inv.append(0)
                rtds.append(is_rtd)

            for r, line in enumerate(table_data):
                for c, cell_text in enumerate(line):
                    tokens_ = tokenizer.tokenize(cell_text)

                    is_rtd = 0

                    for t, token in enumerate(tokens_):
                        if token == '[' or token == ']':
                            continue

                        if 0 < t < len(tokens_) - 1:
                            if tokens_[t - 1] == '[' and token == 's':
                                is_rtd = 1
                                continue
                            if tokens_[t + 1] == ']' and token == '/':
                                is_rtd = 0
                                continue

                        tokens.append(token)
                        segments.append(1)
                        row_ids.append(r + 1)
                        col_ids.append(c + 1)
                        row_ranks.append(ranks[r][c])
                        row_ranks_inv.append(ranks[r][c])
                        rtds.append(is_rtd)

            if len(tokens) > 512:
                continue

            if len(tokens) < 64:
                continue

            ids = tokenizer.convert_tokens_to_ids(tokens=tokens)

            length = len(ids)
            if length > max_length:
                length = max_length

            for l in range(length):
                # ids, mask, segments, row, col, rank, rank_inv
                input_ids[count, 0, l] = ids[l]
                input_ids[count, 1, l] = 1
                input_ids[count, 2, l] = segments[l]
                input_ids[count, 3, l] = row_ids[l]
                input_ids[count, 4, l] = col_ids[l]
                input_ids[count, 5, l] = row_ranks[l]
                input_ids[count, 6, l] = row_ranks_inv[l]
                input_ids[count, 7, l] = ids[l]