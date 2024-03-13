# BROWNFIELD PDF MINER

This repository houses source code, sample files, and associated documentation.
Developers are welcome to fork the repository and contribute.

**Programming Problem:**

Our objective is to extract tabular data from a collection of diverse PDF documents and convert it into a structured format (CSV files) for further analysis.

The documents lack consistency in table placement and formatting.
They originate from various organizations and potentially exhibit different layouts.
A portion of the PDFs are scanned images, while others incorporated Optical Character Recognition (OCR) technology when scanned, and finally there are also electronically generated documents of text and markdown elements.

**Solution Designed:**

The data extraction process is implemented in a multi-step approach:

1. *File Indexing and Filtering:* Documents are categorized and potentially filtered based on specific criteria.
2. *Text Extraction:* The documents are converted into machine-readable text format using appropriate techniques.
3. *Text Analysis and Page Selection:* Textual content is analyzed to identify pages containing relevant information. This may involve the identification of keywords and their concentrations to pinpoint pages requiring detailed parsing.
4. *Table Extraction and Conversion:* Tables are extracted from the designated pages and formatted as CSV files, enabling further analysis.

Built using python. Utilized publicly available libraries detailed below and the Google Gemini LLM API.

---

## Background

A brownfield, as defined by the US Environmental Protection Agency (USEPA), “is a property the expansion, redevelopment, or reuse of which may be complicated by the presence or potential presence of a hazardous substance, pollutant, or contaminant.”  Brownfields are often abandoned or underutilized sites due to the presence of contamination or suspected contamination. 

This project and its associated code target the extraction of data from publicly available documents obtained through a collaborative effort with the Michigan Department of Environmental, Great Lakes, and Energy (EGLE). The documents encompass assessments of commercial properties within the Detroit area.

More information:

- https://detroitmi.gov/departments/buildings-safety-engineering-and-environmental-department/bseed-divisions/environmental-affairs/brownfields-redevelopment

- https://www.michigan.gov/egle/about/organization/remediation-and-redevelopment/brownfields

---

# Method

## 1. Get Documents


Download to local filesystem - PDF documents which were uploaded to cloud by partner. 

### Folder and File Naming Convention:
-	Saved in folder named by Street Address of location.
-	Each folder contains multiple PDF documents associated. Note: not every document is important to extract textual/table data from like correspondence for example.

-	Included files in repository for one Brownfield location. These can be used in your testing and development.

## 2. Index and Filter

Will be collecting attribute information that is useful to categorization for targeting and assigning unique identifier to each document that will be used for later associations.

-	Index files by name and location, generate filepath for later access. 
-	Get file sizes of each PDF.
-	Hash filename as unique identifier going forward. Used MD5 for speed but still collision-resistant.
-	Can at this point filter by filename attribute. In our example, I filtered to only filenames containing ‘BEA’ or ‘RI’ as the document type acronym.
-	Check PDF attributes. We’ll get the number of pages and check the content of the first page for text to classify text/image type PDF.  
-	Save this information and index to a CSV in script directory. This result file is used as input for future steps, so you don’t need to pre-process every time or keep objects in memory forever.


## 3. Extract Text and Content

Converting the pdf to text with script yields a standardized result.
Python exports readable text to an array of plaintext files.
- The structure comprises all files under a hashed-filename titled folder.
- Inside this folder, there is an identifier file containing the title of the original document and other attributes.
- Multiple files per page are generated for each type of media result. The file named Page_xx_Content.txt for each page represents all text.
- For each page, there is a word-map file detailing the words on the content page and their locations.

Here is an example source folder with multiple reports per address. The results subdirectory here will contain the text extracted.
[![Script Image](https://raw.githubusercontent.com/HFHyh1/Brownfield_Miner/main/folderstructure.png)]


Here is the directory structure and the plaintext files generated per document. You can see the directory is the unique hash-name of the document and each page has associated text files labeled accordingly.

Here is the example of a single page of a PDF. The word-map is the frequency and location of each word in the page.

## 4. Parse Tabular Data and Save CSVs

### Isolate Report Pages

### Format and Export CSVs

---
## Flowchart of Process

*Note: this is slightly outdated and not totally accurate. But it does illustrate the overall concepts well. Update in future.*

--- 

# Credits

**Python Libraries:**

**Special Thanks..**

My HFH Colleagues:  
Support, brainstorming, debugging help, and instrumental ideas.

George Stavrakis:  
Heavily borrowed from George's code and tutorial when creating the text extraction page. Check out his Medium profile: https://medium.com/@george.stavrakis.1996