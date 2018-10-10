import pymongo
import requests
import praw
import json
from nltk.corpus import stopwords
from nltk.tokenize  import word_tokenize
from opencage.geocoder import OpenCageGeocode

STOP_WORDS = set(stopwords.words('english'))
REDDIT_PASSWORD = 'REDDIT_PASSWORD'
REDDIT_USERNAME = 'REDDIT_USERNAME'
REDDIT_CLIENT_ID = 'REDDIT_CLIENT_ID'
REDDIT_CLIENT_SECRET = 'REDDIT_CLIENT_SECRET'
REDDIT_USER_AGENT = 'REDDIT_USER_AGENT'
REDDIT = praw.Reddit(client_id=REDDIT_CLIENT_ID,    client_secret=REDDIT_CLIENT_SECRET,
                     password=REDDIT_PASSWORD,      user_agent=REDDIT_USER_AGENT,
                     username=REDDIT_USERNAME)
GEOCODE_KEY = 'GEOCODE_KEY'

class MongoDatabase(object):
    """
    MongoDatabase has the following attributes:
        client: The mongodb client
        db: The mongodb database name
    """

    def __init__(self, db_name):
        """
        Return a
        """
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db     = self.client[db_name]

    def collection(self, collection_name, index):
        """
        Return a
        """
        self.db.create_collection(collection_name).create_index([(index, pymongo.DESCENDING)], unique=True)

    def insert(self, collection_name, data):
        """
        Return a
        """
        self.db.get_collection(collection_name).insert_one(data)

    def get_collections(self):
        """
        Return a
        """
        return self.db.collection_names()

    def index(self, collection_name, index, direction, uniqueness):
        """
        Return a
        """
        if direction == 'descending':
            self.db.get_collection(collection_name).create_index([(index, pymongo.DESCENDING)], unique=uniqueness)
        elif direction == 'ascending':
            self.db.get_collection(collection_name).create_index([(index, pymongo.ASCENDING)], unique=uniqueness)
        else:
            raise ValueError('Please specify direction: ascending or descending')

    def count(self, id):
        """
        Return a
        """
        return self.db.complete_post.find({"id": id}).count() + self.db.post.find({"geoJSON.id": id}).count()

    def find_all(self, collection_name):
        """
        Return a
        """
        return self.db.get_collection(collection_name).find(no_cursor_timeout=True)

    def find(self, collection_name, field, value):
        """
        Return a
        """
        return self.db.get_collection(collection_name).find({field:value},no_cursor_timeout=True)

    def find_one(self, collection_name, field, value):
        """
        Return a
        """
        return self.db.get_collection(collection_name).find_one({field:value},no_cursor_timeout=True)

    def find_and_sort(self, collection_name, query, sort):
        """
        Return a
        """
        return self.db.get_collection(collection_name).find(query,no_cursor_timeout=True).sort(sort, pymongo.DESCENDING)

    def find_all_and_sort(self, collection_name, sort):
        """
        Return a
        """
        return self.db.get_collection(collection_name).find(no_cursor_timeout=True).sort(sort, pymongo.DESCENDING)


    def update(self, collection_name, find_field, find_value, update_field, value):
        """
        Return a
        """
        return self.db.get_collection(collection_name).update_one({find_field: find_value},{"$set":{update_field: value}})

    def update_many(self, collection_name, find_field, find_value, update_field, value):
        """
        Return a
        """
        return self.db.get_collection(collection_name).update_many({find_field: find_value},{"$set":{update_field: value}})

    def update_three(self, collection_name, find_field, find_value, update1_field, update1_value, update2_field, update2_value, update3_field, update3_value):
        """
        Return a
        """
        return self.db.get_collection(collection_name).update({find_field: find_value},{"$inc":{update1_field: update1_value,update2_field: update2_value,update3_field: update3_value}})

    def loc_count(self, loc):
        """
        Return a
        """
        return self.db.get_collection('location').find({"loc": loc}).count(with_limit_and_skip=True)

    def find_loc(self, loc):
        """
        Return a
        """
        return self.db.get_collection('complete_post').find({"loc": loc}, no_cursor_timeout=True).sort("score", pymongo.DESCENDING)

