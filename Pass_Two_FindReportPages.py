#  imports
from dataclasses import dataclass
from datetime import datetime
import os
import shutil
from thefuzz import fuzz
from Lookups import mostCommonWords


@dataclass
class Parse_TextPage_item:
    folderSource: str 
    fileName: str 



#=======================
#===================
#   FUNCTIONS
#===================


def wm_readPage(_filepath : str) -> bool :
    threshold: int = 4
    wordSignal : float = 0.00
    allwords: list[str] = []
    referencewords: list[str] = [
        "unit",
        "dilution",
        "parameters",
        "xylene",
        "benzene",
        "ug/m3",
        "ug/kg",
        "ug/l",
        "µg/m3",
        "µg/kg",
        "µg/l"
    ] 
    #read each line to a list
    with open(_filepath, "r", encoding="utf-8") as file1:
        for line in file1:
            words = line.split()

            for aword in words :
                translator = str.maketrans('', '', "[]|!@#$^&*()?")
                    # Use translate() to remove all punctuation characters from the text
                cleanedword = aword.translate(translator)
                cleanedword = cleanedword.strip()
                if (len(cleanedword) > 1 and mostCommonWords.count(cleanedword) < 1 ):
                    #print(aword)
                    allwords.append(aword)
                    pass
                pass
            pass
        pass

    #compare list against fuzzy match reference string list. Add up signals.
    for aword in allwords : 
        if len(aword) >= 4:
            
            for refword in referencewords:
                fuzyyzig = fuzz.partial_ratio(aword.upper().strip(), refword.upper().strip())
                if fuzyyzig > 90 :
                    print(f"word is {aword} with {refword} SCORE: {fuzyyzig}")
                    wordSignal+=1
                else:
                    pass

                
            if referencewords.count(aword) > 0 :
                wordSignal+=referencewords.count(aword)
            else:
                pass
        else:
            pass

    
    print(f"Page Score: {wordSignal}")
    if wordSignal > threshold:
        return True
    else:
        return False
    #compare total signal to threshold and return bool

#=======================
#===================
#   MAIN SCRIPT
#===================

CompletedReportPagesFolder = "CompletedReport_pages"
EndStepFolder = "FlaggedPages_forGemini"
foldersToCheck = []
allFiles = []

#===================
#   INDEXING
#  looking up all filenames in path
for afilename in os.listdir(CompletedReportPagesFolder):
    foldersToCheck.append(afilename)
print("Files and directories in '", CompletedReportPagesFolder, "' :") 
# prints all files
print(foldersToCheck)
input("next?")

#   this gets all filenames
for afolder in foldersToCheck:
    try:
        os.mkdir(EndStepFolder + "/" + afolder)
    except OSError as error:  
        print(error) 

    for afilename in os.listdir(CompletedReportPagesFolder + "/" + afolder):
        try:
            
            textFile = Parse_TextPage_item(afolder, afilename)
            allFiles.append(textFile)
        except:
            print("some error")

print("=======ALL ENTRIES=======")
print(allFiles) # KEY LIST OF ALL ENTRIES
print("=======END AREA=======")

counter = 0

for _file in allFiles :
    itemFilepath = CompletedReportPagesFolder + "/" + _file.folderSource + "/" + _file.fileName
    print(itemFilepath)
    print(f"Page {counter} of {len(allFiles)}")
    StatusWord = wm_readPage(itemFilepath)
    
    if(StatusWord) : 
        destFilepath = EndStepFolder + "/" + _file.folderSource 
        print(f"Page {counter} of {len(allFiles)}")
        print("PAGE WILL BE COPIED")
        shutil.copy(itemFilepath, destFilepath)
        pass
    counter+=1
    input("continue?")
    pass