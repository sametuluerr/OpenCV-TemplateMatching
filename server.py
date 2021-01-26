import os
import time
import shutil
from camera import VideoCamera
from werkzeug.utils import secure_filename
from templatematching import templateMatching
from flask_fontawesome import FontAwesome
from flask import Flask, flash, request, redirect, render_template, session, url_for, Response


app = Flask(__name__)
fa = FontAwesome(app)
app.secret_key = "lose_yourself"

# Yüklenebilecek maksimum dosya boyutunu belirliyoruz
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB

# Sayfa önbelleğinin temizlenmesi için
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Kabul edilen dosya uzantıları
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Resimlerin dosya yolunu fonksiyona göndermek için tanımlanan dizi
images = []


# dosya uygunluğunu kontrol eden fonksiyon
def allowedFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def createUploadDirectory():
    path = os.getcwd()
    UPLOAD_FOLDER = os.path.join(path, 'static/uploads/') + str(time.time())
    # Eğer Uploads klasörü yoksa oluştur
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    session["IMAGE_UPLOADS"] = UPLOAD_FOLDER


def deleteUploadDirectory():
    if 'IMAGE_UPLOADS' in session:
        if os.path.isdir(session['IMAGE_UPLOADS']):
            shutil.rmtree(session['IMAGE_UPLOADS'])
        session['IMAGE_UPLOADS'] = ''


def gen(camera):
    camera.template_config()
    try:
        while True:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    except:
        del camera

# Ana Sayfa
@app.route('/')
def run():
    session.pop('_flashes', None)
    deleteUploadDirectory()
    return render_template('index.html', page='main')

# GET
@app.route('/uploadPhotos')
def upload_form():
    deleteUploadDirectory()
    createUploadDirectory()
    return render_template('uploadPhotos.html')


# POST
@app.route('/uploadPhotos', methods=['POST'])
def uploadPhotos():
    if request.method == 'POST':
        if len(images) >= 2:
            images.clear()
        # yüklenen dosyaları al
        for files in request.files.getlist('files[]'):
            if len(files.filename) == 0:
                flash("Lütfen her iki fotoğrafı da seçiniz!")
                deleteUploadDirectory()
                return redirect(request.url)
            if files and allowedFile(files.filename):
                # içinde '/' gibi karakterleri güvenli hale getiriyoruz
                filename = secure_filename(files.filename)
                images.append(os.path.join(
                    session["IMAGE_UPLOADS"], filename))
                # yeni ismini almış dosyayı kaydet
                files.save(os.path.join(session["IMAGE_UPLOADS"], filename))
            else:
                flash("Lütfen geçerli dosya uzantılarını(jpg, png, jpeg) seçiniz!")
                return redirect(request.url)
        try:
            threshold = templateMatching(
                images[0], images[1], session["IMAGE_UPLOADS"] + "/result.jpg")
        except:
            deleteUploadDirectory()
            flash("Yüklenen fotoğraf içinde, aranan şablon fotoğrafı bulunamadı.")
            return redirect(request.url)

        return redirect(url_for('completed', threshold=threshold))


# GET
@app.route('/uploadTemplate')
def uploadTemplateForm():
    deleteUploadDirectory()
    createUploadDirectory()
    return render_template('uploadTemplate.html')

# POST
@app.route('/uploadTemplate', methods=['POST'])
def uploadTemplate():
    if request.method == 'POST':
        # yüklenen dosyayı al
        file = request.files["file"]
        if file.filename == "":
            deleteUploadDirectory()
            flash("Lütfen bir fotoğraf seçiniz!")
            return redirect(request.url)
        if file and allowedFile(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(session["IMAGE_UPLOADS"], filename))
            session["FILE_NAME"] = filename
            return redirect("/realtime")
        else:
            flash("Lütfen geçerli dosya uzantılarını(jpg, png, jpeg) seçiniz!")
            return redirect(request.url)


# GET
@app.route('/completed')
def completed():
    threshold = request.args['threshold']
    resultsrc = "/static" + \
        session["IMAGE_UPLOADS"].split('static')[1] + "/result.jpg"
    return render_template('completed.html', resultsrc=resultsrc, threshold=threshold)

# POST
@app.route('/completed', methods=['POST'])
def completedthreshold():
    if request.method == 'POST':
        threshold = templateMatching(
            images[0], images[1], session["IMAGE_UPLOADS"] + "/result.jpg", request.form['value'])
        return redirect(url_for('completed', threshold=threshold))

# GET
@app.route('/video_feed')
def video_feed():
    img = os.path.join(session["IMAGE_UPLOADS"], session["FILE_NAME"])
    camera = VideoCamera(img)
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# GET
@app.route('/realtime')
def realtime():
    return render_template('realtime.html')

# GET
@app.route('/hdiw')
def hdiw():
    return render_template('hdiw.html', page='hdiw')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
