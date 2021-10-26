import re

filePath = "./snapshot.txtpb"
with open(filePath, "r") as srcFile:
    while True:
        srcLine = srcFile.readline()

        if not srcLine:
            break

        srcLine = srcLine.replace("\\240", " ") # space
        srcLine = srcLine.replace("\\040", " ") # space
        srcLine = srcLine.replace("\\041", "!")
        srcLine = srcLine.replace("\\042", "\"")
        srcLine = srcLine.replace("\\043", "#")
        srcLine = srcLine.replace("\\044", "$")
        srcLine = srcLine.replace("\\045", "%")
        # 046 -> &amp;
        srcLine = srcLine.replace("\\047", "'")
        srcLine = srcLine.replace("\\050", "(")
        srcLine = srcLine.replace("\\051", ")")
        srcLine = srcLine.replace("\\052", "*")
        srcLine = srcLine.replace("\\053", "+")
        srcLine = srcLine.replace("\\054", ",")
        srcLine = srcLine.replace("\\055", "-")
        srcLine = srcLine.replace("\\056", ".")
        srcLine = srcLine.replace("\\057", "/")
        srcLine = srcLine.replace("\\060", "0")

        srcLine = srcLine.replace("\\071", "9")
        srcLine = srcLine.replace("\\072", ":")
        srcLine = srcLine.replace("\\073", ";")
        srcLine = srcLine.replace("\\074", "<")
        srcLine = srcLine.replace("\\075", "=")
        srcLine = srcLine.replace("\\076", ">")
        srcLine = srcLine.replace("\\077", "?")

        srcLine = srcLine.replace("\\100", "@")
        srcLine = srcLine.replace("\\101", "A")
        srcLine = srcLine.replace("\\132", "Z")
        srcLine = srcLine.replace("\\133", "[")
        srcLine = srcLine.replace("\\134", "\\")
        srcLine = srcLine.replace("\\135", "]")
        srcLine = srcLine.replace("\\136", "^")
        srcLine = srcLine.replace("\\137", "_")
        srcLine = srcLine.replace("\\140", "`")
        srcLine = srcLine.replace("\\141", "a")

        srcLine = srcLine.replace("\\172", "z")
        srcLine = srcLine.replace("\\173", "{")
        srcLine = srcLine.replace("\\174", "|")
        srcLine = srcLine.replace("\\175", "}")
        srcLine = srcLine.replace("\\176", "~")

        srcLine = re.sub(r"\\[0-9]+", "", srcLine)
        srcLine = srcLine.replace("\\n", " ")
        print(srcLine)


