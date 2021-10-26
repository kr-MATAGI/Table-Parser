import re


class SrcDataSpliter:
    ### VAR ###
    srcFilePath = None
    RE_SEPARTOR = r"^id: \"[^\"]+\""

    ### PRIVATE ###
    def __init__(self, srcFilePath):
        print("INIT - Path: ", srcFilePath)
        SrcDataSpliter.srcFilePath = srcFilePath

    ### PUBLIC ###
    @classmethod
    def SplitSrcFile(self, fileName:str="splited_tapas_", extention:str=".txtpb", limitBytes:int=1073741824):
        if not SrcDataSpliter.srcFilePath:
            print("ERROR - Plz set file path,", self.srcFilePath)
            return

        with open(self.srcFilePath, mode="r", encoding="utf-8") as srcFile:
            writeFileIdx = 1
            writeFileName = fileName + str(writeFileIdx) + extention
            writeRootPath = "SplitedData/tapas"
            writeFile = open(writeRootPath + "/" + writeFileName, mode="w", encoding="utf-8")

            writedFileBytes = 0
            readDataStr = ""
            readLineCount = 0
            while True:
                srcLine = srcFile.readline()
                readLineCount += 1

                readDataStr += (srcLine + "\n")
                writedFileBytes += len(srcLine.encode())
                if not srcLine:
                    print("Complete - End of File")
                    break

                if 0 == (readLineCount % 5000):
                    print("Read Line Count: ", readLineCount, "readBytes: ", writedFileBytes)
                    print(srcLine)

                if re.search(self.RE_SEPARTOR, srcLine):
                    if limitBytes <= writedFileBytes:
                        print("Read to Next File - idx: ", writeFileIdx+1)
                        print("limit: ", limitBytes, "currBytes: ", writedFileBytes)
                        ## Ready to next file
                        # Write data
                        writeFile.write(readDataStr)
                        readDataStr = ""

                        # Current file close
                        writeFile.close()
                        writedFileBytes = 0

                        # Make next file
                        writeFileIdx += 1
                        writeFileName = fileName + str(writeFileIdx) + extention
                        writeFile = open(writeRootPath + "/" + writeFileName, mode="w", encoding="utf-8")

            # Close File
            writeFile.write(readDataStr)
            writeFile.close()

