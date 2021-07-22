#!/usr/local/bin/python3
import os

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# auth to azure and create a client instance
subscription_key = os.environ.get("AZURE_COMPVISION_KEY")
endpoint = os.environ.get("AZURE_COMPVISION_ENDPOINT")
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# auth to cosmosdb
import pymongo
cosmos_dbname = os.environ["AZURE_COSMOS_DBNAME"]
cosmos_colname = os.environ["AZURE_COSMOS_COLNAME"]
cosmos_uri = os.environ["AZURE_COSMOS_CONNSTRING"]
cosmos_client = pymongo.MongoClient(cosmos_uri)

from flask import Flask
app = Flask(__name__)

def get_image_tags(remote_image_url):
    """
    Returns a tag (key word) for each thing in the image.
    """
    # Call API with remote image
    tags_result_remote = computervision_client.tag_image(remote_image_url)

    if (len(tags_result_remote.tags) == 0):
        return []
    else:
        return tags_result_remote.tags

def response_builder(tags):
    response = """
    <html>
    <title>Image Recognizer</title>
    """
    if len(tags) == 0:
        response += "<p>No tags detected</p>"
    else:
        response += "<p>Tags detected in image</p>"
        response += "<ul>\n"
        for tag in tags:
            t = "'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100)
            response += "<li>{}</li>\n".format(t)
        response += "</ul>"
    response += "</html>"
    return response

def save_image_tags(tags):
    db = cosmos_client.get_database(cosmos_dbname)
    col = db.get_collection(cosmos_colname)
    doc = {'tags': {}}
    for tag in tags:
        doc['tags'][tag.name] = tag.confidence * 100
    result = col.insert_one(doc)
    print("Inserted to database: {}".format(result.inserted_id))

@app.route("/test")
def tag_test():
    remote_image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg"
    tags = get_image_tags(remote_image_url)
    if tags:
        save_image_tags(tags)
    response = response_builder(tags)
    return response

if __name__ == "__main__":
    app.run()