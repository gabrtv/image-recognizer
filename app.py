#!/usr/local/bin/python3
import os

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# auth to azure and create a client instance
subscription_key = os.environ.get("AZURE_COMPVISION_KEY")
endpoint = os.environ.get("AZURE_COMPVISION_ENDPOINT")
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

from flask import Flask
app = Flask(__name__)

def get_image_tags(remote_image_url):
    """
    Returns a tag (key word) for each thing in the image.
    """
    # Call API with remote image
    tags_result_remote = computervision_client.tag_image(remote_image_url)

    if (len(tags_result_remote.tags) == 0):
        return "No tags detected."
    else:
        tags_detected = []
        
        for tag in tags_result_remote.tags:
            t = "'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100)
            tags_detected.append(t)

        return tags_detected

def response_builder(result):
    response = """
    <html>
    <title>Image Recognizer</title>
    """
    response += "<ul>\n"
    response += "<p>Tags detected in image</p>"
    for item in result:
        response += "<li>{}</li>\n".format(item)
    response += "</ul>"
    response += "</html>"
    return response

@app.route("/test")
def tag_test():
    remote_image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg"
    tags = get_image_tags(remote_image_url)
    response = response_builder(tags)
    return response

if __name__ == "__main__":
    app.run()