import os
from dataclasses import dataclass
from GeminiAPIQueryLib import GeminiQuery

sourcePath = "textSource_Documents"
endPath = "CSV_Results"
foldersToCheck = []
discreteSources = []
writtenFiles = []

@dataclass
class SourceText_item:
    folderSource: str 
    fileName: str 

#===================
#   MAIN SCRIPT
#===================

#===================
#   INDEXING
#  looking up all filenames in path
for afilename in os.listdir(sourcePath):
    foldersToCheck.append(afilename)
print("Files and directories in '", sourcePath, "' :") 
# prints all files
print(foldersToCheck)

#   this gets all filenames
for afolder in foldersToCheck:
    try:
        os.mkdir(endPath + "/" + afolder)
    except OSError as error:  
        print(error) 

    for afilename in os.listdir(sourcePath + "/" + afolder):
        try:
            filesize = os.path.getsize(sourcePath + "/" + afolder + "/" + afilename)
            newEntry = SourceText_item(afolder, afilename)
            discreteSources.append(newEntry)
        except:
            print("some filesystem error")



print("=======ALL ENTRIES=======")
print(discreteSources) # KEY LIST OF ALL ENTRIES
print("=======END AREA=======")

GQuery = GeminiQuery()
for aSourceDoc in discreteSources:
    GemCSVResponse = ""
    
    try:
        print("Gemini Reading :  .." + sourcePath + "/" + aSourceDoc.folderSource + "/" + aSourceDoc.fileName)
        docPath = sourcePath + "/" + aSourceDoc.folderSource + "/" + aSourceDoc.fileName
        with open(docPath, "r") as fileReading:
            pageText = fileReading.read()
            print(pageText)
            GQuery.queryText = pageText
            GemResponse = GQuery.newCSVQuery()
            print(GemResponse)
            GemCSVResponse = GemResponse
        print(GemCSVResponse)
        
        endDocPath = endPath + "/" + aSourceDoc.folderSource + "/" + aSourceDoc.fileName
        with open(endDocPath, "w", encoding="utf-8") as fileWriting:
            fileWriting.write(GemCSVResponse)
            writtenFiles.append(aSourceDoc)
        pass
    except:
        print("Gemini Error.")
        pass

#final file writing step      
for aResultDoc in writtenFiles:
    #get the data needed to clean - report type and new name
    resultDocPath = endPath + "/" + aResultDoc.folderSource + "/" + aResultDoc.fileName
    fileparts = aResultDoc.fileName.split("_")
    reportType = fileparts[0]
    fileExtensionParts = aResultDoc.fileName.split(".")

    newFilename = fileExtensionParts[0] + ".csv"
    newDocPath = endPath + "/" + aResultDoc.folderSource + "/" + newFilename

    print("====NOW CLEANING STEP====")
    print("Cleaning:")
    print(reportType)
    print(newFilename)

    rewriteLines = []

    try:
        with open(resultDocPath, "r", encoding="utf-8") as writtenText :
            #remove the first and the last items from the text document. Also remove the header row, which will be replaced.
            allLines = writtenText.readlines()
            allLines.pop(len(allLines)-1)
            allLines.pop(0)
            rewriteLines = allLines
            pass

        #rewrite to actual csv
        with open(newDocPath, "w", encoding="utf-8") as writtenCSV :
            writtenCSV.writelines(rewriteLines)
            pass

        pass
    except:
        print("Filewrite Error.")
        pass