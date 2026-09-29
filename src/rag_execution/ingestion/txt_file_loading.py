#from pathlib import Path
from langchain_community.document_loaders import TextLoader


#def load_txt_file(file_path: str):
    #path = Path(file_path)

    #if not path.exists():
     #   raise FileNotFoundError(f"File not found: {path.resolve()}")

    #if path.suffix.lower() != ".txt":
     #   raise ValueError("Only .txt files are supported in this stage.")

    #loader = TextLoader(str(path), encoding="utf-8", autodetect_encoding=True)
    #documents = loader.load()
    #return documents 


 #####################################################################################


from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader, CSVLoader

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".csv"}


def load_single_file(file_path: str):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path.resolve()}")

    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}")

    if suffix == ".txt":
        loader = TextLoader(str(path), encoding="utf-8", autodetect_encoding=True)
        return loader.load()

    if suffix == ".pdf":
        loader = PyMuPDFLoader(str(path))
        return loader.load()

    if suffix == ".csv":
        loader = CSVLoader(file_path=str(path), encoding="utf-8")
        return loader.load()


def load_txt_file(file_path: str):
    return load_single_file(file_path)