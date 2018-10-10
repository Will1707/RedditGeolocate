import unittest
import os
import json
from posts import Post, UserContent, Geolocation, LocationInfo

DIR_PATH  = os.path.dirname(os.path.realpath(__file__))
FILE_PATH = os.path.join(DIR_PATH, 'tests', 'TestData')

class PostTest(unittest.TestCase):

    def setUp(self):
        self.post = Post('8405kv', '946684800', 'https://www.imgur.xyz/home/pic.jpg', 'will', 'This is a picture of Sheffield', 5555, 33)

    def test_token_title_default(self):
        """
        Test that lower case words are not tokenized
        """
        self.assertEqual(self.post.token_title(), ["Sheffield"])

    def test_token_title_lower(self):
        """
        Test that lower case words are not tokenized
        """
        self.post.title = "london sheffield exeter leeds"
        self.assertEqual(self.post.token_title(), [])

    def test_token_title_upper(self):
        """
        Test that upper case words are tokenized
        """
        self.post.title = "London Sheffield Exeter Leeds"
        self.assertEqual(self.post.token_title(), ["London", "Sheffield", "Exeter", "Leeds"])

    def test_token_title_upper_stop_words(self):
        """
        Test that stop words are not tokenized
        """
        self.post.title = "This Is A String"
        self.assertEqual(self.post.token_title(), ["String"])

    def test_token_title_oc(self):
        """
        Test that OC is not tokenized
        """
        self.post.title = "London Sheffield Exeter Leeds OC"
        self.assertEqual(self.post.token_title(), ["London", "Sheffield", "Exeter", "Leeds"])

    def test_token_title_distance(self):
        """
        Test that Distance not tokenized
        """
        self.post.title = "London Sheffield Exeter Leeds Distance"
        self.assertEqual(self.post.token_title(), ["London", "Sheffield", "Exeter", "Leeds"])

    def test_token_title_lower_punctuation(self):
        """
        Test that punctuation does not affect result
        """
        self.post.title = "£london *sheffield exeter? leeds!"
        self.assertEqual(self.post.token_title(), [])

    def test_token_title_upper_punctuation(self):
        """
        Test that punctuation does not affect result
        """
        self.post.title = "£London *Sheffield Exeter? Leeds!"
        self.assertEqual(self.post.token_title(), ["Exeter", "Leeds"])

    def test_token_title_upper_stop_words_punctuation(self):
        """
        Test that punctuation does not affect result
        """
        self.post.title = "This Is A A! String! ?! £$£$ ^^&"
        self.assertEqual(self.post.token_title(), ["String"])

    def test_token_title_numbers(self):
        """
        Test that numbers are not tokenized
        """
        self.post.title = "11 {22} [33] <44> ~55~ [6*7] 9cc 0leeds 10Exeter"
        self.assertEqual(self.post.token_title(), [])

    def test_thumb_url_no_image(self):
        """
        Test that url remains the same if imgur not in url
        """
        self.post.url = "https://www.mapforreddit.xyz/home/index.html"
        self.assertEqual(self.post.thumb_url(), self.post.url)

    def test_thumb_url_image_jpg(self):
        """
        Test that url remains the same if imgur not in url
        """
        self.post.url = "https://www.mapforreddit.xyz/home/pic.jpg"
        self.assertEqual(self.post.thumb_url(), self.post.url)

    def test_thumb_url_image_png(self):
        """
        Test that url remains the same if imgur not in url
        """
        self.post.url = "https://www.mapforreddit.xyz/home/pic.png"
        self.assertEqual(self.post.thumb_url(), self.post.url)

    def test_thumb_url_imgur_image_jpg(self):
        """
        Test that thumbnail image is selected if imgur in url
        """
        self.post.url = "https://www.imgur.xyz/home/pic.jpg"
        self.assertEqual(self.post.thumb_url(), "https://www.imgur.xyz/home/picm.jpg")

    def test_thumb_url_imgur_image_png(self):
        """
        Test that thumbnail image is selected if imgur in url
        """
        self.post.url = "https://www.imgur.xyz/home/pic.png"
        self.assertEqual(self.post.thumb_url(), "https://www.imgur.xyz/home/picm.png")

    def test_thumb_url_imgur_random_ext(self):
        """
        Test that a random extension is not converted
        """
        self.post.url = "https://www.imgur.xyz/home/pic.mp3"
        self.assertEqual(self.post.thumb_url(), self.post.url)

    def test_thumb_url_random(self):
        """
        Test that randpm characters are not converted
        """
        self.post.url = "dfg fdgdfg  fdg sdfg 3241324134 456 xdbvxcvb"
        self.assertEqual(self.post.thumb_url(), self.post.url)

    def test_updated_score_working_id(self):
        """
        Test that a working id works
        """
        self.post.id = "8405kv"
        self.assertIsInstance(self.post.updated_score(), int)

    def test_updated_score_broken_id(self):
        """
        Test that a broken id dosent break it
        """
        self.post.id = "dQw4w9WgXcQ"
        self.assertEqual(self.post.updated_score(), self.post.score)