class Post(object):
    """
    Each Reddit post has the following attributes:
        id: A string representing the id
        created: An int representing the date
        url: A sting representing the url
        author: A string representing the author
        title: A string representing the title
        score: An int representing the score
        comments: An int representing the number of comments
    """

    def __init__(self, id, created, url, author, title, score, comments):
        """
        Return a Post object whose id is *id*, author is *author*, url is *url*
        and title is *title*
        """
        self.id = id
        self.created = created
        self.url = url
        self.author = author
        self.title = title
        self.score = score
        self.comments = comments

    def token_title(self):
        """
        Returns a tokenized title of the upper case words, minus any stopwords,
        as a list
        """
        token_title = []
        tmp = word_tokenize(self.title)
        for word in tmp:
            if word[0].isupper() and word != 'OC' and word.lower() != 'distance' and word.lower() != 'itap' and word.lower() not in STOP_WORDS:
                token_title.append(word)
        return token_title

    def thumb_url(self):
        """
        Returns a url modified to give a thumbnail sized image if the domain
        is imgur as a string
        """
        thumb_url = self.url
        if 'imgur' in self.url:
            if self.url[-4:].lower() == '.jpg':
                split = self.url.split('.jpg')
                thumb_url = f'{split[0]}m.jpg'
            elif self.url[-4:].lower() == '.png':
                split = self.url.split('.png')
                thumb_url = f'{split[0]}m.png'
        return thumb_url

    def updated_score(self):
        """
        Returns the updated score as an int
        """
        try:
            return REDDIT.submission(self.id).score
        except Exception as e:
            if e.response.status_code == 404:
                return self.score

class UserContent(object):
    """
    User content has the following attributes:
        author: A string represting the author
    """

    def __init__(self, author):
        """
        Return a UserContent object whose author is *author*
        """
        self.author = author
        self.content = None

    def other_posts(self):
        """
        Returns a dict of the users other posts
        """
        ## FIX dosent add all the images eg. user - RyanSmith
        content = {}
        if self.author != '[deleted]':
            try:
                for submission in REDDIT.redditor(self.author).submissions.top('all'):
                    post = Post(submission.id, submission.created_utc, submission.url, self.author, None, submission.score, submission.num_comments)
                    if "imgur" in post.url or post.url[-4:].lower() == '.jpg' or post.url[-4:].lower() == '.png':
                        sub = str(submission.subreddit).split("=")[0]
                        if "." in sub:
                            sub = sub.replace(".", "")
                        if not submission.over_18:
                            content.setdefault(sub.lower(), []).append({
                                    'subreddit': sub,
                                    'created': post.created,
                                    'url': post.url,
                                    'thumb_url': post.thumb_url(),
                                    'score': post.score,
                                    'comments': post.comments,
                                    'id': post.id
                            })
                self.content = content
                if len(self.content) == 0:
                    return None
                return self.content
            except Exception as e:
                if e.response.status_code == 404:
                    return None
        else:
            return None

    def pie_chart(self):
        """
        Returns a dict of the subreddit and number of submissions to it
        """
        pie_chart = {}
        if isinstance(self.content, dict):
            for key in self.content.keys():
                if not isinstance(self.content[key], int):
                    pie_chart[key] = len(self.content[key])
        if len(pie_chart) == 0:
            return None
        else:
            return pie_chart

class Geolocation(object):

    api_limit = 10000
    api_count = 0

    def __init__(self, title):
        """
        Return a Geolocation object whose title is *title*
        """
        self.title = title
        self.geocode_attempted = False
        self.lng = None
        self.lat = None
        self.geocode_array = None
        self.result()

    def set_api_count(self, api_count):
        """
        Sets the api count, defaults to zero
        """
        if isinstance(api_count, int) and api_count < Geolocation.api_limit:
            Geolocation.api_count = api_count
        else:
            raise ValueError(f'Please supply an int below the api limit {Geolocation.api_limit}')

    def api_count_inc(self):
        Geolocation.api_count += 1
        print(Geolocation.api_count)
        return Geolocation.api_count

    def result(self):
        """
        Returns a list of geocoded data
        """
        result = []
        if isinstance(self.title, list):
            place = ' '.join(self.title)
        else:
            place = self.title
        if place is not None:
            if Geolocation.api_count < 0:
                raise ValueError('Negative api count')
            elif Geolocation.api_count <= Geolocation.api_limit:
                result = OpenCageGeocode(GEOCODE_KEY).geocode(place)
                self.api_count_inc()
                self.geocode_attempted = True
                if len(result) == 0:
                    self.geocode_array = None
                    return self.geocode_array
                else:
                    self.geocode_array = result
                    self.location()
                    return self.geocode_array
            elif Geolocation.api_count >= Geolocation.api_limit:
                raise ValueError('Api limit reached')
        self.geocode_array = None
        return self.geocode_array

    def location(self):
        """
        Returns a list of the latitude and longitude
        """
        if self.geocode_attempted == False:
            self.result()
        try:
            self.lng = self.geocode_array[0]['geometry']['lng']
            self.lat  = self.geocode_array[0]['geometry']['lat']
            return [self.lat, self.lng]
        except (IndexError, TypeError):
            return None

