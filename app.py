import time
from os.path import exists, dirname
from pprint import pprint
from aiLibs import funs_decode_checkpos
import cv2

from aiLibs import ImageProcessing
from aiLibs.ProjectConfigManager import ConfigManager

import os

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy  # pip install Flask-SQLAlchemy
from functools import wraps
from flask import make_response
import datetime
import string

from aiLibs.ProjectLog import taLogClass, tt

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + basedir + '/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.secret_key = b'Tuan anh Foxconn.AI'


# Định nghĩa mô hình User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    role = db.Column(db.String(10))
    remember_token = db.Column(db.String(100), unique=True)

    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role


def generate_remember_token():
    dt7days = datetime.datetime.now() + datetime.timedelta(days=7)
    dt7days = dt7days.strftime("%Y-%m-%d--%H-%M-%S.%f")
    return dt7days


def is_token_expired(user):
    if user.remember_token is None:
        return True
    else:
        token_expiry = datetime.datetime.strptime(user.remember_token, "%Y-%m-%d--%H-%M-%S.%f")
        return token_expiry < datetime.datetime.now()


@app.before_request
def check_remembered_user():
    if 'username' not in session:
        # Kiểm tra remember me cookie
        remember_token = request.cookies.get('remember_token')

        if remember_token is not None:
            # Tìm người dùng với remember me token tương ứng
            user = User.query.filter_by(remember_token=remember_token).first()

            if user and not is_token_expired(user):
                # Đánh dấu người dùng là đã đăng nhập và tạo session cookie mới
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:  # Lưu thông tin người dùng đăng nhập vào session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            if 'remember_me' in request.form:
                remember_me = request.form['remember_me']
                if remember_me:
                    # Tạo remember me token ngẫu nhiên
                    remember_token = generate_remember_token()

                    # Lưu remember me token vào cơ sở dữ liệu của người dùng
                    user.remember_token = remember_token
                    db.session.commit()

                    # Tạo remember me cookie và đặt thời gian tồn tại là 3 tháng
                    remember_cookie = make_response(render_template('Modules/show_messages.html', mess="Đăng nhập thành công!"))
                    remember_cookie.set_cookie('remember_token', remember_token, max_age=90 * 24 * 60 * 60)

                    # Gửi response với remember me cookie
                    return remember_cookie
            return redirect(url_for('index'))
        else:
            return render_template('Modules/show_messages.html', mess='Sai tên đăng nhập hoặc mật khẩu')
    return render_template('login.html')


# Xử lý đăng xuất
@app.route('/logout')
def logout():  # Xóa thông tin người dùng trong session
    remember_token = request.cookies.get('remember_token')
    if remember_token is not None:
        # Tìm người dùng với remember me token tương ứng
        user = User.query.filter_by(remember_token=remember_token).first()
        if user is not None:
            # Xóa remember me token của người dùng
            user.remember_token = None
            db.session.commit()
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))





def CodelandUsernameValidation(strParam):
    match = string.ascii_letters + string.digits + '_'
    if not all([x in match for x in strParam]):
        return False
    if not (4 <= len(strParam) <= 25):
        return False
    if not strParam[0].isalpha():
        return False
    if strParam[-1:] == '_':
        return False
    return True


# keep this function call here

# Trang tạo người dùng
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        if not CodelandUsernameValidation(username):
            return render_template('Modules/show_messages.html', mess='Tên người dùng không hợp lệ')
        password = request.form['password']
        password1 = request.form['password1']
        if password != password1: return render_template('Modules/show_messages.html', mess='Mật khẩu không trùng khớp')
        role = 'user'
        if 'role' in request.form: role = request.form['role']
        try:
            new_user = User(username, password, role)
            db.session.add(new_user)
            db.session.commit()
        except:
            return render_template('Modules/show_messages.html', mess="User đã tồn tại trong hệ thống, hãy chọn tên khác")
        return redirect(url_for('index'))
    return render_template('login.html')


# =================================================================
# Decorator kiểm tra trạng thái đăng nhập
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra xem người dùng đã đăng nhập hay chưa
        if 'username' not in session:
            # Nếu chưa đăng nhập, chuyển hướng đến trang đăng nhập
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# Decorator kiểm tra quyền admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra quyền của người dùng
        if session.get('role') not in ['Admin', 'Manager']:
            # Nếu không có quyền admin, chuyển hướng đến trang cấm truy cập: access_denied
            return render_template('Modules/show_messages.html', mess="Access Denied! Bạn không có quyền truy cập nội dung này!")
        return f(*args, **kwargs)

    return decorated_function


# Trang yêu cầu quyền admin
@app.route('/admin_only')
@login_required
@admin_required
def admin_only():
    return render_template('admin_only.html')


# @app.route('/access_denied')
# def access_denied():
#


# =================================================================
# Route cho trang admin
@app.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    if request.method == 'POST':
        data = request.get_json()
        user_id = data['user_id']
        role = data['role']
        user = User.query.get(user_id)
        # user = session.get(user_id)
        user.role = role
        db.session.commit()  # Cập nhật vai trò của người dùng trong cơ sở dữ liệu
        return jsonify({'status': 'success'})
    else:
        # Lấy danh sách người dùng từ cơ sở dữ liệu
        users = User.query.all()
        return render_template('Modules/admin.html', users=users)


# ------------------------------------------------------------------------------------------------------------------------

config = ConfigManager("AI_Data/config/config.yaml")


# create a section and add some keys


# ---- LOGIN INFORMATION--------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------------------------------

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/update', methods=['POST'])
def update():
    action = request.form.get('action')
    mID = request.form.get('mID')

    if action == 'Update':
        if mID == 'inp1':
            return {'message': 'Updated v1 successfully!'}
        if mID == 'inp2':
            return {'message': 'Updated v2 successfully!'}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5566)