class UserContentTest(unittest.TestCase):

    def setUp(self):
        self.usercontent = UserContent('will')

    def test_other_posts_user_deleted(self):
        """
        Test that if the author is deleted None is returned
        """
        self.usercontent.author = "[deleted]"
        self.assertEqual(self.usercontent.other_posts(), None)

    def test_other_posts_user_not_exist(self):
        """
        Test that if an author is supplied that dosent exist None is returned
        """
        self.usercontent.author = "ThisIsAUserThatDosentExist123456"
        self.assertEqual(self.usercontent.other_posts(), None)

    def test_other_posts_user_exists(self):
        """
        Test that if a know user is supplied that a dict is returned
        """
        self.usercontent.author = "spez"
        self.assertIsInstance(self.usercontent.other_posts(), dict)

    def test_pie_chart_correct_data_short(self):
        """
        Test that when supplied with known data pie_chart returns the correct dict
        """
        correct_pie_chart = {'earthporn': 1, 'adviceanimals': 1, 'pics': 1}
        with open(f'{FILE_PATH}/test_data_short_other_posts.json') as json_file:
            self.usercontent.content = json.load(json_file)
        self.assertEqual(self.usercontent.pie_chart(), correct_pie_chart)

    def test_pie_chart_correct_data_long(self):
        """
        Test that when supplied with known data, pie_chart returns the correct dict
        """
        correct_pie_chart = {'earthporn': 77, 'art': 2, 'itookapicture': 15,
                            'pics': 1, 'cityporn': 5}
        with open(f'{FILE_PATH}/test_data_long_other_posts.json') as json_file:
            self.usercontent.content = json.load(json_file)
        self.assertEqual(self.usercontent.pie_chart(), correct_pie_chart)

    def test_pie_chart_dict_string_string(self):
        """
        Test that when supplied with known bad data, pie_chart returns the correct dict
        """
        self.usercontent.content = {
                                    "this": "is",
                                    "a": "fake",
                                    "dict": "string"
                                    }
        self.assertEqual(self.usercontent.pie_chart(), {'this': 2, 'a': 4, 'dict': 6})

    def test_pie_chart_dict_string_int(self):
        """
        Test that when supplied with a dict with ints as values pie_chart returns None
        """
        self.usercontent.content = {
                                    "this": 12,
                                    "a": 34,
                                    "dict": 45
                                    }
        self.assertEqual(self.usercontent.pie_chart(), None)

    def test_pie_chart_dict_int_string(self):
        """
        Test that when supplied with ints as keys, pie_chart returns the correct dict
        """
        self.usercontent.content = {
                                    12: "is",
                                    34: "fake",
                                    56: "string"
                                    }
        self.assertEqual(self.usercontent.pie_chart(), {12: 2, 34: 4, 56: 6})

    def test_pie_chart_bad_dict_int_int(self):
        """
        Test that when supplied with a dict with ints as values and keys pie_chart returns None
        """
        self.usercontent.content = {
                                    12: 34,
                                    56: 78,
                                    90: 123
                                    }
        self.assertEqual(self.usercontent.pie_chart(), None)

    def test_pie_chart_dict_list(self):
        """
        Test that when supplied with known data, pie_chart returns the correct dict
        """
        self.usercontent.content = {
                                    "fake": ["This", "is", "A", "List"],
                                    "key": ["A", "list", "of", "numbers", 1, 1212, 123324],
                                    1234: ["123", "ABC", 123]
                                    }
        self.assertEqual(self.usercontent.pie_chart(), {'fake': 4, 'key': 7, 1234: 3})

    def test_pie_chart_string(self):
        """
        Test that if supplied with a string pie_chart returns None
        """
        self.usercontent.content = "This is a string"
        self.assertEqual(self.usercontent.pie_chart(), None)

    def test_pie_chart_none(self):
        """
        Test that if supplied with a None pie_chart returns None
        """
        self.usercontent.content = None
        self.assertEqual(self.usercontent.pie_chart(), None)

    def test_pie_chart_list(self):
        """
        Test that if supplied with a list pie_chart returns None
        """
        self.usercontent.content = ['This', 'Is', 'A', 'List']
        self.assertEqual(self.usercontent.pie_chart(), None)

    def test_pie_chart_int(self):
        """
        Test that if supplied with an int pie_chart returns None
        """
        self.usercontent.content = 123456789
        self.assertEqual(self.usercontent.pie_chart(), None)

