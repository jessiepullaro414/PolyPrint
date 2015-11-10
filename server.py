from flask import Flask, flash, redirect, url_for, request, get_flashed_messages, render_template, send_from_directory
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
import os
from werkzeug import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

#Start Server at Port 5000
if os.getenv("VCAP_APP_PORT"):
    port = int(os.getenv("VCAP_APP_PORT"))
else:
    port = 80

# use for encrypt session
app.config['SECRET_KEY'] = 'b56936b292f44fc397f77d882b3418ee'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

# For a given file, return whether it's an allowed types or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

login_manager = LoginManager()
login_manager.init_app(app)

class UserNotFoundError(Exception):
    pass
class User(UserMixin):
    '''Simple User class'''
    USERS = {
        # user : password
        'admin': 'admin'
    }

    def __init__(self, id):
        if not id in self.USERS:
            raise UserNotFoundError()
        self.id = id
        self.password = self.USERS[id]

    @classmethod
    def get(self_class, id):
        '''Return user instance of id, return None if not exist'''
        try:
            return self_class(id)
        except UserNotFoundError:
            return None

# Flask-Login use this to reload the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return User.get(id)

@app.route('/')
def index():
    if current_user.is_authenticated():
        user = user=current_user.get_id()
        return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/dashboard')
def dash():
    if current_user.is_authenticated():
        user = user=current_user.get_id()
        return render_template('dashboard.html',user=user or 'Guest')
    else:
        return redirect('/')

@app.route('/login/student')
def student_login():
    if current_user.is_authenticated():
        user = user=current_user.get_id()
        return redirect('/dashboard')
    else:
        return render_template('student_login.html')

@app.route('/login/admin')
def admin_login():
    if current_user.is_authenticated():
        user = user=current_user.get_id()
        return redirect('/dashboard')
    else:
        return render_template('admin_login.html')

@app.route('/login/check', methods=['post'])
def login_check():
    # validate username and password
    user = User.get(request.form['username'])
    if (user and user.password == request.form['password']):
        login_user(user)
    else:
        flash('Username or password incorrect')

    return redirect(url_for('dash'))

@app.route('/logout')
def logout():
    logout_user()
    if current_user.is_authenticated():
        user = user=current_user.get_id()
        return redirect('/dashboard')
    else:
        return render_template('student_login.html')

@app.route('/status')
def printer_status():
    return render_template('status.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug = True)
