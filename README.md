# RedditGeolocate


pushshift_download.py will download all the reddit submissions available from https://pushshift.io into a data folder in your directory and then will unzip them. They take up around 900GB as of the 2018-05 download so ensure there is enough space. If downloading a large amount please consider donating to pushshift https://pushshift.io/donations/.

geolocate.py expects mongodb to be running on localhost 27017. It iterates through the downloaded submissions to find submissions to the EarthPorn subreddit, https://www.reddit.com/r/earthporn. The desired subreddit can be changed by changing SUBREDDIT_NAME and the SUBREDDIT_ID. Once it has found a submission to EarthPorn it attempts to geolocate it using the https://opencagedata.com api. The X-Small subscription allows 10,000 calls a day to the api. This limit is set in the Geolocate class. If sucessful it will use the coordinates from the opencagedata to search for the nearest Wikipedia article, using the Wiki api. From the Wikipedia article it will extract the title and the content of the article. Using the coordinates a geoJSON file is produced, to allow the submission to be displayed on a map. Using the Reddit api, through praw, a search is made for the users other image based posts. This data is then processed so the results can be displayed in a pie chart.

location_database.py should be run after a whole subreddit has been geolocated. It will group the posts by location, ranked by score, so that they are easily displayed on a map.

country_rank.py when run will rank the posts by country, ie. the highest score in each country will be 1st, 2nd highest score 2nd etc. This can be used to display a minimum number of posts per country.

cluster.py will set the display level of every post. Starting at the post with the highest score it runs a $nearSphere search on MongoDB which finds all the other posts within x meters of it. The display level of the post with highest score in the area is set to True and the rest are set False. This is repeated for 10 distances. The end result is, that depending on the display level only the highest scoring post in the area is displayed. ie. a circle of 5000m centered on a post with a score of 1000 and containing only posts with a lower score will only display the post with a score of 1000 at level 5.

RedditGeolocate was written to get the data to display on www.mapforreddit.xyz 

I previously used a geocoder with better natural language processing so it was able to extract the location from the description with greater accuracy. Some work needs to be done to improve the accuracy of the geolocation results. For example searching for previosuly geoloated posts with the same title or using better NLP before sending the result to be geocoded.
