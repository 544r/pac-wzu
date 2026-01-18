"""
管理后台页面模板
"""

ADMIN_HTML = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理后台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #f5f7fa; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { margin-bottom: 20px; }
        .card { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .card h2 { font-size: 16px; margin-bottom: 16px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }
        .status-item { background: #f8f9fa; padding: 16px; border-radius: 8px; text-align: center; }
        .status-value { font-size: 18px; font-weight: 700; color: #667eea; }
        .status-label { font-size: 12px; color: #666; margin-top: 4px; }
        .status-ok { color: #10b981; }
        .status-err { color: #ef4444; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; }
        .log-success { color: #10b981; }
        .log-error { color: #ef4444; }
        .log-warning { color: #f59e0b; }
        .log-info { color: #3b82f6; }
        .btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; margin-right: 8px; text-decoration: none; display: inline-block; }
        .btn-primary { background: #667eea; color: #fff; }
        .btn-success { background: #10b981; color: #fff; }
        .btn-secondary { background: #eee; color: #333; }
        .actions { margin-bottom: 20px; }
        .login-box { max-width: 300px; margin: 100px auto; background: #fff; padding: 30px; border-radius: 12px; }
        .login-box h2 { text-align: center; margin-bottom: 20px; }
        .login-box input { width: 100%; padding: 12px; margin-bottom: 12px; border: 2px solid #e0e0e0; border-radius: 8px; }
        .login-box button { width: 100%; padding: 12px; background: #667eea; color: #fff; border: none; border-radius: 8px; cursor: pointer; }
        .login-box .err { color: red; text-align: center; margin-top: 10px; display: none; }
    </style>
</head>
<body>
    <div class="container" id="panel" style="display:none;">
        <h1>📊 管理后台</h1>
        <div class="actions">
            <button class="btn btn-primary" onclick="loadAll()">🔄 刷新</button>
            <button class="btn btn-success" onclick="runNow()">▶️ 立即检查</button>
            <a href="/" class="btn btn-secondary">← 首页</a>
        </div>
        <div class="card"><h2>⚙️ 系统状态</h2><div class="status-grid" id="statusGrid"></div></div>
        <div class="card"><h2>👥 订阅用户 (<span id="subCount">0</span>)</h2><div style="overflow-x:auto;"><table><thead><tr><th>用户</th><th>邮箱</th><th>间隔</th><th>时段</th><th>通知</th><th>状态</th><th>最后成功</th></tr></thead><tbody id="subTable"></tbody></table></div></div>
        <div class="card"><h2>🔑 密钥用户 (<span id="pinCount">0</span>)</h2><div style="overflow-x:auto;"><table><thead><tr><th>用户</th><th>创建时间</th></tr></thead><tbody id="pinTable"></tbody></table></div></div>
        <div class="card"><h2>📜 日志</h2><div style="overflow-x:auto;max-height:400px;overflow-y:auto;"><table><thead><tr><th>时间</th><th>级别</th><th>用户</th><th>消息</th></tr></thead><tbody id="logTable"></tbody></table></div></div>
    </div>
    <div class="login-box" id="loginBox">
        <h2>🔐 管理员</h2>
        <input type="password" id="pwd" placeholder="密码" onkeypress="if(event.keyCode==13)login()">
        <button onclick="login()">登录</button>
        <p class="err" id="err"></p>
    </div>
    <script>
        async function login() {
            const res = await fetch('/api/admin/login', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ password: document.getElementById('pwd').value }) });
            const d = await res.json();
            if (d.status === 'ok') { document.getElementById('loginBox').style.display = 'none'; document.getElementById('panel').style.display = 'block'; loadAll(); }
            else { document.getElementById('err').textContent = d.msg; document.getElementById('err').style.display = 'block'; }
        }
        async function loadAll() {
            const s = await (await fetch('/api/admin/status')).json();
            document.getElementById('statusGrid').innerHTML = `
                <div class="status-item"><div class="status-value ${s.scheduler_running?'status-ok':'status-err'}">${s.scheduler_running?'✅':'❌'}</div><div class="status-label">调度器</div></div>
                <div class="status-item"><div class="status-value">${s.total_checks}</div><div class="status-label">检查次数</div></div>
                <div class="status-item"><div class="status-value">${s.emails_sent}</div><div class="status-label">邮件数</div></div>
                <div class="status-item"><div class="status-value">${s.wechat_sent||0}</div><div class="status-label">微信数</div></div>
                <div class="status-item"><div class="status-value">${s.subscriber_count}</div><div class="status-label">订阅数</div></div>
                <div class="status-item"><div class="status-value">${s.pin_count}</div><div class="status-label">密钥数</div></div>
                <div class="status-item"><div class="status-value ${s.resend_configured?'status-ok':'status-err'}">${s.resend_configured?'✅':'❌'}</div><div class="status-label">邮件API</div></div>
                <div class="status-item"><div class="status-value ${s.wechat_configured?'status-ok':'status-err'}">${s.wechat_configured?'✅':'❌'}</div><div class="status-label">微信推送</div></div>
                <div class="status-item"><div class="status-value ${s.persistent_storage?'status-ok':'status-err'}">${s.persistent_storage?'✅':'⚠️'}</div><div class="status-label">存储</div></div>
                <div class="status-item"><div class="status-value" style="font-size:11px;">${s.last_check_time||'未执行'}</div><div class="status-label">最后检查</div></div>
            `;
            const subs = await (await fetch('/api/admin/subscribers')).json();
            document.getElementById('subCount').textContent = subs.length;
            document.getElementById('subTable').innerHTML = subs.length ? subs.map(x=>{
                let notify = [];
                if (x.notify_email !== false) notify.push('📧');
                if (x.notify_wechat) notify.push('💬');
                return `<tr><td>${x.username}</td><td>${x.email}</td><td>${x.interval}分钟</td><td>${x.start_hour}-${x.end_hour}</td><td>${notify.join(' ')}</td><td class="${x.status==='active'?'status-ok':'status-err'}">${x.status}</td><td>${x.last_success||'-'}</td></tr>`;
            }).join('') : '<tr><td colspan="7" style="text-align:center;color:#999;">无</td></tr>';
            const pins = await (await fetch('/api/admin/pins')).json();
            document.getElementById('pinCount').textContent = pins.length;
            document.getElementById('pinTable').innerHTML = pins.length ? pins.map(x=>`<tr><td>${x.username}</td><td>${x.created}</td></tr>`).join('') : '<tr><td colspan="2" style="text-align:center;color:#999;">无</td></tr>';
            const logs = await (await fetch('/api/admin/logs')).json();
            document.getElementById('logTable').innerHTML = logs.length ? logs.slice(-50).reverse().map(l=>`<tr><td>${l.time}</td><td class="log-${l.level}">${l.level}</td><td>${l.user||'-'}</td><td>${l.message}</td></tr>`).join('') : '<tr><td colspan="4" style="text-align:center;color:#999;">无</td></tr>';
        }
        async function runNow() { await fetch('/api/admin/run-now', { method: 'POST' }); alert('已触发'); setTimeout(loadAll, 3000); }
    </script>
</body>
</html>
'''
