# استيراد المكتبات المطلوبة
from flask import Flask, render_template_string, request, redirect
import ping3
from datetime import datetime
import json
import webbrowser
import threading

# إنشاء تطبيق Flask
app = Flask(__name__)

# قائمة الأجهزة الافتراضية للمراقبة
devices = [
    {"name": "Google DNS", "ip": "8.8.8.8"},
    {"name": "Cloudflare DNS", "ip": "1.1.1.1"},
    {"name": "Local Gateway", "ip": "192.168.1.1"},
]

# دالة للتحقق من حالة الجهاز عبر Ping
def check_device(ip):
    try:
        response = ping3.ping(ip, timeout=2)
        if response is not None:
            return True, round(response * 1000, 2)
        return False, None
    except:
        return False, None

# واجهة HTML للداشبورد
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Monitor</title>
    <!-- تحديث تلقائي كل 30 ثانية -->
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial; background: #0d1117; color: #fff; padding: 30px; }
        h1 { color: #58a6ff; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #161b22; padding: 12px; text-align: left; color: #58a6ff; }
        td { padding: 12px; border-bottom: 1px solid #30363d; }
        .online { color: #3fb950; font-weight: bold; }
        .offline { color: #f85149; font-weight: bold; }
        .time { color: #8b949e; margin-bottom: 20px; }
        tr:hover { background: #161b22; }
        .form-box { background: #161b22; padding: 20px; border-radius: 8px; margin-top: 30px; width: 400px; }
        input { background: #0d1117; border: 1px solid #30363d; color: #fff; padding: 8px; width: 100%; margin-bottom: 10px; border-radius: 4px; }
        button { background: #238636; color: #fff; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-right: 10px; }
        button.save { background: #1f6feb; }
        button.delete { background: #da3633; padding: 6px 12px; }
    </style>
</head>
<body>
    <h1>🖥️ Network Monitoring Dashboard</h1>
    <p class="time">Last updated: {{ time }} — Auto refresh every 30 sec</p>
    
    <!-- جدول عرض الأجهزة وحالتها -->
    <table>
        <tr>
            <th>Device</th>
            <th>IP Address</th>
            <th>Status</th>
            <th>Response Time</th>
            <th>Action</th>
        </tr>
        {% for device in devices %}
        <tr>
            <td>{{ device.name }}</td>
            <td>{{ device.ip }}</td>
            <td class="{{ 'online' if device.status == 'Online' else 'offline' }}">
                {{ '✅ Online' if device.status == 'Online' else '❌ Offline' }}
            </td>
            <td>{{ device.response_time }}</td>
            <!-- زر حذف الجهاز -->
            <td>
                <form action="/delete" method="post" style="display:inline">
                    <input type="hidden" name="ip" value="{{ device.ip }}">
                    <button class="delete" type="submit">🗑️</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>

    <!-- فورم إضافة جهاز جديد وحفظ التقرير -->
    <div class="form-box">
        <h3 style="color:#58a6ff; margin-top:0">➕ Add Device</h3>
        <form action="/add" method="post">
            <input type="text" name="name" placeholder="Device name" required>
            <input type="text" name="ip" placeholder="IP Address" required>
            <button type="submit">Add</button>
            <button class="save" type="button" onclick="window.location='/save'">💾 Save Report</button>
        </form>
    </div>
</body>
</html>
"""

# الصفحة الرئيسية — تعرض حالة كل الأجهزة
@app.route("/")
def index():
    results = []
    for device in devices:
        status, response_time = check_device(device["ip"])
        results.append({
            "name": device["name"],
            "ip": device["ip"],
            "status": "Online" if status else "Offline",
            "response_time": f"{response_time} ms" if response_time else "N/A"
        })
    return render_template_string(HTML, devices=results, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# إضافة جهاز جديد للقائمة
@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name")
    ip = request.form.get("ip")
    devices.append({"name": name, "ip": ip})
    return redirect("/")

# حذف جهاز من القائمة
@app.route("/delete", methods=["POST"])
def delete():
    ip = request.form.get("ip")
    devices[:] = [d for d in devices if d["ip"] != ip]
    return redirect("/")

# حفظ تقرير JSON بالنتائج الحالية
@app.route("/save")
def save():
    results = []
    for device in devices:
        status, response_time = check_device(device["ip"])
        results.append({
            "device": device["name"],
            "ip": device["ip"],
            "status": "Online" if status else "Offline",
            "response_time": f"{response_time} ms" if response_time else "N/A",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=4)
    return f"<h2 style='font-family:Arial;color:green'>Report saved: {filename}</h2><a href='/' style='color:white'>Back</a>"

# فتح المتصفح تلقائياً عند التشغيل
def open_browser():
    webbrowser.open("http://localhost:5000")

# تشغيل التطبيق
if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=False)