class GeolocationTest(unittest.TestCase):

    def setUp(self):
        self.geolocation = Geolocation(['London', 'Eye'])

    def test_geolocation_set_api_count_int(self):
        """
        Test that returns the correct result when supplied with a known location
        """
        self.geolocation.set_api_count(500)
        self.assertEqual(Geolocation.api_count, 500)

    def test_geolocation_set_api_count_string(self):
        """
        Test that returns the correct result when supplied with a known location
        """
        with self.assertRaises(ValueError) as context:
            self.geolocation.set_api_count('This is a string')
        self.assertTrue(f'Please supply an int below the api limit {Geolocation.api_limit}', str(context.exception))

    def test_geolocation_set_api_count_list(self):
        """
        Test that returns the correct result when supplied with a known location
        """
        with self.assertRaises(ValueError) as context:
            self.geolocation.set_api_count(['This', 'is', 'a', 'string'])
        self.assertTrue(f'Please supply an int below the api limit {Geolocation.api_limit}', str(context.exception))

    def test_geolocation_set_api_count_dict(self):
        """
        Test that returns the correct result when supplied with a known location
        """
        with self.assertRaises(ValueError) as context:
            self.geolocation.set_api_count({})
        self.assertTrue(f'Please supply an int below the api limit {Geolocation.api_limit}', str(context.exception))

    def test_geolocation_set_api_count_high(self):
        """
        Test that returns the correct result when supplied with a known location
        """
        with self.assertRaises(ValueError) as context:
            self.geolocation.set_api_count(100000000000000)
        self.assertTrue(f'Please supply an int below the api limit {Geolocation.api_limit}', str(context.exception))

    def test_geolocation_api_count_inc(self):
        """
        Test that returns the correct result when supplied with a known location
        """
        api_count = self.geolocation.api_count + 1
        self.assertEqual(self.geolocation.api_count_inc(), api_count)

    def test_geolocation_result_real_location(self):
        """
        Test that returns the correct result when supplied with a known location
        """
        self.assertIsInstance(self.geolocation.result(), list)

    def test_geolocation_result_fake_location(self):
        """
        Test that a wrong location returns None
        """
        self.geolocation.title = ['This', 'Place', 'Dosen', 'Exist']
        self.assertEqual(self.geolocation.result(), None)

    def test_geolocation_result_string_location(self):
        """
        Test that a string still gets the correct result
        """
        self.geolocation.title = "London Eye"
        self.assertIsInstance(self.geolocation.result(), list)

    def test_geolocation_result_negative_api_limit(self):
        """
        Test that a negative api count raises error
        """
        self.geolocation.set_api_count(-10)
        with self.assertRaises(ValueError) as context:
            self.geolocation.result()
        self.assertTrue('Negative api count', str(context.exception))
        self.geolocation.set_api_count(0)

    def test_geolocation_result_negative_api_limit_high(self):
        """
        Test that a large negative number raises error
        """
        self.geolocation.set_api_count(-100000)
        with self.assertRaises(ValueError) as context:
            self.geolocation.result()
        self.assertTrue('Negative api count', str(context.exception))
        self.geolocation.set_api_count(0)

    def test_geolocation_result_api_limit_high(self):
        """
        Test that api limit limits the result
        """
        Geolocation.api_count = 1000000
        with self.assertRaises(ValueError) as context:
            self.geolocation.result()
        self.assertTrue('Api limit reached', str(context.exception))
        self.geolocation.set_api_count(0)

    def test_geolocation_location_real_location(self):
        """
        Test that location returns the correct coordinates when supplied with known data
        """
        with open(f'{FILE_PATH}/test_data_london_eye_geocoded.json') as json_file:
            self.geolocation.geocode_array = json.load(json_file)
        self.assertEqual(self.geolocation.location(), [51.5032803, -0.1196873])

    def test_geolocation_location_none(self):
        """
        Test that when supplied with none location (find coordinates) returns none
        """
        self.geolocation.geocode_array = None
        self.assertEqual(self.geolocation.location(), None)

