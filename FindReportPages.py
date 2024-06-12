#  imports
from dataclasses import dataclass
from datetime import datetime
import os
import csv
import hashlib
from thefuzz import fuzz
from thefuzz import process
import shutil

#=======================
#===================
#   DATACLASSES
#===================

@dataclass
class Parse_PDF_item:
    folderSource: str 
    fileName: str 
    fileSize: float #this is pulled in bytes, so divide by 1,000,000 to get megabytes
    fullFilePath: str
    totalPages: int
    isPDFText: bool # by checking first page for text 
    hashValue: str 

@dataclass
class Page_WordMap:
    wordItem: str
    wordFreq: int
    pageNum: int 

@dataclass
class Page_toSave:
    path: str 
    docHash: str 
    filename: str
    streetAddress: str


#=======================
#===================
#   PRESET VARS
#===================
fileconnectPath = "SRC_brownfield_pdfs"
discretePDFs = []
PagesToSave = []
sourceFilename = "Processed_PDF_Index.csv"

#=======================
#===================
#   FUNCTIONS
#===================

# for writing text logs for results
def Logger( filename, linesToWrite)  :
    with open(filename, "w") as file1:
        for line in linesToWrite :
            file1.write(line + "\n")
    pass

#  open csv and load those lines as pdf items. Load these to a master List.
def Read_CSV_toList() :
    with open(sourceFilename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)
            discretePDFs.append(Parse_PDF_item(row[2],row[1],row[0],row[3],row[4],row[5],row[6]))
    pass

#  check hash named folder
def wm_getPages(pdfdoc: Parse_PDF_item) -> list[str] :
    counter = 0 
    pageListReturn : list[str] = []
    print(pdfdoc.fullFilePath)
    while counter < int(pdfdoc.totalPages) :
        pageListReturn.append(f"SRC_brownfield_pdfs/{pdfdoc.folderSource}/results/{pdfdoc.hashValue}/{pdfdoc.hashValue}_Page_{counter}_wordmap.txt")
        counter+=1
    return pageListReturn

#  check each page wordmap
def wm_readPage(_filepath : str) -> bool :
    threshold: int = 2
    wordSignal : float = 0.00
    allwords: list[str] = []
    referencewords: list[str] = [
        "benzene",
        "methane",
    ] 
    #read each line to a list
    with open(_filepath, "r", encoding="utf-8") as file1:
        for line in file1:
            word = line.split(":", 1)
            allwords.append(word[0])
        pass

    #compare list against fuzzy match reference string list. Add up signals.
    for aword in allwords : 
        if len(aword) > 5:
            for refword in referencewords:
                fuzyyzig = fuzz.partial_ratio(aword, refword)
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
    if wordSignal > 5:
        return True
    else:
        return False
    #compare total signal to threshold and return bool

# CONFIG FUNCTION
# the below function checks name of document to classify the type of report. Expand and change as required.
def CheckReportType(_filename : str) -> str : 
    if (fuzz.token_set_ratio(_filename, "AKT_Peerless") > 99) :
        print("this file is akt type")
        return "AKT"
    
    elif (fuzz.token_set_ratio(_filename, "EGLE_Laboratory") > 99) :
        print("this file is EGLE type")
        return "EGLE"
    
    elif (fuzz.token_set_ratio(_filename, "Fibertec_Environmental_Services") > 99) :
        print("this file is Fibertec type")
        return "FIBERTEC"
    
    elif (fuzz.token_set_ratio(_filename, "ASTI_Environmental") > 99) :
        print("this file is Fibertec type")
        return "ASTI"
    
    elif (fuzz.token_set_ratio(_filename, "Environmental_Resources_Group") > 99) :
        print("this file is Environmental Resources Group type")
        return "ERG"
    
    elif (fuzz.token_set_ratio(_filename, "Mannik_Smith_Group") > 99) :
        print("this file is Mannik Smith type")
        return "MSG"
    
    else :
        print ("unknown report type")
        return "OTHER"
    pass

#=======================
#===================
#   MAIN SCRIPT
#===================

#===================


print("begin script..")
#open csv, read to list, check folders in list, read wordmap for each page in each folder, note the pages that need further investigation 
Read_CSV_toList()

for listItem in discretePDFs :
    print("===")
    print(listItem.totalPages)
    allPages = wm_getPages(listItem)

    counter = 0
    #now process each page
    for apage in allPages:
        statusPage = wm_readPage(apage)
        if statusPage:
            newPageEntry = Page_toSave(
                f"SRC_brownfield_pdfs/{listItem.folderSource}/results/{listItem.hashValue}/{listItem.hashValue}_Page_{counter}_content.txt",
                f"{listItem.hashValue}",
                f"{CheckReportType(listItem.fileName)}_{listItem.hashValue}_p{counter}.txt",
                f"{listItem.folderSource}"
            )
            PagesToSave.append(newPageEntry)
        else:
            pass
        print(f"page end: {counter}")
        counter +=1

print(PagesToSave)
for doc in PagesToSave:
    try:
        os.mkdir(f"CompletedReport_pages/{doc.streetAddress}")
    except FileExistsError:
        print("Already Path")
        
    shutil.copy(doc.path, f"CompletedReport_pages/{doc.streetAddress}/{doc.filename}")
    print("File copied successfully.")
    try:
        pass
 
    # If source and destination are same
    except shutil.SameFileError:
        print("Source and destination represents the same file.")
    
    # If there is any permission issue
    except PermissionError:
        print("Permission denied.")
    
    # For other errors
    except:
        print("Error occurred while copying file.")
    
#=======================
#===================
#   END
#===================
print("done - > Look for results in file: " )
elfin = input()