# app.py

from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# In-memory list to store the latest alerts
alerts = []

# HTML template with Bootstrap and Font Awesome
template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>雾天交通监控 Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
      integrity="sha512-pbwXkR1ClP8pFYSBWB/06Crx0zAZ59/OYF4qb6QGr8uJTUu+vvY60eRs+4d6S6OumBS6wlero0nOY1wJu4g7VA=="
      crossorigin="anonymous"
      referrerpolicy="no-referrer"
    />
    <style>
        body { padding: 1rem; background-color: #f8f9fa; }
        h3 { font-size: 2.5rem; margin-bottom: 1.5rem; }
        .alert-card { margin-bottom: 1rem; font-size: 1.25rem; }
        .card-title { font-weight: bold; font-size: 1.5rem; }
        .card-text { font-size: 1.25rem; }
        #frame { width: 100%; height: auto; border: 2px solid #007bff; border-radius: 8px; margin-top: 1rem; }
    </style>
</head>
<body>
<div class="container">
    <h3 class="text-center">雾天交通监控 Dashboard</h3>
    <div id="alerts">
        {% if alerts %}
            {% for a in alerts %}
            <div class="card alert-card">
                <div class="card-body">
                    <h6 class="card-title">
                      <i class="fas fa-exclamation-triangle text-danger"></i>
                      高置信度告警
                    </h6>
                    <p class="card-text">{{ a.ts }}: {{ a.cls }} ({{ a.conf }})</p>
                </div>
            </div>
            {% endfor %}
        {% else %}
           <p class="lead text-danger fw-bold">警报！！！</p>
        {% endif %}
    </div>
    <img id="frame" src="{{ latest_frame }}" alt="Detection Frame">
</div>
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
<script>
// 每隔2秒拉取最新告警和最新检测图
setInterval(() => {
    // 拉取告警
    axios.get('/api/alerts').then(res => {
        const container = document.getElementById('alerts');
        container.innerHTML = '';
        if (res.data.length === 0) {
            container.innerHTML = '<p class="text-muted lead">暂无告警</p>';
        } else {
            res.data.forEach(a => {
                container.innerHTML += `
                    <div class="card alert-card">
                        <div class="card-body">
                            <h6 class="card-title">
                              <i class="fas fa-exclamation-triangle text-danger"></i>
                              高置信度告警
                            </h6>
                            <p class="card-text">${a.ts}: ${a.cls} (${a.conf})</p>
                        </div>
                    </div>`;
            });
        }
    });

    // 更新检测图
    const frame = document.getElementById('frame');
    frame.src = '/static/latest.jpg?t=' + Date.now();
}, 2000);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    # 初始渲染页面
    return render_template_string(template,
                                  alerts=alerts,
                                  latest_frame='/static/latest.jpg')

@app.route('/api/alerts')
def get_alerts():
    # 返回当前告警列表（JSON）
    return jsonify(alerts)

@app.route('/api/alert', methods=['POST'])
def post_alert():
    # 接收边缘节点发送的单条告警
    data = request.json
    alerts.insert(0, data)
    # 只保留最新10条
    if len(alerts) > 10:
        alerts.pop()
    return jsonify({"status": "ok"})

@app.route('/api/frame', methods=['POST'])
def post_frame():
    # 接收边缘节点上传的最新检测后图像（二进制JPEG数据）
    img_data = request.data
    os.makedirs('static', exist_ok=True)
    with open('static/latest.jpg', 'wb') as f:
        f.write(img_data)
    return jsonify({"status": "frame received"})

if __name__ == '__main__':
    # 确保静态目录存在，并初始化空文件
    os.makedirs('static', exist_ok=True)
    placeholder = 'static/latest.jpg'
    if not os.path.exists(placeholder):
        open(placeholder, 'wb').close()
    app.run(host='0.0.0.0', port=8080)
