from eunjeon import Mecab

class TableDetailScorer:
    ### VAR ###


    ### PRIVATE ###


    ### PUBLIC ###
    def __init__(self):
        self.tagger = Mecab()
        self.Bi_character_feature = []
        print('INIT TableDetailScorer')

    '''
        @Param
            table
    '''
    def GetFeature(self, query):
        self.Bi_character_feature = []

        TKs = self.tagger.morphs(query)

        for TK in TKs:
            if 1 < len(TK):
                for idx in range(1, len(TK)):
                    self.Bi_character_feature.append(str(TK[idx-1:idx+1]))

    '''
        @Param
            sequence
    '''
    def GetParagraphScore(self, paragraph):
        score = 0

        for ch_feat in self.Bi_character_feature:
            if paragraph.find(ch_feat) != -1:
                score += 1
        if 0 == len(self.Bi_character_feature):
            return 1

        return 1 + (score / len(self.Bi_character_feature))