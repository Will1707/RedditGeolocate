import requests
import os
import ast
from bs4 import BeautifulSoup
"""
Downloding all the compressed files will take ~130GB as of the 2018-05 download
"""
DIR_PATH  = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(DIR_PATH, 'data')
FILE_PATH = os.path.join(DIR_PATH, 'data', 'downloaded.txt')
downloaded = []

def open_file():
    try: ## GET FILES ALREADY IN DATA FOLDER
        with open(FILE_PATH, "r") as file:
            tmp = file.read()
        downloaded = ast.literal_eval(tmp)
    except FileNotFoundError:
        pass
    return downloaded

def download_files(downloaded):
    """
    Downloads all the reddit submission files from pushshift individually, not in parallel
    Does not download files that have previously been downloaded
    """
    r = requests.get('http://files.pushshift.io/reddit/submissions/')
    html = r.content
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href[:4] == "./RS":
            if href[2:].split(".")[0] not in downloaded:
                downloaded.append(href[2:].split(".")[0])
                os.system(f"wget -cP {PATH} http://files.pushshift.io/reddit/submissions/{href[2:]}")
    with open(FILE_PATH, "w") as file:
        file.write(str(downloaded))

def unzip_rename():
    """
    requires GNU Parallel (sudo apt-get install parallel) and rename (sudo apt install rename)
    The uncompressed files take roughly 900GB as of the 2018-05 download
    """
    os.chdir(PATH)
    os.system("ls *.bz2 | parallel bzip2 -d")
    os.system("xz -d --threads=0 *.xz && rename 's/RS_v2/RS/g' * && rename 's/$/.json1/' *")

def main():
    downloaded = open_file()
    download_files(downloaded)
    unzip_rename()

if __name__== "__main__":
    main()
