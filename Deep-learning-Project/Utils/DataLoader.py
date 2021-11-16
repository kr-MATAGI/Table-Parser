# Kor wiki
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, dump, ElementTree

# Namuwiki
import ijson

# Definition
from Definition.WikiDef import *

def ReadWikiDataset(filePath:str):
    print("Read Wikipedia dataset:", filePath)

    document = ET.parse(filePath)
    root = document.getroot()
    for page in root.iter(tag="page"):
        titleTag = page.find("title")
        revisionTag = page.find("revision")
        textTag = revisionTag.find("text")

        title = titleTag.text
        text = textTag.text

        yield (title, text)

if "__main__" == __name__:

    # Example
    for pageData in ReadWikiDataset("../Dataset/kor-wiki/test.xml"):
        wikipage = WikiPage(title=pageData[0],
                            text=pageData[1])