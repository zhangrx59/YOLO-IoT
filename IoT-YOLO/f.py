from f import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# In-memory queue for alerts
alerts = []

# HTML template using Bootstrap for mobile
template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>雾天交通监控</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding-top: 1rem; }
        .alert-card { margin-bottom: 1rem; }
        .frame-img { width: 100%; height: auto; border-radius: 8px; }
    </style>
</head>
<body class="bg-light">
<div class="container">
    <h3 class="text-center mb-4">雾天交通监控 Dashboard</h3>
    <div id="alerts" class="mb-4">
        {% for a in alerts %}
        <div class="card alert-card">
            <div class="card-body">
                <h6 class="card-title">高置信度告警</h6>
                <p class="card-text">{{ a.ts }}: {{ a.cls }} ({{ a.conf }})</p>
            </div>
        </div>
        {% else %}
        <p class="text-muted">暂无告警</p>
        {% endfor %}
    </div>
    <img id="frame" src="{{ latest_frame }}" class="frame-img" alt="Latest Frame">
</div>
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
<script>
// Poll for alerts and latest frame
setInterval(() => {
    axios.get('/api/alerts').then(res => {
        const container = document.getElementById('alerts');
        container.innerHTML = '';
        if (res.data.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无告警</p>';
        } else {
            res.data.forEach(a => {
                container.innerHTML += `<div class="card alert-card">
                    <div class="card-body">
                        <h6 class="card-title">高置信度告警</h6>
                        <p class="card-text">${a.ts}: ${a.cls} (${a.conf})</p>
                    </div>
                </div>`;
            });
        }
    });
    // update frame
    const frame = document.getElementById('frame');
    frame.src = '/static/latest.jpg?t=' + new Date().getTime();
}, 2000);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    latest_frame = '/static/latest.jpg'
    return render_template_string(template, alerts=alerts, latest_frame=latest_frame)

@app.route('/api/alerts')
def get_alerts():
    return jsonify(alerts)

@app.route('/api/alert', methods=['POST'])
def post_alert():
    data = request.json
    alerts.insert(0, data)
    if len(alerts) > 10:
        alerts.pop()
    return jsonify({"status": "ok"})

@app.route('/api/frame', methods=['POST'])
def post_frame():
    img_data = request.data
    # Save raw image bytes to static/latest.jpg
    with open('static/latest.jpg', 'wb') as f:
        f.write(img_data)
    return jsonify({"status": "frame received"})

if __name__ == '__main__':
    import os
    os.makedirs('static', exist_ok=True)
    # Initialize a placeholder image
    with open('static/latest.jpg', 'wb') as f:
        f.write(b'')  # empty placeholder
    app.run(host='0.0.0.0', port=8080)

