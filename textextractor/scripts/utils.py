import requests
import time
import fpdf
import StringIO
import flask


import matplotlib.pyplot as plt
from pdf2image import convert_from_path
from matplotlib.patches import Polygon
from PIL import Image
from io import BytesIO

def _get_subscription():
    """ 
    Function to get the subscription key from the user \
    for the Microsoft Azure account
    
    Returns:
        String -- Subscription key accepted from user
    """

    subscription_key = str(input("Enter the Subscription key :"))
    return subscription_key

def _API_url():
    """
    Function to get the url for the main API

    Returns:
        String -- API url
    """

    vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/"
    text_recognition_url = vision_base_url + "recognizeText"
    return(text_recognition_url)

def make_request(image_url):
    """
    Makes the request for the image collected for performing text detection
    Uses Microsoft's Azure for getting the text
    More info : "https://azure.microsoft.com/en-in/services/cognitive-services/computer-vision/"

    Arguments:
        image_url {String} -- url of the image stored
    
    Returns:
        [Object] -- Response received
        [String] -- Operation url from response

    """
    subscription_key = _get_subscription()

    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    params  = {'mode': 'Printed'}
    data    = {'url': image_url}
    text_recognition_url = _API_url()

    response = requests.post(text_recognition_url, headers=headers,\
    params=params, json=data)
    response.raise_for_status()
    operation_url = response.headers["Operation-Location"]

    return (response, operation_url)


def get_text(analysis):
    """
    Gets the resultant text of the image supplied
    
    Arguments:
        analysis {JSON} -- JSON form of the final response 
        that contains the text detected
    
    Returns:
        [list] -- Returns the polygon data, and the text detected 
    """


    if('recognitionResult' in analysis):
        polygons = [(line["boundingBox"], line["text"])for line in analysis["recognitionResult"]["lines"]]
        text = [line['text'] for line in analysis["recognitionResult"]["lines"]]
        return (polygons, text)
    else:
        return('Sorry the image that you sent cannot be \
        recognised! Please try with another image.')


def display_image(image_url, plt, polygons):
    """
    Generates the polygon plots for the text extracted,
    and maps out the extracted text in the image itself
    
    Arguments:
        image_url {String} -- Url of the image
        plt {Object} -- Plot object
        polygons {list} -- Contains the x,y coordinates of the text extracted

    Returns:
       [Object] : Plot object
    """

    plt.figure(figsize=(15, 15))
    image = Image.open(BytesIO(requests.get(image_url).content))

    ax = plt.imshow(image)

    for polygon in polygons:
	    vertices = [(polygon[0][i], polygon[0][i+1])
		for i in range(0, len(polygon[0]), 2)]
	    text     = polygon[1]
	    patch    = Polygon(vertices, closed=True, fill=False, linewidth=2, color='y')
	    ax.axes.add_patch(patch)
	    plt.text(vertices[0][0], vertices[0][1], text, fontsize=20, va="top")

    _ = plt.axis("off")

    return(plt)

def convert_to_pdf(textList):
    """
    Converts the list of text detected,
    into a pdf file.
    
    Arguments:
        textList {list} -- text list detected
    
    Returns:
        [bytes] -- resulting PDF file
    """


    
    pdf = fpdf.FPDF(format='letter')
    pdf.add_page()
    pdf.set_font('Arial', size=12)

    for line in textList:
        pdf.write(5, str(line))
        pdf.ln()

    return (pdf.output(name = 'text_detected.pdf', dest='S'))

def convert_to_jpeg(pdfFile):
    """
    Takes in a pdf file, and returns a jpeg image
    
    Arguments:
        pdfFile {Byte} -- pdf file 
    
    Returns:
        [mimetype] -- jpeg image from the pdf file
    """

    
    pages = convert_from_path(pdfFile, 500)

    for key, page in enumerate(pages):
        img_io = StringIO()
        page.save(img_io,'JPEG')
        img_io.seek(0)
        return flask.send_file(img_io, mimetype='{}/jpeg'.format(pdfFile+key))