class LocationInfo(object):
    """
    Location Info has the following attributes:
        lat: An int represting latitude
        lng: An int represtenting longitude
    """

    def __init__(self, lat, lng):
        """
        Return a LocationInfo object whose lat is *lat*
        """
        self.lat = lat
        self.lng = lng
        self.all_page_id = None
        self.page_id = None
        self.content = None
        self.wiki_page_ids_all_attempted = False

    def geoJSON(self, post):
        """
        Returns a geoJSON object
        """
        geoJSON = None
        if isinstance(self.lat, float) or isinstance(self.lat, int) and isinstance(self.lng, float) or isinstance(self.lng, int):
            lat = self.lat
            lng = self.lng
            if isinstance(post, Post):
                geoJSON = {
                    "type": "Feature",
                    "id": post.id,
                    "geometry": {
                    "type": "Point",
                    "coordinates": [self.lng, self.lat]
                  },
                  "properties": {
                    "title": post.title,
                    "image_link": post.thumb_url(),
                    "author": post.author,
                    "date": post.created,
                    "score": post.score,
                    "comments": post.comments
                    }
                  }
            return geoJSON
        elif self.lat is None or self.lng is None:
            return None
        else:
            raise ValueError('lat/lng is not a number')

    def wiki_page_ids_all(self):
        """
            Returns a dict of wikipedia page ids within 10000m of the location
        """
        if isinstance(self.lat, float) or isinstance(self.lat, int) and isinstance(self.lng, float) or isinstance(self.lng, int):
            response = requests.get(f'http://en.wikipedia.org/w/api.php?action=query&format=json&list=geosearch&gscoord={self.lat}|{self.lng}&gsradius=10000')
            self.wiki_page_ids_all_attempted = True
            if response.status_code == 200:
                if len(response.json()['query']['geosearch']) != 0:
                    self.all_page_id = response.json()
                    return self.all_page_id
            self.all_page_id = None
            return self.all_page_id
        elif self.lat is None or self.lng is None:
            self.all_page_id = None
            return self.all_page_id
        else:
            raise ValueError('lat/lng is not a number')

    def closest_wiki_page_id(self):
        """
            Returns a dict of wikipedia page ids within 10000m of the location
        """
        if self.wiki_page_ids_all_attempted is False:
            self.wiki_page_ids_all()
        if self.all_page_id is not None:
            self.page_id = self.all_page_id['query']['geosearch'][0]['pageid']
            return self.page_id
        else:
            self.page_id = None
            return self.page_id

    def closest_wiki_content(self):
        """
        Returns a dict of the closest wikipedia article to the location
        """

        self.closest_wiki_page_id()
        if self.page_id is not None:
            response = requests.get(f'http://en.wikipedia.org/w/api.php?action=query&format=json&prop=iwlinks%7Ccoordinates%7Cextracts%7Ccategories%7Cdescription%7Cextlinks&export=1' \
                                    f'&iwurl=1&continue=&pageids={self.page_id}&exsentences=5&exlimit=max&exintro=1&explaintext=1&exsectionformat=plain&excontinue=&ellimit=max')
            binary = response.content
            result = json.loads(binary.decode('utf8'))
            if response.status_code == 200 and len(result['query']['pages'][str(self.page_id)]) != 2:
                self.content = result
                return self.content
        self.content = None
        return self.content

    def closest_wiki_title(self):
        """
            Returns a dict of wikipedia page ids within 10000m of the location
        """
        if self.wiki_page_ids_all_attempted is True and self.content is not None:
            return self.content['query']['pages'][str(self.page_id)]['title']
        elif self.wiki_page_ids_all_attempted is False:
            self.closest_wiki_content()
            if self.content is not None:
                return self.content['query']['pages'][str(self.page_id)]['title']
        return None

    def closest_wiki_extract(self):
        """
            Returns a dict of wikipedia page ids within 10000m of the location
        """
        if self.wiki_page_ids_all_attempted is True and self.content is not None:
            return self.content['query']['pages'][str(self.page_id)]['extract']
        elif self.wiki_page_ids_all_attempted is False:
            self.closest_wiki_content()
            if self.content is not None:
                return self.content['query']['pages'][str(self.page_id)]['extract']
        return None
