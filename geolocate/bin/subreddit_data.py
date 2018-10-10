import jsonlines
import pymongo
import os
from posts import MongoDatabase


"""
This takes a very long time to run - in the order of a few days 
"""

DIR_PATH  = os.path.dirname(os.path.realpath(__file__))
FILE_PATH = os.path.join(DIR_PATH, "data")
MONGO_CLIENT = 'localhost'
DB_NAME = 'reddit'
COLLECTION_NAME = 'subreddits'
YEAR_START = 5 # >= 2005
YEAR_END = 19 # <= 2018
MONTH_START = 1 # >= January
MONTH_END = 13 # <= December

def initialise():
    """
    Initialises mongodb
    """
    mongodb = MongoDatabase(MONGO_CLIENT, DB_NAME)
    if COLLECTION_NAME not in mongodb.get_collections():
        mongodb.collection(COLLECTION_NAME, 'name')
    return mongodb

def create_dict(reader):
    """
    Creates a dict from the json1 line
    """
    obj = reader.read(allow_none=False, skip_empty=True)
    data = insert = {}
    for key in obj:
        data[key] = obj[key]
    return data

def create_update(data, mongodb):
    """
    If a subreddit is in the database it updates the submission count, total no. of comments
    and the total score. If the subreddit is not in the database it creates a new document
    """
    sub = data['subreddit']
    if "." in sub:
        sub = sub.replace(".", "")
    found = mongodb.find(COLLECTION_NAME, 'name', sub)
    if found.count(with_limit_and_skip=True) == 0:
        insert = {
            "name": sub,
            "id": data['subreddit_id'],
            "submissions": 1,
            "total_comments": data['num_comments'],
            "total_score": data['score']
        }
        mongodb.insert(COLLECTION_NAME, insert)
    else:
        mongodb.update_three(COLLECTION_NAME, "name", sub, "submissions", 1, "total_comments",
                            data['num_comments'], "total_score", data['score'])

def main():
    mongodb = initialise()
    for year in range(YEAR_START, YEAR_END):
        for month in range(MONTH_START, MONTH_END):
            file_name = f'RS_20{year:02}-{month:02}.json1'
            file = os.path.join(FILE_PATH, file_name)
            print(file_name)
            try:
                with jsonlines.open(file, mode='r') as reader:
                    while True:
                        try:
                            data = create_dict(reader)
                            create_update(data, mongodb)
                        except EOFError:
                            print("EOF")
                            obj = {}
                            break
                        except Exception as e:
                            print(e)
            except FileNotFoundError:
                print("File missing")

if __name__== "__main__":
    main()
