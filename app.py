from flask import Flask, render_template, request, redirect, url_for, session, Response
import cv2

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# 读取用户名和密码信息
def read_users(file_path):
    users = {}
    with open(file_path, 'r') as file:
        for line in file:
            username, password = line.strip().split(':')
            users[username] = password
    return users

# 验证用户名和密码
def authenticate(username, password):
    users = read_users('users.txt')
    if users.get(username) == password:
        return True
    return False

# 捕获摄像头
cap = cv2.VideoCapture(0)

# 读取摄像头
def gen_frames():
    while True:
        success, frame = cap.read()  # 读取一帧
        if not success:
            break
        else:
            # 转换成 JPEG 格式
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # 将每一帧作为流传输到前端

# 登录页面
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session['username'] = username
            return redirect(url_for('video_feed'))
        else:
            return render_template('login.html', message='Invalid username or password.')
    return render_template('login.html')

# 登出
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# 视频页面
@app.route('/video_feed')
def video_feed():
    if 'username' not in session:
        return redirect(url_for('login'))
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # 允许局域网内的其他设备访问
    app.run(host='0.0.0.0', debug=True)
