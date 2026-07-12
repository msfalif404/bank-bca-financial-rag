import opendataloader_pdf
import os

os.environ["TESSDATA_PREFIX"] = os.getenv("TESSDATA_PREFIX", r"C:\Program Files\Tesseract-OCR\tessdata")

# Batch all files in one call — each convert() spawns a JVM process, so repeated calls are slow
opendataloader_pdf.convert(
    input_path=["test.pdf"],
    output_dir="output/",
    image_output="external",
    image_format="png",
)