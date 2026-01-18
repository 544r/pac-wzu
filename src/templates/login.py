"""
登录页面模板
"""

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>温州大学成绩查询</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; min-height: 100vh; background: linear-gradient(135deg, #1e3c72, #2a5298); display: flex; align-items: center; justify-content: center; padding: 20px; }
        .card { width: 100%; max-width: 400px; background: white; border-radius: 16px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo-icon { font-size: 48px; }
        .logo h1 { font-size: 22px; color: #1a1a2e; margin-top: 10px; }
        .logo p { color: #666; font-size: 14px; margin-top: 5px; }
        .tabs { display: flex; margin-bottom: 24px; background: #f0f0f0; border-radius: 8px; padding: 4px; }
        .tab { flex: 1; padding: 10px; text-align: center; cursor: pointer; border-radius: 6px; font-size: 14px; font-weight: 500; transition: all 0.2s; }
        .tab.active { background: white; color: #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .tab:not(.active) { color: #666; }
        .form-panel { display: none; }
        .form-panel.active { display: block; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-size: 14px; font-weight: 600; color: #333; margin-bottom: 8px; }
        .form-group input { width: 100%; padding: 12px; font-size: 16px; border: 2px solid #e0e0e0; border-radius: 8px; outline: none; }
        .form-group input:focus { border-color: #667eea; }
        .btn { width: 100%; padding: 14px; font-size: 16px; font-weight: 600; color: #fff; background: linear-gradient(135deg, #667eea, #764ba2); border: none; border-radius: 8px; cursor: pointer; }
        .btn:disabled { opacity: 0.6; }
        .error { background: #fee; color: #c00; padding: 12px; border-radius: 8px; margin-top: 16px; display: none; font-size: 14px; }
        .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #999; }
        .footer a { color: #667eea; }
        .hint { font-size: 12px; color: #999; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">
            <div class="logo-icon">🎓</div>
            <h1>温大成绩助手</h1>
            <p>支持成绩变动邮件推送</p>
        </div>
        <div class="tabs">
            <div class="tab active" onclick="switchTab('account')">账号登录</div>
            <div class="tab" onclick="switchTab('pin')">密钥登录</div>
        </div>
        <div id="accountPanel" class="form-panel active">
            <form id="loginForm">
                <div class="form-group">
                    <label>学号</label>
                    <input type="text" id="username" placeholder="请输入学号" required>
                </div>
                <div class="form-group">
                    <label>密码</label>
                    <input type="password" id="password" placeholder="教务系统密码" required>
                </div>
                <button type="submit" class="btn" id="loginBtn">登 录</button>
            </form>
        </div>
        <div id="pinPanel" class="form-panel">
            <form id="pinForm">
                <div class="form-group">
                    <label>快捷密钥</label>
                    <input type="password" id="pinCode" placeholder="输入你设置的密钥" required>
                    <p class="hint">💡 使用密钥自动登录，无需输入学号密码</p>
                </div>
                <button type="submit" class="btn" id="pinBtn">密钥登录</button>
            </form>
        </div>
        <div class="error" id="errorMsg"></div>
        <div class="footer"><p>🔒 密码加密传输存储 | <a href="/admin">管理后台</a></p></div>
    </div>
    <script>
        function switchTab(type) {
            document.querySelectorAll('.tab').forEach((t, i) => t.classList.toggle('active', (type === 'account' && i === 0) || (type === 'pin' && i === 1)));
            document.getElementById('accountPanel').classList.toggle('active', type === 'account');
            document.getElementById('pinPanel').classList.toggle('active', type === 'pin');
            document.getElementById('errorMsg').style.display = 'none';
        }
        document.getElementById('loginForm').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('loginBtn'), err = document.getElementById('errorMsg');
            btn.disabled = true; btn.textContent = '登录中...'; err.style.display = 'none';
            try {
                const res = await fetch('/api/login', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ username: document.getElementById('username').value, password: document.getElementById('password').value }) });
                const data = await res.json();
                if(data.status === 'ok') { window.location.href = "/dashboard"; }
                else { err.textContent = data.msg; err.style.display = 'block'; btn.disabled = false; btn.textContent = '登 录'; }
            } catch(e) { err.textContent = '网络错误'; err.style.display = 'block'; btn.disabled = false; btn.textContent = '登 录'; }
        }
        document.getElementById('pinForm').onsubmit = async (e) => {
            e.preventDefault();
            const btn = document.getElementById('pinBtn'), err = document.getElementById('errorMsg');
            btn.disabled = true; btn.textContent = '登录中...'; err.style.display = 'none';
            try {
                const res = await fetch('/api/pin-login', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ pin: document.getElementById('pinCode').value }) });
                const data = await res.json();
                if(data.status === 'ok') { window.location.href = "/dashboard"; }
                else { err.textContent = data.msg; err.style.display = 'block'; btn.disabled = false; btn.textContent = '密钥登录'; }
            } catch(e) { err.textContent = '网络错误'; err.style.display = 'block'; btn.disabled = false; btn.textContent = '密钥登录'; }
        }
    </script>
</body>
</html>
'''
