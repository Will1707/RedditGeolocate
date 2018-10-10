from pymongo import MongoClient
import pymongo

"""
This takes a very long time to run - in the order of a few days
"""
SUBREDDIT_NAME = 'earthporn'
distance = [1000, 2000, 3000, 4000, 5000, 7500, 10000, 20000, 30000, 50000]
level = [f'level_{x}' for x in range(1,11)]
locs = []

def main():
    mongodb = MongoDatabase(SUBREDDIT_NAME)
    cursor = mongodb.find_all_and_sort('post', 'geoJSON.properties.score')
    for post in cursor:
        for i in range(len(level)):
            if post['loc'] != [0, 0]:
                clus = "cluster." + level[i]
                query = {
                    "geoJSON.geometry.coordinates" : {
                        "$nearSphere": {
                            "$geometry": {
                                    "type": "Point",
                                    "coordinates" : post['geoJSON']['geometry']['coordinates']
                             },
                             "$maxDistance" : distance[i]
                        }
                    },
                    clus: True
                }
                found = mongodb.find_and_sort('post', query, 'geoJSON.properties.score')
                first_result = 0
                print(f"id: {post['geoJSON']['id']} location: {post['loc']} level: {level[i]}")
                for loc in found:
                    loc_bool = loc['cluster'][level[i]]
                    if loc['loc'] not in locs:
                        cluster = loc['cluster']
                        cluster[level[i]] = False
                        mongodb.update_many('post', 'loc', loc['loc'], 'cluster', cluster)
                        locs.append(loc['loc'])
                    if first_result == 0:
                        top_cluster = loc['cluster']
                        top_cluster[level[i]] = loc_bool
                        mongodb.update('post', 'geoJSON.id', loc['geoJSON']['id'], 'cluster', top_cluster)
                        first_result += 1
                locs = []
                print("Finished location search")
        mongodb.update('post', 'geoJSON.id', post['geoJSON']['id'], 'cluster_completed', True)
        print(f"completed {post['geoJSON']['id']} cluster")

if __name__== "__main__":
    main()
