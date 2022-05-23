from flask import Flask, render_template, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL
from sqlalchemy.sql import func
from sqlalchemy import create_engine
import os
import ffmpeg_streaming
from var_dump import  var_dump
from ffmpeg_streaming import Formats, Bitrate, Representation, Size



from werkzeug.utils import secure_filename, redirect

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost:3308/videostream_db'

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_PORT'] = 3308
# app.config['MYSQL_DB'] = 'videostream_db'

# VOLUME_PATH = './uploads/videos'

# Create a directory in a known location to save files to.
uploads_dir = os.path.join(app.instance_path, '/uploads/videos')
os.makedirs(uploads_dir, exist_ok=True)
ALLOWED_EXTENSIONS = set(['mp4'])


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    photo_path = db.Column(db.String(100), nullable=False)
    comments = db.Column(db.TEXT)

    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    def __init__(self, title, photo_path, comments):
        self.title = title
        self.photo_path = photo_path
        self.comments = comments





@app.route('/')
def index():
    videos = Video.query.all()

    return render_template('index.html',videos=videos)

@app.route('/admin/')
def admin_index():
    videos = Video.query.all()

    return render_template('admin_index.html',videos=videos)


@app.route('/admin/new', methods=["GET", "POST"])
def new_record():
    if request.method == 'POST' :
        file = request.files['video_clip']



       # file_path = make_dash(profile)
        fpath = os.path.join(uploads_dir, secure_filename(file.filename))
        var_dump(fpath)
        file.save(fpath)


        file_path = make_dash('D:/uploads/videos/town_gal_pt_1.mp4')

        #v = Video
        title =request.form['title']
        photo_path =file_path
        comments = request.form['notes']

        v = Video(title=title,photo_path=photo_path,comments=comments)
        #video = Video(title=request.form['title'], photo_path=file_path, notes=request.form['notes'])
        db.session.add(v)
        db.session.commit()

        #flash('You were successfully logged in')

        return redirect(url_for('admin_index'))

    return render_template('create.html')
@app.route('/selected_video/<int:id>')
def play_video(id:int):

    selected_video = Video.query.get(id)

    return render_template('video_page.html',selected_video= selected_video)




def make_dash(file):
    from ffmpeg_streaming import Formats

    var_dump(file)

    #file_path = os.path.join(uploads_dir, secure_filename(file.filename))

    video = ffmpeg_streaming.input(file)
    var_dump(video)

    _144p = Representation(Size(256, 144), Bitrate(95 * 1024, 64 * 1024))
    _240p = Representation(Size(426, 240), Bitrate(150 * 1024, 94 * 1024))
    _360p = Representation(Size(640, 360), Bitrate(276 * 1024, 128 * 1024))
    _480p = Representation(Size(854, 480), Bitrate(750 * 1024, 192 * 1024))
    _720p = Representation(Size(1280, 720), Bitrate(2048 * 1024, 320 * 1024))
    _1080p = Representation(Size(1920, 1080), Bitrate(4096 * 1024, 320 * 1024))
    _2k = Representation(Size(2560, 1440), Bitrate(6144 * 1024, 320 * 1024))
    _4k = Representation(Size(3840, 2160), Bitrate(17408 * 1024, 320 * 1024))
    dash = video.dash(Formats.h264())
    dash.representations(_144p, _240p, _360p, _480p, _720p, _1080p, _2k, _4k)

    #dash.auto_generate_representations

    #gen_path = 'uploads/media' + 'file.filename' + '.mpd'
    dash.output('D:/uploads/media/test.mpd')


    return gen_path






if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
