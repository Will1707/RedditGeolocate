import pymongo
from pymongo import MongoClient
from posts import MongoDatabase

MONGO_CLIENT = 'localhost'
SUBREDDIT_NAME = 'EarthPorn'
SUBREDDIT_ID = 't5_2sbq3' # earthporn

def get_location_posts(posts):
    user_posts[posts['id']] = {
        'url':          posts['url'],
        'thumb_url':    posts['thumb_url'],
        'id':           posts['id'],
        'created':      posts['created_utc'],
        'title':        posts['title'],
        'author':       posts['author'],
        'score':        posts['score'],
        'num_comments': posts['num_comments'],
        'user_content': posts['user_content'],
        'pie_chart':    posts['pie_chart']
    }
    return user_posts

def location_info(posts, user_posts):
    insert = {
        'subreddit':    SUBREDDIT_NAME,
        'subreddit_id': SUBREDDIT_ID,
        'loc':          posts['loc'],
        'wiki_extract': posts['wiki_extract'],
        'wiki_title':   posts['wiki_title'],
        'user_posts':   user_posts
    }
    return insert

def main():
    mongodb = MongoDatabase(SUBREDDIT_NAME.lower())
    cursor  = mongodb.find_all('complete_post')
    for post in cursor:
        insert = {}
        user_posts = {}
        try:
            if mongodb.loc_count(post['loc']) == 0:
                locations = mongodb.find_loc(post['loc'])
                for posts in locations:
                    user_posts = get_location_posts(posts)
                insert = location_info(posts, user_posts)
                mongodb.insert('location', insert)
        except:
            pass
            
if __name__== "__main__":
    main()
