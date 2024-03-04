#  imports
from dataclasses import dataclass
from datetime import datetime
import os
import csv
from PyPDF2 import PdfReader
import hashlib

from ExtractTxtClass import TextExtractor

#  code starts here
#=======================
#===================
#   DATACLASSES
#===================
@dataclass
class PDF_item:
    folderSource: str 
    fileName: str 
    fileSize: float #this is pulled in bytes, so divide by 1,000,000 to get megabytes

# let's add a hash and image or text flag to a different data class and only pull in BEA
# Can relate pages of text later to the file using this hash. MD5 hash is fine and short.
@dataclass
class Parse_PDF_item:
    folderSource: str 
    fileName: str 
    fileSize: float #this is pulled in bytes, so divide by 1,000,000 to get megabytes
    fullFilePath: str
    totalPages: int
    isPDFText: bool # by checking first page for text 
    hashValue: str # will hash MD5, shouldnt be any collisions

#=======================
#===================
#   PRESET VARS
#===================
fileconnectPath = "brownfield_pdfs"
foldersToCheck = []
discretePDFs = []
resultFilename = "ProcessedObj_pdfs.csv"

#=======================
#===================
#   FUNCTIONS
#===================

# for writing text logs for results
def Logger( filename, linesToWrite)  :
    with open(filename, "w") as file1:
        for line in linesToWrite :
            file1.write(line + "\n")


def PDFCheckPageTotal(filepath) -> int :
    reader = PdfReader(filepath) 
    return len(reader.pages)

def PDFReadText(filepath) -> bool:    
    reader = PdfReader(filepath) 
    page = reader.pages[0]
    text = page.extract_text() 
    # empty or image pages will have a length of zero
    if (len(text) > 0):
        return True
    else:
        return False



#=======================
#===================
#   MAIN SCRIPT
#===================

#===================
#   INDEXING
#  looking up all filenames in path
for afilename in os.listdir(fileconnectPath):
    foldersToCheck.append(afilename)
print("Files and directories in '", fileconnectPath, "' :") 
# prints all files
print(foldersToCheck)

#   this gets all filenames
for afolder in foldersToCheck:
    try:
        os.mkdir(fileconnectPath + "/" + afolder + "/results")
    except OSError as error:  
        print(error) 

    for afilename in os.listdir(fileconnectPath + "/" + afolder):
        try:
            filesize = os.path.getsize(fileconnectPath + "/" + afolder + "/" + afilename)
            pdfEntry = PDF_item(afolder, afilename, filesize)
            discretePDFs.append(pdfEntry)
        except:
            print("some error")

print("=======ALL ENTRIES=======")
print(discretePDFs) # KEY LIST OF ALL ENTRIES
print("=======END AREA=======")


#===================
#   BASIC INVESTIGATION OF SIZE 
filesizes = []
for anItem in discretePDFs :
    filesizes.append(str(anItem.fileSize / 1000000) + "," + anItem.fileName + f",{anItem.folderSource}")
#Logger("filesizes.txt", filesizes)

useFulFiles = []
# ^^^^^^^^^^^^^^^^^^
# Now can start using this filtered list.
for anItem in discretePDFs :
    if ( (anItem.fileName.find("__BEA__") > 0) or (anItem.fileName.find("__RI__") > 0) ):
        useFulFiles.append(anItem)
# just the Remediation investigation and BEA items now.
print(f"Total RI and BEA forms -> {len(useFulFiles)}")


hashedAndPrepped = []

for anItem in useFulFiles:
    itemFullFilename = fileconnectPath + "/" + anItem.folderSource + "/" + anItem.fileName
    itemPageSize = PDFCheckPageTotal(itemFullFilename)
    itemHash = hashlib.md5(itemFullFilename.encode())
    itemHashHex = itemHash.hexdigest()
    print(f"{itemFullFilename} is {itemPageSize} pages long with a hash of: {itemHashHex}")
    firstpageText = PDFReadText(itemFullFilename)
    print("Is PDF text ? : " + str(firstpageText))
    print("==")
    makeHashed = Parse_PDF_item(anItem.folderSource, anItem.fileName, anItem.fileSize, itemFullFilename, itemPageSize, firstpageText, itemHashHex)
    hashedAndPrepped.append(makeHashed)
    try:
        os.mkdir(fileconnectPath + "/" + makeHashed.folderSource + "/results/" + makeHashed.hashValue)
    except OSError as error:  
        print(error) 

print()
print()
print("built list of objects: ")
print(len(hashedAndPrepped))

HusefulFileSizes = []
for anItem in hashedAndPrepped:
    HusefulFileSizes.append(str(anItem.fileSize / 1000000) + "," + anItem.fileName + f",{anItem.folderSource},{anItem.fullFilePath},{str(anItem.totalPages)},{str(anItem.isPDFText)},{anItem.hashValue}" )
Logger(resultFilename, HusefulFileSizes)
#=======================
#===================
#   END
#===================
print("done - > Look for results in file: " + resultFilename)
elfin = input("Continue.. stop here to read just the index")

Extractor = TextExtractor(hashedAndPrepped)
digResult = Extractor.ProcessExtractPDFs()
print(digResult)
elfin = input("End..")