from flask import Flask, request, render_template, flash, url_for, redirect
from flask_admin import Admin, BaseView, expose
from models.models import Painting, Administrator
from config.config import session, ADM_EMAIL, ADM_PW
from flask_admin.contrib.sqla import ModelView
import boto3
import boto3.s3
import sys
import os
from werkzeug.utils import secure_filename
from boto3.s3.transfer import S3Transfer
import random
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

UPLOAD_FOLDER = 'static/data/pics'
application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.secret_key = 'claramorgado'
admin = Admin(application, name='Clara Morgado', template_mode='bootstrap3')
# Set the max size of the file to 50MB
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
application.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Login manager set up
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = "admin.login"

# Add administrative views here
class AddPaintingView(BaseView):
    @expose('/')
    @login_required
    def index(self):
        return self.render('add_painting.html')

class PaintingModelView(ModelView):
    can_create = False

admin.add_view(AddPaintingView(name='Novo Quadro', endpoint='paintings'))
admin.add_view(PaintingModelView(Painting, session))

if (session.query(Administrator).filter_by(email = ADM_EMAIL).first() == None):
    try:
        new_admin = Administrator(email = ADM_EMAIL)
        new_admin.set_password(ADM_PW)
        print(new_admin.pw_hash)
        session.add(new_admin)
        session.commit()
    except Exception as e:
        print(e)


@login_manager.user_loader
def load_user(token):
  user = session.query(Administrador).filter(Administrador.session_token == token).first()
  return user

# Login logic HERE
@application.route('/admin/login')
def login():
    user_email = request.form.get('email')
    user_password = request.form.get('password')
    user = session.query(Administrator).filter_by(email = user_email).first()
    if (user != None):
        if (user.check_password(user_password)):
            login_user(user)
            return redirect(url_for('admin.index'))

    flash('Credenciais incorrectas')
    return redirect(url_for('admin.login'))

@application.route('/')
def index():
    paintings = session.query(Painting).order_by(Painting.date)
    return render_template("index.html", paintings = paintings)

@application.route("/admin/paintings/create_painting", methods=["POST"])
@login_required
def create_painting():
    name = request.form.get('name')
    style = request.form.get('style')
    date = request.form.get('date')
    size = request.form.get('size')

    if name is None or style is None or date is None:
        # HANDLE ERROR HERE
        flash('Make sure every field is filled')
        return redirect(url_for('create_painting'))

    if 'file' in request.files:
        print ("File in request files is true!")
        file = request.files['file']
        if file.filename == '':
            file = None
        if file and allowed_file(file.filename):
            try:
                filename = str(secure_filename(file.filename))
                filename = str(random.random()) + filename
                file_location = os.path.join(application.config['UPLOAD_FOLDER'], filename)
                file.save(file_location)
                credentials = {
                    'aws_access_key_id': AWS_ACCESS_KEY_ID,
                    'aws_secret_access_key': AWS_SECRET_ACCESS_KEY
                }
                bucket='clara-morgado'
                client = boto3.client('s3', 'eu-west-1', **credentials)
                transfer = S3Transfer(client)
                transfer.upload_file(file_location, bucket, filename,
                                     extra_args={'ACL': 'public-read'})

                file_url = '%s/%s/%s' % (client.meta.endpoint_url, bucket, filename)
                os.remove(file_location)
            except Exception as e:
                print(e) # Just for debug
                flash('Erro a adicionar pintura')
                return redirect(url_for('admin.index'))
    else:
        file = None

    try:
        new_painting = Painting(name = name, style = style, size = size, date = date, image = file_url)
        session.add(new_painting)
        session.commit()
    except Exception as e:
        print(e) # Just for debug
        flash('Erro a adicionar pintura')
        return redirect(url_for('admin.index'))

    flash('Adicionado com sucesso')
    return redirect(url_for('admin.index'))


@application.route('/painting/<int:id>')
def show_painting(id):
    painting = session.query(Painting).get(id)
    if painting is None:
        return "404"
    return render_template('painting.html', painting = painting)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0')
