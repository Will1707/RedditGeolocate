import jsonlines
import pymongo
import os
from posts import MongoDatabase, Post, UserContent, Geolocation, LocationInfo

SUBREDDIT_NAME = 'earthporn'
SUBREDDIT_ID = 't5_2sbq3' # earthporn
YEAR_START = 5 # >= 2005
YEAR_END = 19 # <= 2018
MONTH_START = 1 # >= January
MONTH_END = 13 # <= December
API_COUNT = 10000
DIR_PATH  = os.path.dirname(os.path.realpath(__file__))
FILE_PATH = os.path.join(DIR_PATH, 'data')
FILE_NAMES = [os.path.join(FILE_PATH, f'RS_20{year:02}-{month:02}.json1') 
              for year in range(YEAR_START, YEAR_END) for month in range(MONTH_START, MONTH_END)]

def initialise():
    """
    Sets up mongodb and sets the initial api count of the geocoder
    """
    mongodb = MongoDatabase(SUBREDDIT_NAME)
    if 'complete_post' not in mongodb.get_collections():
        mongodb.collection('complete_post', 'id')
    if 'post' not in mongodb.get_collections():
        mongodb.collection('post', 'geoJSON.id')
    Geolocation(None).set_api_count(API_COUNT)
    return mongodb

def get_post_data(reader):
    """
    Creates a dict from the json1 line
    """
    obj = reader.read(allow_none=False, skip_empty=True)
    return {key:value for (key,value) in obj.items() if SUBREDDIT_ID in obj.values()}

def get_add_data(post_data):
    """
    Geolocates the post, finds the user's other image posts and gets the closest
    wikipedia artile
    """
    post = None
    user = None
    geo = None
    loc_info = None
    add_data = None
    try:
        created = post_data['created']
    except KeyError:
        created = post_data['created_utc']
    post = Post(post_data['id'], created, post_data['url'], post_data['author'],
                post_data['title'], post_data['score'], post_data['num_comments'])
    user = UserContent(post.author)
    geo = Geolocation(post.token_title())
    loc_info = LocationInfo(geo.lat, geo.lng)
    add_data = {
        'token_title': post.token_title(),
        'updated_score': post.updated_score(),
        'thumb_url': post.thumb_url(),
        'other_posts': user.other_posts(),
        'pie_chart': user.pie_chart(),
        'opencage_geo': geo.geocode_array,
        'loc': geo.location(),
        'geoJSON': loc_info.geoJSON(post),
        'wiki_page_id': loc_info.wiki_page_ids_all(),
        'wiki_content': loc_info.closest_wiki_content(),
        'wiki_title':   loc_info.closest_wiki_title(),
        'wiki_extract': loc_info.closest_wiki_extract()
    }
    return add_data

def get_and_insert(reader, mongodb):
    """
    Inserts all the data into one collection and the loc, geoJSON and score
    into another
    """
    post_data = get_post_data(reader)
    try:
        if mongodb.count(post_data['id']) == 0:
            add_data = get_add_data(post_data)
            mini_post = {
                "loc": add_data['loc'],
                "score": add_data['updated_score'],
                "geoJSON": add_data['geoJSON']
            }
            post_data.update(add_data)
            mongodb.insert('complete_post', post_data)
            if mini_post['geoJSON'] != None:
                mongodb.insert('post', mini_post)
    except:
        pass

def main():
    mongodb = initialise()
    for file in FILE_NAMES:
        print(file)
        try:
            with jsonlines.open(file, mode='r') as reader:
                while True:
                    try:
                        get_and_insert(reader, mongodb)
                    except EOFError:
                        print("EOF")
                        obj = {}
                        break
        except FileNotFoundError:
            print("File missing")

if __name__== "__main__":
    main()
