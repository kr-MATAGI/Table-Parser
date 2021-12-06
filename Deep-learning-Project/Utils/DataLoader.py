# Kor wiki
import xml.etree.ElementTree as ET
import ijson

# Definition
from Definition.WikiDef import *
from Definition.NamuSyntax import *

def ReadWikiDataset(filePath:str):
    print("Read Wikipedia dataset:", filePath)

    document = ET.parse(filePath)
    root = document.getroot()
    docCount = 0
    for page in root.iter(tag="page"):
        docCount += 1
        titleTag = page.find("title")
        revisionTag = page.find("revision")
        textTag = revisionTag.find("text")

        title = titleTag.text
        text = textTag.text

        if 0 == (docCount % 1000):
            print("docCount:", docCount, " title:", title)

        yield (title, text)

def ReadNamuwikiDataset(srcFilePath):
    with open(srcFilePath, mode="r", encoding="utf-8") as srcFile:
        parser = ijson.parse(srcFile)

        retValue = {}
        isNewKey = False
        for prefix, event, value in parser:
            if ('item', 'start_map') == (prefix, event):
                isNewKey = True
            elif True == prefix.endswith('.title') and True == isNewKey:
                retValue[DOC_TITLE] = value
                retValue[DOC_TEXT] = []
            elif True == prefix.endswith('.text'):
                retValue[DOC_TEXT].append(value)
            elif ('item', 'end_map') == (prefix, event):
                yield retValue
                isNewKey = False
                retValue.clear()

if "__main__" == __name__:

    # Example
    korwiki_testMode = False
    namuwiki_testMode = True


    if korwiki_testMode:
        for pageData in ReadWikiDataset("../Dataset/kor-wiki/test.xml"):
            wikipage = WikiPage(title=pageData[0],
                                text=pageData[1])

    if namuwiki_testMode:
        documentCount = 0
        for document in ReadNamuwikiDataset("../Dataset/namu-wiki/namuwiki_20210301.json"):
            documentCount += 1

            print(document[DOC_TITLE])
            print(document[DOC_TEXT])
            exit()