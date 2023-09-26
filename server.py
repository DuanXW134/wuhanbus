from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import os
import base64
import json
import requests
import urllib.parse
from cropAndOcr import myOCR

API_KEY = "p7l1l7zzGQe2KQySaXBNSpTD"
SECRET_KEY = "C2SlDmvhxeGCVaTDhGoI8Q0gQok98wz0"
count = 1
number = ''


def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY,
    }
    return str(requests.post(url, params=params).json().get("access_token"))


app = Flask(__name__)

# 文件上传目录
app.config['UPLOAD_FOLDER'] = 'uploads/'
# 支持的文件格式
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # 集合类型


# 判断文件名是否是我们支持的格式
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def hello_world():
    return 'hello world'


@app.route('/upload', methods=['POST'])
def upload():
    upload_file = request.files['image']
    if upload_file and allowed_file(upload_file.filename):
        filename = secure_filename(upload_file.filename)
        # 将文件保存到 uploads 目录，文件名同上传时使用的文件名
        upload_file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
        return 'info is ' + request.form.get('info', '') + '. success'
    else:
        return 'failed'


@app.route('/test', methods=['POST'])
def test():
    print(request.form)
    print(request.data)
    print(request.content_type)
    return "hello world"


@app.route('/image', methods=['POST'])
def upload_image():
    global count
    global number
    # 获取上传的数据（整个JSON字符串）
    data_json = request.data  # 获取整个JSON字符串，假设它是唯一的字段

    if data_json:
        try:
            data_dict = json.loads(data_json)  # 将JSON字符串解析为字典
            image_data_value = data_dict.get('imageData')  # 获取imageData字段的值

            if image_data_value:
                # 现在你可以处理imageData的值，比如进行base64解码和保存
                image_data_binary = base64.b64decode(image_data_value)

                # 保存图片数据到.png文件（假设是PNG格式）
                if os.path.exists('/FlaskTest/save.jpg'):
                    os.remove('/FlaskTest/save.jpg')

                with open('/FlaskTest/save.jpg', 'wb') as f:
                    f.write(image_data_binary)

                print("ok")
                if count == 0:
                    count = 1
                    number = myOCR('/FlaskTest/save.jpg')
                    print(number+'once more')
                    return
                else:
                    count = 0
                    result = myOCR('/FlaskTest/save.jpg')
                    print('second number' + result)
                    if number == result:
                        number = ''
                        return result
                    else:
                        number = ''
                        return
            else:
                print("没有值")
                return '未找到imageData字段的值'
        except json.JSONDecodeError as e:
            print("JSON解析错误:", str(e))
            return 'JSON解析错误'
    else:
        print("未找到JSON字符串")
        return '未找到JSON字符串'


@app.route("/getSound/<text>", methods=["GET"])
def getSound(text):
    url = "https://tsn.baidu.com/text2audio"
    payload = "tok=" + get_access_token() + "&tex=" + urllib.parse.quote(
        text) + "&cuid=8ARbMuwNIOIiwsBdXNdtaosepGjyeUWs&ctp=1&lan=zh&spd=5&pit=5&vol=5&per=1&aue=3"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "*/*"}
    response = requests.request("POST", url, headers=headers, data=payload)
    with open("./sound.mp3", "wb") as file:
        file.write(response.content)
        file.close()
    return send_file("./sound.mp3", as_attachment=True)


@app.route('/piggy', methods=['POST', 'GET'])
def piggy():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
