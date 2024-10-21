# To read the PDF
import PyPDF2
# To analyze the PDF layout and extract text
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
# To extract text from tables in PDF
import pdfplumber
# To extract the images from the PDFs
from PIL import Image
from pdf2image import convert_from_path
# To perform OCR to extract text from images 
import pytesseract 
# To remove the additional created files
import os
from dataclasses import dataclass
from datetime import datetime
import string
from Lookups import mostCommonWords

import string

@dataclass
class Parse_PDF_item:
    folderSource: str 
    fileName: str 
    fileSize: float #this is pulled in bytes, so divide by 1,000,000 to get megabytes
    fullFilePath: str
    totalPages: int
    isPDFText: bool # by checking first page for text 
    hashValue: str 


class TextExtractor:
    pdf_path: str 
    filename: str
    parentFolder: str 
    hashedName: str 
    pagesDoc: int
    all_files: list[Parse_PDF_item]

    def __init__(self, inputItems: list[Parse_PDF_item]) -> None:
        self.all_files = inputItems
        pass

    #  FUNCTIONS
    def remove_punctuation(self, input_string):
        # Make a translator object to remove all punctuation except /
        translator = str.maketrans('', '', string.punctuation.replace('/', '').replace('.', '').replace(',', '.-'))
        # Use the translator object to remove punctuation
        no_punct = input_string.translate(translator)
        return no_punct

    # Create a function to extract text

    def text_extraction(self, element):
        # Extracting the text from the in-line text element
        line_text = element.get_text()
        
        # Find the formats of the text
        # Initialize the list with all the formats that appeared in the line of text
        line_formats = []
        for text_line in element:
            if isinstance(text_line, LTTextContainer):
                # Iterating through each character in the line of text
                for character in text_line:
                    if isinstance(character, LTChar):
                        # Append the font name of the character
                        line_formats.append(character.fontname)
                        # Append the font size of the character
                        line_formats.append(character.size)
        # Find the unique font sizes and names in the line
        format_per_line = list(set(line_formats))
        
        # Return a tuple with the text in each line along with its format
        return (line_text, format_per_line)

    # Create a function to crop the image elements from PDFs
    def crop_image(self, element, pageObj):
        # Get the coordinates to crop the image from the PDF
        [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1] 
        # Crop the page using coordinates (left, bottom, right, top)
        pageObj.mediabox.lower_left = (image_left, image_bottom)
        pageObj.mediabox.upper_right = (image_right, image_top)
        # Save the cropped page to a new PDF
        cropped_pdf_writer = PyPDF2.PdfWriter()
        cropped_pdf_writer.add_page(pageObj)
        # Save the cropped PDF to a new file
        with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
            cropped_pdf_writer.write(cropped_pdf_file)

    # Create a function to convert the PDF to images
    def convert_to_images(self, input_file,):
        images = convert_from_path(input_file)
        image = images[0]
        output_file = "PDF_image.png"
        image.save(output_file, "PNG")

    # Create a function to read text from images
    def image_to_text(self, image_path):
        # Read the image
        img = Image.open(image_path)
        # Extract the text from the image
        text = pytesseract.image_to_string(img)
        return text

    # Extracting tables from the page

    def extract_table(self, pdf_path, page_num, table_num):
        # Open the pdf file
        pdf = pdfplumber.open(pdf_path)
        # Find the examined page
        table_page = pdf.pages[page_num]
        # Extract the appropriate table
        table = table_page.extract_tables()[table_num]
        return table

    # Convert table into the appropriate format
    def table_converter(self, table):
        table_string = ''
        # Iterate through each row of the table
        for row_num in range(len(table)):
            row = table[row_num]
            # Remove the line breaker from the wrapped texts
            cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
            # Convert the table into a string 
            table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
        # Removing the last line break
        table_string = table_string[:-1]
        return table_string

    def Logger(self, filename, linesToWrite)  :
        with open(filename, "w", encoding="utf-8") as file1:
            for line in linesToWrite :
                file1.write(line)

    def count_word_occurrences_with_locations(self, Mapinput_file_path, Mapoutput_file_path):
        # Open the input text file
        with open(Mapinput_file_path, 'r', encoding="utf-8") as file:
            # Read the content of the file
            content = file.read()

            # Split the content by space and new line
            words = content.split()

            # Create a dictionary to store word occurrences and their locations
            word_data = {}
            for index, word in enumerate(words):
                
                translator = str.maketrans('', '', "[]|!@#$^&*()?")
                # Use translate() to remove all punctuation characters from the text
                cleanedword = word.translate(translator)
                cleanedword = cleanedword.strip()
                if (len(cleanedword) > 1 and mostCommonWords.count(cleanedword) < 1 ):
                    cleanedword = cleanedword.lower()  # Convert to lowercase to treat words case-insensitively
                    if cleanedword in word_data:
                        word_data[cleanedword]['count'] += 1
                        word_data[cleanedword]['locations'].append(index)
                    else:
                        word_data[cleanedword] = {'count': 1, 'locations': [index]}

        # Convert the word_data dictionary to the desired output format
        result_data = [{"word": self.remove_punctuation(word), "count": data['count'], "locations": data['locations']} for word, data in word_data.items()]

        # Write the results to the output text file
        with open(Mapoutput_file_path, 'w', encoding="utf-8") as output_file:
            for result in result_data:
                output_file.write(f"{result['word']}: {result['count']}, {result['locations']}\n")

    def MainFunc(self, fPDFPath, fPDFFilename, fPDFHash) :
        #  MAIN SCRIPT 
        print(f"{datetime.now()} -- processing doc: " + fPDFPath + fPDFFilename)
        # create a PDF file object
        pdfFileObj = open(fPDFPath + fPDFFilename, 'rb')
        # create a PDF reader object
        pdfReaded = PyPDF2.PdfReader(pdfFileObj)

        # Create the dictionary to extract text from each image
        text_per_page = {}
        # We extract the pages from the PDF
        for pagenum, page in enumerate(extract_pages(fPDFPath + fPDFFilename)):
            print(f"processing page - {pagenum}")
            # Initialize the variables needed for the text extraction from the page
            pageObj = pdfReaded.pages[pagenum]
            page_text = []
            line_format = []
            text_from_images = []
            text_from_tables = []
            page_content = []
            # Initialize the number of the examined tables
            table_num = 0
            first_element= True
            table_extraction_flag= False
            # Open the pdf file
            pdf = pdfplumber.open(fPDFPath + fPDFFilename)
            # Find the examined page
            page_tables = pdf.pages[pagenum]
            # Find the number of tables on the page
            tables = page_tables.find_tables()


            # Find all the elements
            page_elements = [(element.y1, element) for element in page._objs]
            # Sort all the elements as they appear in the page 
            page_elements.sort(key=lambda a: a[0], reverse=True)

            # Find the elements that composed a page
            for i,component in enumerate(page_elements):
                # Extract the position of the top side of the element in the PDF
                pos= component[0]
                # Extract the element of the page layout
                element = component[1]
                
                # Check if the element is a text element
                if isinstance(element, LTTextContainer):
                    # Check if the text appeared in a table
                    if table_extraction_flag == False:
                        # Use the function to extract the text and format for each text element
                        (line_text, format_per_line) = self.text_extraction(element)
                        # Append the text of each line to the page text
                        page_text.append(line_text)
                        # Append the format for each line containing text
                        line_format.append(format_per_line)
                        page_content.append(line_text)
                    else:
                        # Omit the text that appeared in a table
                        pass

                # Check the elements for images
                if isinstance(element, LTFigure):
                    # Crop the image from the PDF
                    self.crop_image(element, pageObj)
                    # Convert the cropped pdf to an image
                    self.convert_to_images('cropped_image.pdf')
                    # Extract the text from the image
                    image_text = self.image_to_text('PDF_image.png')
                    text_from_images.append(image_text)
                    page_content.append(image_text)
                    # Add a placeholder in the text and format lists
                    page_text.append('image')
                    line_format.append('image')

                # Check the elements for tables
                if isinstance(element, LTRect):
                    # If the first rectangular element
                    if first_element == True and (table_num+1) <= len(tables):
                        # Find the bounding box of the table
                        lower_side = page.bbox[3] - tables[table_num].bbox[3]
                        upper_side = element.y1 
                        # Extract the information from the table
                        table = self.extract_table(fPDFPath + fPDFFilename, pagenum, table_num)
                        # Convert the table information in structured string format
                        table_string = self.table_converter(table)
                        # Append the table string into a list
                        text_from_tables.append(table_string)
                        page_content.append(table_string)
                        # Set the flag as True to avoid the content again
                        table_extraction_flag = True
                        # Make it another element
                        first_element = False
                        # Add a placeholder in the text and format lists
                        page_text.append('table')
                        line_format.append('table')

                        # Check if we already extracted the tables from the page

                        if element.y0 >= lower_side and element.y1 <= upper_side:
                            pass
                        elif not isinstance(page_elements[i+1][1], LTRect):
                            table_extraction_flag = False
                            first_element = True
                            table_num+=1


            # Create the key of the dictionary
            dctkey = 'Page_'+str(pagenum+1)
            # Add the list of list as the value of the page key
            text_per_page[dctkey]= [page_text, line_format, text_from_images,text_from_tables, page_content]

            self.Logger(f"SRC_brownfield_pdfs/{self.parentFolder}/results/{self.hashedName}/{self.hashedName}_Ident.txt",[self.filename, "  |  " + self.parentFolder, f" | Pages: {self.pagesDoc}", f" | is text: {self.IsTextDoc}"])
            #print(result)
            # Display the content of the page
            result = ''.join(text_per_page[dctkey][0])
            print("page text")
            self.Logger(f"SRC_brownfield_pdfs/{self.parentFolder}/results/{self.hashedName}/{self.hashedName}_{dctkey}_text.txt",result)
            #print(result)

            print("formatting")
            result = ''.join(str(v) for v in text_per_page[dctkey][1])
            self.Logger(f"SRC_brownfield_pdfs/{self.parentFolder}/results/{self.hashedName}/{self.hashedName}_{dctkey}_formatting.txt",result)
            #print(text_per_page[dctkey][1])

            print("text image")
            result = ''.join(text_per_page[dctkey][2])
            self.Logger(f"SRC_brownfield_pdfs/{self.parentFolder}/results/{self.hashedName}/{self.hashedName}_{dctkey}_image.txt",result)
            #print(result)

            print("text tables")
            result = ''.join(text_per_page[dctkey][3])
            self.Logger(f"SRC_brownfield_pdfs/{self.parentFolder}/results/{self.hashedName}/{self.hashedName}_{dctkey}_tables.txt",result)
            #print(result)

            print("page content")
            result = ''.join(text_per_page[dctkey][4])
            self.Logger(f"SRC_brownfield_pdfs/{self.parentFolder}/results/{self.hashedName}/{self.hashedName}_{dctkey}_content.txt",result)
            #print(result)

            #finally create a wordmap of the page contents
            print("creating wordmap")
            self.count_word_occurrences_with_locations(f"SRC_brownfield_pdfs/{self.parentFolder}/results/{self.hashedName}/{self.hashedName}_{dctkey}_content.txt", f"SRC_brownfield_pdfs/{self.parentFolder}/results/{self.hashedName}/{self.hashedName}_{dctkey}_wordmap.txt")

        # Closing the pdf file object
        pdfFileObj.close()

        # Deleting the additional files created
        os.remove('cropped_image.pdf')
        os.remove('PDF_image.png')


    def ProcessExtractPDFs(self) -> bool:
        totalFiles = len(self.all_files)
        filecounter = 0
        for document in self.all_files :
                filecounter+=1
                print(f"processing file ({filecounter} of {totalFiles})")
                self.filename = document.fileName
                self.parentFolder = document.folderSource
                self.hashedName = document.hashValue
                self.pdf_path = document.fullFilePath
                self.pagesDoc = document.totalPages
                self.IsTextDoc = document.isPDFText
                self.MainFunc(('SRC_brownfield_pdfs/' + document.folderSource + '/'), document.fileName, document.hashValue)
        try:
            
            return True
        except Exception as e:
            print(e)
            return False
        