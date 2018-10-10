from posts import MongoDatabase

SUBREDDIT_NAME = 'earthporn'
country_rank = {}

def main():
    mongoPost = MongoDatabase(SUBREDDIT_NAME)
    mongoLoc = MongoDatabase(SUBREDDIT_NAME)
    cursor = mongoPost.find_all_and_sort('post', "score")
    for post in cursor:
        found = mongoLoc.find('location', 'loc', post['loc'])
        for loc in found:
            try:
                country = loc['location_info']['country']['name']
            except:
                country = None
        if country is not None:
            country_rank.setdefault(country, 1)
            rank = country_rank[country]
            mongoPost.update('post', '_id', post['_id'], 'country_rank', rank)
            rank += 1
            country_rank[country] = rank
        rank = None

if __name__== "__main__":
    main()
