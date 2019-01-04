import os
import uuid
import json
import sys
import base64
import requests
import matplotlib.pyplot as plt

from PIL import Image
from io import BytesIO
from flask import Flask, render_template, request, send_from_directory, g, session,make_response
from matplotlib.patches import Polygon
from fpdf import FPDF

from .scripts.utils import make_request, render_analysis, get_text

# sys.path.append('/textextractor')

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
UPLOAD_FOLDER = '/tmp/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/submit/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/jpg_to_pdf')
def jpg_to_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    text_list = session.get('text')
    for line in text_list:
        pdf.write(5, str(line))
        pdf.ln()
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers.set('Content-Disposition', 'attachment', filename='text_detected' + '.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response

    

@app.route('/display_plot/<filename>')
def display_plot(filename):
    print("jhj")
    with open(('/tmp/'+filename), 'rb') as image:
    #     img_data = image.read()
        print("INNNN")

        plt.figure(figsize=(15, 15))
        image = Image.open(BytesIO(image.read()))
        print(image)
        ax = plt.imshow(image)
        polygons = session.get('polygons')
        for polygon in polygons:
            vertices = [(polygon[0][i], polygon[0][i+1])
            for i in range(0, len(polygon[0]), 2)]
            text     = polygon[1]
            patch    = Polygon(vertices, closed=True, fill=False, linewidth=2, color='y')
            ax.axes.add_patch(patch)
            plt.text(vertices[0][0], vertices[0][1], text, fontsize=20, va="top")
        _ = plt.axis("off")
        plt.savefig(os.path.join(UPLOAD_FOLDER, 'new_plot.jpeg'))
    # print('  HHH {}'.format(send_from_directory(UPLOAD_FOLDER, 'new_plot.jpeg')))
    return send_from_directory(UPLOAD_FOLDER, 'new_plot.jpeg')



@app.route('/submit', methods=['GET', 'POST'])
def submit():
    '''
    This function takes in an image,
    and results in the text detected page
    '''

    if request.method == 'POST':
        
        file_img = request.files['u_img']
        choice = request.form['options']
        # print(request.args)
        print(choice)
        g.img = file_img
        extension = os.path.splitext(file_img.filename)[1]
        f_name = str(uuid.uuid4()) + extension
        # print(f_name)
        # print(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        file_img.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        # print(type(files))
        # img = files.read()
        # print(type(img))
        # 
        # # print(response)
        img_data = None
        # print(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        with open(('/tmp/'+ f_name), 'rb') as image:
           
            img_data = image.read()
        #     output = BytesIO()
        #     print('TYPE OF IMAGE {}'.format(image))
        #     image.save(output, format='JPEG')
        # img_data = output.getvalue()
        # 
        
        response,operation_url,headers=make_request(img_data, choice)
        analysis = render_analysis(response,operation_url,headers)
        polygons,text = get_text(analysis)
        session['polygons'] = polygons
        session['text'] = text
        print(text)
        # print('HELOO {}'.format(type(img_data)) )
        print('YAYYY')
        data_text = list()
        for item in text:
            data_text.append(item)
        return(render_template('submit.html', text=data_text, filename=f_name, polygons=polygons))
        
    return(render_template('submit.html'))
    

if __name__ == '__main__':
    app.run(debug=True)
