from eunjeon import Mecab
from tokenizers import ByteLevelBPETokenizer

class MyTokenizer:
    def __init__(self):
        # Mecab
        self.mecab = Mecab(dicpath="C:/mecab/mecab-ko-dic").morphs
        print("Mecab Check: 안녕하세요, 최재훈 입니다. ->", self.mecab("안녕하세요, 최재훈 입니다."))

        # BPE Tokenizer
        self.tokenizer = ByteLevelBPETokenizer()
        print("Tokenizer Init - Using Mecab (eunjeon)")

    def Tokenization(self, sentenceList):
        total_morph = []

        for sent in sentenceList:
            morph_sentece = []
            count = 0
            for token_mecab in self.mecab(sent):
                token_mecab_save = token_mecab
                if count > 0:
                    token_mecab_save = "##" + token_mecab_save
                    morph_sentece.append(token_mecab_save)
                else:
                    morph_sentece.append(token_mecab_save)
                    count += 1
            total_morph.append(morph_sentece)

        return total_morph

    def TrainTokenizer(self, corpus_files, vocab_size=32000, min_frequency=5, show_progress=True):
        self.tokenizer.train(files=corpus_files,
                             vocab_size=vocab_size,
                             min_frequency=min_frequency,
                             show_progress=show_progress)
        print("Train Complete !")


if "__main__" == __name__:
    myTokenizer = MyTokenizer()

    testSent = ["안녕하세요 저는 최재훈입니다.",
                "국물이 끝내줘요~",
                "아브라카다브라",
                "이것이 과연 어떻게 토큰화 될것인가?",
                "나는 오늘 아침밥을 먹었다."]
    ans = myTokenizer.Tokenization(testSent)

    for a in ans:
        print(a)
