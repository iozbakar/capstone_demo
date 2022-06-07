from flask import Flask, render_template, Response, send_file, request,send_from_directory,stream_with_context
from werkzeug.utils import secure_filename
import AppleClassifier
from AppleClassifier import AppleClassifierNet
from PIL import Image, ImageFile,ImageOps
import cv2
import numpy
import os, shutil
import time
import json
from datetime import datetime
import plotly
import plotly.express as px
import pandas as pd


ImageFile.LOAD_TRUNCATED_IMAGES = True
vc = cv2.VideoCapture(0) 
app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
save = os.path.join(APP_ROOT, 'save/')
REPORTS_FOLDER = os.path.join(APP_ROOT, 'reports/')

@app.route('/report_images/<id>/photos/<path:filename>/<path:i><format>')
def download_file(filename,id,i,format):
    path = os.path.join(REPORTS_FOLDER, f"{id}/")
    #filename = os.path.join(filename, f"{i}{format}")
    filename = f"photos/{filename}/{i}{format}"
    return send_from_directory(path, filename, as_attachment=True)

@app.route("/")
def index_page():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard_page():
    reports = os.listdir("reports")
    reports_data = []
   
    for i in reports:
        with open(f"reports/{i}/data.json","r") as f:
            data = json.load(f)
         
        my_data = {
            "id":str(data["id"]),
            "Number of Good Quality Apple":data["AppleQuality"]["Good Apple Number"],
            "Number of Middle Quality Apple":data["AppleQuality"]["Mid Apple Number"],
            "Number of Bad Quality Apple":data["AppleQuality"]["Bad Apple Number"],
            "Total Number of Apples":data["AppleQuality"]["Good Apple Number"]+data["AppleQuality"]["Mid Apple Number"]+data["AppleQuality"]["Bad Apple Number"]
        }
         
         
            
        reports_data.append(my_data)   
    
    if reports_data:  
        data_df = pd.DataFrame(reports_data)
        pie_sf = data_df.drop(["id","Total Number of Apples"],axis=1).sum(axis=0)
        pie_df = pd.DataFrame({'quality':pie_sf.index, 'number':pie_sf.values})
        
        pie_fig = px.pie(pie_df,values="number", names="quality",title="Apple Quality Ratio")
        bar_fig = px.bar(data_df,x="id",y=["Number of Good Quality Apple","Number of Middle Quality Apple","Number of Bad Quality Apple"],title="Bar Chart")
        
        pie_graph_json =  json.dumps(pie_fig, cls=plotly.utils.PlotlyJSONEncoder)
        bar_fig_json = json.dumps(bar_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
    else:
        pie_graph_json = None
        bar_fig_json = None

    return render_template("dashboard.html", pie_json=pie_graph_json,bar_json=bar_fig_json)

@app.route("/reports")
def reports_page():
    reports = os.listdir("reports")
    reports_data = []
   
    for i in reports:
        with open(f"reports/{i}/data.json","r") as f:
            data = json.load(f)
            
        reports_data.append(data)   
   
    return render_template("reports.html", data_rp=reports_data)

def gen(): 
   """Video streaming generator function.""" 
   while True: 
       rval, frame = vc.read()
       if not rval:
           break
       else: 
            cv2.imwrite('static/temp_img/pic.jpg', frame) 
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + open('static/temp_img/pic.jpg', 'rb').read() + b'\r\n') 

