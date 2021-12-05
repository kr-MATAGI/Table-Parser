from Tokenization import MyTokenizer

if "__main__" == __name__:
    print("Tokenizer Test")

    testTable = [[ "트랙", "제목", "링크" , "러닝 타임", "작곡가" ],
                [ "1", "Way Back then 옛날 옛적에", "", "2:32", "정재일" ],
                [ "2", "Round I 1라운드", "", "1:20", "정재일" ],
                [ "3", "The Rope is Tied 밧줄은 묶여 있다", "", "3:19", "정재일" ],
                [ "4", "Pink Soldiers 분홍 병정", "", "0:39", "김성수" ],
                [ "5", "Hostage Crisis 인질극", "", "2:23", "김성수" ],
                [ "6", "I Remember My Name · TITLE 내 이름이 기억났어", "", "3:14", "정재일" ]]

    testTableList = []
    testTableList.append(testTable)

    testTokenizer = MyTokenizer()
    testTokenizer.LoadNewTokenizer(path="./NewTokenizer")
    testTokenizer.MakeDatasets(testTableList)

