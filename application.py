import boto3
import boto3.s3
import sys
import os
from flask import Flask, request, render_template, flash, url_for, redirect, send_from_directory
from flask_admin import Admin, BaseView, expose
from models.models import Painting, Administrator
from config.config import session, ADM_EMAIL, ADM_PW, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY\
    , EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO, APP_SECRET_KEY
from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import secure_filename
from boto3.s3.transfer import S3Transfer
import random
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from urllib.parse import urlparse, urljoin
from flask_mail import Mail, Message

UPLOAD_FOLDER = 'static/data/pics'
application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.secret_key = APP_SECRET_KEY
admin = Admin(application, name='Clara Morgado', template_mode='bootstrap3')
# Set the max size of the file to 50MB
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
application.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Login manager set up
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = "login"

application.config.update(
	DEBUG = False,
	#EMAIL SETTINGS
	MAIL_SERVER = 'smtp.gmail.com',
	MAIL_PORT = 465,
	MAIL_USE_SSL = True,
	MAIL_USERNAME = EMAIL_FROM,
	MAIL_PASSWORD = EMAIL_PASSWORD,
    MAIL_DEFAULT_SENDER = EMAIL_FROM
	)

mail = Mail(application)
# Add administrative views here
class AddPaintingView(BaseView):
    @expose('/')
    @login_required
    def index(self):
        return self.render('add_painting.html')
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))


class LoginView(BaseView):
    @expose('/')
    def index(self):
        return self.render('login.html')

    def is_accessible(self):
        return not current_user.is_authenticated

    @application.route('/admin/login/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        user_email = request.form.get('email')
        user_password = request.form.get('password')
        user = session.query(Administrator).filter_by(email = user_email).first()
        if (user != None):
            if (user.check_password(user_password)):
                login_user(user)
                next = request.args.get('next')
                # is_safe_url should check if the url is safe for redirects.
                if not is_safe_url(next):
                    return abort(400)

                return redirect(next or url_for('admin.index'))

        flash('Credenciais incorrectas')
        return render_template('login.html')

class LogoutView(BaseView):
    @expose('/')
    @login_required
    def index(self):
        logout_user()
        return redirect(url_for('admin.index'))
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

class PaintingModelView(ModelView):
    can_create = False
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

admin.add_view(AddPaintingView(name='Novo Quadro', endpoint='paintings'))
admin.add_view(PaintingModelView(Painting, session))
admin.add_view(LoginView(name='Entrar', endpoint='login'))
admin.add_view(LogoutView(name='Sair', endpoint='logout'))

if (session.query(Administrator).filter_by(email = ADM_EMAIL).first() == None):
    try:
        token = str(os.urandom(24))
        new_admin = Administrator(email = ADM_EMAIL, session_token = token)
        new_admin.set_password(ADM_PW)
        session.add(new_admin)
        session.commit()
    except Exception as e:
        print(e)


@login_manager.user_loader
def load_user(user_id):
    return session.query(Administrator).get(user_id)

@application.route('/')
def index():
    paintings = session.query(Painting).order_by(Painting.date)
    count = (paintings.count()//3)
    return render_template("index.html", paintings = paintings, count = count)

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

@application.route('/painting/inquire', methods=['POST'])
def inquire():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    painting_id = request.form.get('painting_id')
    link = request.url_root[:-1] + url_for('show_painting', id = painting_id)

    try:
        msg = Message('[Pedido de Informações] ClaraMorgado', recipients= [EMAIL_TO])
        msg.html = '''Olá, recebeu uma nova mensagem do site <a href="{url}">Clara Morgado</a>
            sobre o seguinte <a href="{link}">quadro</a>.<br><br>
            De: {name} (<a href="mailto:{email}">{email}</a>)<br>
            Assunto: {subject}<br>
            Mensagem: "{message}"'''.format(url = request.url_root, link = link, name = name, email = email, subject = subject, message = message)
        mail.send(message=msg)

    except Exception as e:
        print (e)
        flash('Erro ao enviar a mensagem. Por favor, tente mais tarde')
        return redirect(url_for('show_painting', id=painting_id))
    flash('Mensagem enviada com sucesso')
    return redirect(url_for('show_painting', id=painting_id))


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0')
