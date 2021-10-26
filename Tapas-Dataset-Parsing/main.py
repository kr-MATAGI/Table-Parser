from Utils.SourceDataSpliter import SrcDataSpliter


### Definition
## Global
IsNeedSplitSrcData = True

if "__main__" == __name__:
    srcDataSpliter = SrcDataSpliter("SourceData/tapas/interactions.txtpb")
    srcDataSpliter.SplitSrcFile()