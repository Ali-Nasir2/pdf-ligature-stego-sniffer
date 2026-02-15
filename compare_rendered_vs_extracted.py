import os

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT", "")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY", "")
if not endpoint or not key:
    raise RuntimeError(
        "Missing Azure Form Recognizer credentials. Set "
        "AZURE_FORM_RECOGNIZER_ENDPOINT and AZURE_FORM_RECOGNIZER_KEY."
    )

pdf_path = "data/benign/sample.pdf"  # Change to your PDF

client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

with open(pdf_path, "rb") as f:
    poller = client.begin_analyze_document("prebuilt-read", document=f)
    result = poller.result()

for page in result.pages:
    print(f"Page {page.page_number}:")
    print("".join([line.content + "\n" for line in page.lines])) 