class LocationInfoTest(unittest.TestCase):

    def setUp(self):
        self.locationinfo = LocationInfo(51.5032803, -0.1196873)
        self.post = Post('8405kv', '946684800', 'https://www.imgur.xyz/home/pic.jpg', 'will', 'This is a picture of Sheffield', 5555, 33)

    def test_geoJSON_real_post(self):
        """
        Test that
        """
        geoJSON = {'type': 'Feature', 'id': '8405kv', 'geometry':
            {'type': 'Point', 'coordinates': [-0.1196873, 51.5032803]}, 'properties':
            {'title': 'This is a picture of Sheffield', 'image_link': 'https://www.imgur.xyz/home/picm.jpg',
            'author': 'will', 'date': '946684800', 'score': 5555, 'comments': 33}}
        self.assertEqual(self.locationinfo.geoJSON(self.post), geoJSON)

    def test_geoJSON_string_post(self):
        """
        Test that
        """
        self.assertEqual(self.locationinfo.geoJSON("Not a real post"), None)

    def test_geoJSON_int_post(self):
        """
        Test that
        """
        self.assertEqual(self.locationinfo.geoJSON(1234), None)

    def test_geoJSON_string_coords(self):
        """
        Test that
        """
        self.locationinfo.lat = "string"
        self.locationinfo.lng = "string"
        with self.assertRaises(ValueError) as context:
            self.locationinfo.geoJSON(self.post)
        self.assertTrue('lat/lng is not an int', str(context.exception))

    def test_wiki_page_ids_dict(self):
        """
        Test that
        """
        self.assertIsInstance(self.locationinfo.wiki_page_ids_all(), dict)

    def test_wiki_page_ids_result(self):
        """
        Test that
        """
        with open(f'{FILE_PATH}/test_data_london_eye_wikipedia_page_ids.json') as json_file:
            result = json.load(json_file)
        self.assertEqual(self.locationinfo.wiki_page_ids_all(), result)

    def test_wiki_page_ids_string_coords(self):
        """
        Test that
        """
        self.locationinfo.lat = "string"
        self.locationinfo.lng = "string"
        with self.assertRaises(ValueError) as context:
            self.locationinfo.wiki_page_ids_all()
        self.assertTrue('lat/lng is not an int', str(context.exception))

    def test_wiki_content_is_dict_london_eye(self):
        """
        Test that
        """
        self.locationinfo.wiki_page_ids_all()
        self.locationinfo.closest_wiki_page_id()
        self.assertIsInstance(self.locationinfo.closest_wiki_content(), dict)

    def test_wiki_content_no_result(self):
        """
        Test that
        """
        self.locationinfo.wiki_page_ids_all_attempted = True
        self.locationinfo.page_id = None
        self.assertEqual(self.locationinfo.closest_wiki_content(), None)

if __name__ == '__main__':
    unittest.main()