@app.route('/video_feed') 
def video_feed(): 
   """Video streaming route. Put this in the src attribute of an img tag.""" 
   return Response(gen(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame') 
@app.route('/capture_img')
def capture_img():
    return send_file("static/temp_img/pic.jpg","image/jpg")
 
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
        print(request.files) 
        f = request.files['file']
        f.save("save/" + secure_filename(f.filename))
        return 'file uploaded successfully'
 
@app.route("/remove", methods=["GET","POST"])
def remove_file():
    if request.method == 'POST':
        file_no = request.form['file_no']
        file_name = file_no + ".jpg"
        try:
            os.remove("save/"+file_name)
        except FileNotFoundError:
            pass
        return "file deleted successfuly" 
 
@app.route("/submit", methods=["POST"])
def submit_form():
    if request.method == "POST":
        g_apple_count , mid_apple_count, bad_apple_count, classifier = predict_apples()
        
        submission_successful = True #or False. you can determine this.
        
        save_report(classifier,g_apple_count,mid_apple_count,bad_apple_count)
        return render_template("index.html", submission_successful=submission_successful)
data =None

def save_report(classifier:AppleClassifier.AppleClassifier,g_apple_count,mid_apple_count,bad_apple_count):
    report_name = int(time.time())
    os.mkdir(f"reports/{report_name}")
    os.mkdir(f"reports/{report_name}/photos")
    os.mkdir(f"reports/{report_name}/photos/yolo")
    os.mkdir(f"reports/{report_name}/photos/good")
    os.mkdir(f"reports/{report_name}/photos/mid")
    os.mkdir(f"reports/{report_name}/photos/bad")
    os.mkdir(f"reports/{report_name}/photos/raw")
    saved_photos = os.listdir("save")
    for i in saved_photos:
        os.replace("save/" + i,f"reports/{report_name}/photos/raw/{i}")    
    
    for idx, apple in enumerate(classifier.good_apple_list):
        try:
            classifier.img_list[apple[-3]].crop(apple[:4]).save(f"reports/{report_name}/photos/good/{idx}.jpg")
        except FileNotFoundError:
            pass
    
    for idx, apple in enumerate(classifier.mid_apple_list):
        try:
            classifier.img_list[apple[-3]].crop(apple[:4]).save(f"reports/{report_name}/photos/mid/{idx}.jpg")
        except FileNotFoundError:
            pass
        
    for idx, apple in enumerate(classifier.bad_apple_list):
        try:
            classifier.img_list[apple[-3]].crop(apple[:4]).save(f"reports/{report_name}/photos/bad/{idx}.jpg")
        except FileNotFoundError:
            pass

    for idx, i in enumerate(classifier.results_list):
        i.save()
    
    yolo_images_folder = os.listdir("runs/detect")
    
    num = 0
    for folder in yolo_images_folder:
        img_files = os.listdir(f"runs/detect/{folder}")
        for img in img_files:
            os.replace(f"runs/detect/{folder}/{img}", f"reports/{report_name}/photos/yolo/{num}.jpg")
            num += 1
    
    for folder in yolo_images_folder:
        shutil.rmtree(f"runs/detect/{folder}")
        
    today = datetime.now()    
        
    save_json = {
        "id": report_name,
        "time":{
            "day":str(today.strftime("%d")),
            "month":str(today.strftime("%m")),
            "year":str(today.strftime("%Y")),
            "hour":str(today.strftime("%H")),
            "minute":str(today.strftime("%M")),
            "second":str(today.strftime("%S")),
            },
        "AppleQuality": {
            "Good Apple Number": g_apple_count,
            "Mid Apple Number": mid_apple_count,
            "Bad Apple Number": bad_apple_count,
            "Total Apple Number": g_apple_count+mid_apple_count+bad_apple_count,
        }
    }
    
    with open(f'reports/{report_name}/data.json','w') as f:
        json.dump(save_json, f)
    
@app.route("/reports/<id>")
def get_reports(id):
    reports = os.listdir("reports")
    if id in reports:
        with open(f"reports/{id}/data.json", "r") as f:
            data = json.load(f)
            
        my_data = [{
            "id":str(data["id"]),
            "Number of Good Quality Apple":data["AppleQuality"]["Good Apple Number"],
            "Number of Middle Quality Apple":data["AppleQuality"]["Mid Apple Number"],
            "Number of Bad Quality Apple":data["AppleQuality"]["Bad Apple Number"],
            "Total Number of Apples":data["AppleQuality"]["Good Apple Number"]+data["AppleQuality"]["Mid Apple Number"]+data["AppleQuality"]["Bad Apple Number"]
        }]    
            
            
            
            
        data_df = pd.DataFrame(my_data)
        pie_sf = data_df.drop(["id","Total Number of Apples"],axis=1).sum(axis=0)
        pie_df = pd.DataFrame({'quality':pie_sf.index, 'number':pie_sf.values})
        
        pie_fig = px.pie(pie_df,values="number", names="quality",title="Apple Quality Ratio")
        pie_graph_json =  json.dumps(pie_fig, cls=plotly.utils.PlotlyJSONEncoder)
         
            
        image_count = len(os.listdir(f"reports/{id}/photos/raw"))
            
            

        return render_template("reports_detail.html", data = my_data, pie_json=pie_graph_json,id=id, image_count=image_count)
    else:
        #not found
        return render_template("404.html")

        
def predict_apples():
    model = AppleClassifier.AppleClassifier()
    img_paths = os.listdir("save")
    for i in img_paths:
        link = "save/"+str(i)
        img_input = Image.open(link)
        img_input = ImageOps.exif_transpose(img_input)
        model.calculateApples(img_input)
     
    return model.good_apple_count, model.mid_apple_count, model.bad_apple_count, model
 
if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True, threaded=True)
