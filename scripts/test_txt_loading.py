#from src.rag_execution.ingestion.txt_file_loading import load_txt_file


#def main():
    #docs = load_txt_file("data/ap_policy_TXT.txt")

    #print(f"Total loaded documents: {len(docs)}")

    #if docs:
      #  print("\n--- Document Content ---\n")
       # print(docs[0].page_content)

       # print("\n--- Metadata ---\n")
       # print(docs[0].metadata)


#if __name__ == "__main__":
  #  main()


##############################################################################

from src.rag_execution.ingestion.txt_file_loading import load_single_file


def test_file(file_path: str):
    print(f"\n{'='*50}")
    print(f"Testing: {file_path}")
    print(f"{'='*50}")

    docs = load_single_file(file_path)
    print(f"Total loaded documents: {len(docs)}")

    if docs:
        print("\n--- Document Content (first 400 chars) ---\n")
        print(docs[0].page_content[:400])
        print("\n--- Metadata ---\n")
        print(docs[0].metadata)


def main():
    test_file("data/policies/ap_policy_master.txt")
    test_file("data/policies/ap_approval_matrix.csv")


if __name__ == "__main__":
    main()