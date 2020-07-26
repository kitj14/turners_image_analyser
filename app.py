from flask import Flask, render_template, request, redirect, url_for # to write flask code
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__) # file that creates flask app

def stockChecker(results): # function to check if uploaded image has similar car in Turners then displays similar image of that car 
    present = False
    carList = {
                'convertible' : 'https://content.tgstatic.co.nz/photos/good/nissan-fairlady-20303135_12249249.jpg',
                'convertible car' : 'https://content.tgstatic.co.nz/photos/good/nissan-fairlady-20303135_12249249.jpg',
                'wagon' : 'https://content.tgstatic.co.nz/photos/good/subaru-legacy-19956783_11531418.jpg',
                'wagon car' : 'https://content.tgstatic.co.nz/photos/good/subaru-legacy-19956783_11531418.jpg',
                'utility' : 'https://content.tgstatic.co.nz/photos/good/ford-ranger-19800515_11071290.jpg',
                'utility car' : 'https://content.tgstatic.co.nz/photos/good/ford-ranger-19800515_11071290.jpg',
                'coupe' : 'https://content.tgstatic.co.nz/photos/good/bmw-320i-20332003_12214867.jpg',
                'coupe car' : 'https://content.tgstatic.co.nz/photos/good/bmw-320i-20332003_12214867.jpg',
                'hatchback' : 'https://content.tgstatic.co.nz/photos/good/mazda-demio-20015927_11740524.jpg',
                'hatchback car' : 'https://content.tgstatic.co.nz/photos/good/mazda-demio-20015927_11740524.jpg',
                'van' : 'https://content.tgstatic.co.nz/photos/good/nissan-vanette-20250762_11885645.jpg', 
                'truck' : 'https://www.teletracnavman.co.nz/media/17344/safety-truck-002.jpg', 
                'sedan' : 'https://content.tgstatic.co.nz/photos/good/toyota-camry-19854663_11321470.jpg', 
                'sports utility' : 'https://content.tgstatic.co.nz/photos/good/jeep-grand-cherokee-20017016_11744839.jpg', 
                'sport utility' : 'https://content.tgstatic.co.nz/photos/good/jeep-grand-cherokee-20017016_11744839.jpg'
            }

    for result in results:        
        if result['class'] in carList:
            category = result['class']
            present = True
            car = carList[category]
            if present:
                break
        else:
            category = "No identical car"
            car = 'https://www.odt.co.nz/sites/default/files/story/2020/01/turners_210120.jpg'
    return category, car

def allowed_image(filename): # function to check if the uploaded image extension is allowed
    app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

def fetch_result(path): # function to fetch data from IBM watson visual recognition
    from watson_developer_cloud import VisualRecognitionV3

    visual_recognition = VisualRecognitionV3(
        '2018-03-19',
        iam_apikey='e_84LnMSEb2jcIdhBcOb2EYqQfXfeXBXR39q91HBn8X5')

    with open(path, 'rb') as images_file:
        classes = visual_recognition.classify(
            images_file,
            threshold='0.6',
            classifier_ids='default').get_result()
        results = classes['images'][0]['classifiers'][0]['classes']
        return results


@app.route('/', methods= ['GET','POST']) # route for base url

def home(): 
    from ibm_watson import VisualRecognitionV3
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator 

    apikey = 'e_84LnMSEb2jcIdhBcOb2EYqQfXfeXBXR39q91HBn8X5'
    URL= 'https://api.us-south.visual-recognition.watson.cloud.ibm.com' 
    version = '2019-02-11'
    authenticator = IAMAuthenticator(apikey)

    visual_recognition = VisualRecognitionV3(
        version=version,
        authenticator=authenticator
    )

    visual_recognition.set_service_url(URL) 

    if request.method == 'POST':
        url = request.form['site']
    else:
        url = 'https://www.driven.co.nz/media/100004742/3er.jpg?width=820'

    classes = visual_recognition.classify(url=url).get_result()
    results = classes['images'][0]['classifiers'][0]['classes']
    
    category, car = stockChecker(results)
    return render_template('home.html', results = results, url = url, type = category, car = car)    


@app.route('/upload', methods= ['GET','POST']) # route for upload page

def upload():
    if request.method == 'POST':
        
        image = request.files['file']

        if allowed_image(image.filename):
            img = secure_filename(image.filename)      
            npath = os.path.join(r'C:\Users\Danilo Palen\Documents\Mission2-Visual-Recognition\static\uploads', img)   
            image.save(os.path.join(r'C:\Users\Danilo Palen\Documents\Mission2-Visual-Recognition\static\uploads', img))         
            
            results = fetch_result(npath)
            category, car = stockChecker(results)        
            return render_template('upload.html', results = results, img = img, type = category, car = car)
        else:
            return redirect(request.url)
    else:
        return redirect(url_for('home'))
