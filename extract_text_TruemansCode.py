import pypdfium2 as pdfium

pdf_path = "SRC_brownfield_pdfs/11545 Van Dyke St/Remediation_Investigation_-_Monitoring_Analytical_Report__RI__-_EGLE_Laboratory__3_10_22_Air_Sampling_Results_-_2203090.PDF"
pdf = pdfium.PdfDocument(pdf_path)
n_pages = len(pdf)  # get the number of pages in the document
page = pdf[2]  # load a page
# Load a text page helper
textpage = page.get_textpage()
# Extract text from the whole page
text_all = textpage.get_text_range()

with open(f"test.txt", "w") as file:
	file.write(text_all)