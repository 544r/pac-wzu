"""
仪表盘页面模板
"""

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的成绩单</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #f5f7fa; }
        .navbar { background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
        .navbar-brand { color: #fff; font-size: 18px; font-weight: 600; }
        .btn-logout { background: rgba(255,255,255,0.2); color: #fff; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; text-decoration: none; font-size: 14px; }
        .main { padding: 20px; max-width: 1200px; margin: 0 auto; }
        
        .pin-card { background: linear-gradient(135deg, #f093fb, #f5576c); border-radius: 16px; padding: 20px; margin-bottom: 20px; color: #fff; }
        .pin-card h3 { margin-bottom: 12px; font-size: 16px; }
        .pin-form { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }
        .pin-form .field { flex: 1; min-width: 150px; }
        .pin-form label { display: block; font-size: 12px; margin-bottom: 6px; opacity: 0.9; }
        .pin-form input { width: 100%; padding: 10px; border-radius: 8px; border: none; font-size: 14px; }
        .pin-form button { padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; }
        .btn-pin { background: #fff; color: #f5576c; }
        .btn-del-pin { background: rgba(255,255,255,0.2); color: #fff; }
        .pin-status { margin-top: 12px; font-size: 13px; padding: 8px 12px; background: rgba(255,255,255,0.15); border-radius: 8px; }
        
        .sub-card { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 16px; padding: 24px; margin-bottom: 20px; color: #fff; }
        .sub-card h3 { margin-bottom: 16px; font-size: 16px; }
        .sub-form { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }
        .sub-form .field { flex: 1; min-width: 120px; }
        .sub-form label { display: block; font-size: 12px; margin-bottom: 6px; opacity: 0.9; }
        .sub-form input, .sub-form select { width: 100%; padding: 10px; border-radius: 8px; border: none; font-size: 14px; }
        .sub-form button { padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; }
        .btn-sub { background: #fff; color: #667eea; }
        .btn-unsub { background: rgba(255,255,255,0.2); color: #fff; border: 1px solid rgba(255,255,255,0.4) !important; }
        .btn-test { background: #10b981; color: #fff; }
        .sub-status { margin-top: 12px; font-size: 13px; padding: 8px 12px; background: rgba(255,255,255,0.15); border-radius: 8px; }
        
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
        @media (max-width: 768px) { .stats { grid-template-columns: repeat(2, 1fr); } }
        .stat-card { background: #fff; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .stat-icon { font-size: 28px; margin-bottom: 8px; }
        .stat-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
        .stat-label { font-size: 13px; color: #666; margin-top: 4px; }
        
        .panel { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .panel-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }
        .panel-row .field { flex: 1; min-width: 140px; }
        .panel-row label { display: block; font-size: 13px; color: #666; margin-bottom: 6px; }
        .panel-row select { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; }
        .btn-query { padding: 12px 24px; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
        .btn-export { padding: 12px 24px; background: #10b981; color: #fff; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
        
        .table-card { background: #fff; border-radius: 12px; overflow: hidden; }
        .table-header { padding: 16px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .table-header h2 { font-size: 16px; }
        .badge { background: #667eea; color: #fff; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 14px 16px; text-align: left; border-bottom: 1px solid #f0f0f0; font-size: 14px; }
        th { background: #f8f9fa; font-weight: 600; color: #666; }
        .course-name { font-weight: 600; }
        .score-good { color: #059669; font-weight: 600; }
        .score-bad { color: #dc2626; font-weight: 600; }
        .loading, .empty { padding: 60px 20px; text-align: center; color: #666; }
        .spinner { width: 40px; height: 40px; border: 4px solid #e0e0e0; border-top-color: #667eea; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <nav class="navbar">
        <span class="navbar-brand">🎓 温大成绩助手</span>
        <a href="/logout" class="btn-logout">退出登录</a>
    </nav>
    <main class="main">
        <div class="pin-card">
            <h3>🔑 快捷密钥设置</h3>
            <div class="pin-form">
                <div class="field">
                    <label>设置密钥（4-16位）</label>
                    <input type="text" id="newPin" placeholder="例如: mykey123">
                </div>
                <button class="btn-pin" onclick="setPin()">保存密钥</button>
                <button class="btn-del-pin" onclick="deletePin()">删除密钥</button>
            </div>
            <div class="pin-status" id="pinStatus">💡 设置后可用密钥代替学号密码登录（密钥=你的账号密码）</div>
        </div>
        
        <div class="sub-card">
            <h3>📧 成绩推送设置</h3>
            <div class="sub-form">
                <div class="field"><label>接收邮箱</label><input type="email" id="subEmail" placeholder="your@email.com"></div>
                <div class="field"><label>查询间隔</label><select id="subInterval"><option value="15">每15分钟</option><option value="30" selected>每30分钟</option><option value="60">每1小时</option></select></div>
                <div class="field"><label>开始时间</label><select id="subStart"><option value="6">06:00</option><option value="7">07:00</option><option value="8" selected>08:00</option><option value="9">09:00</option></select></div>
                <div class="field"><label>结束时间</label><select id="subEnd"><option value="20">20:00</option><option value="21">21:00</option><option value="22" selected>22:00</option><option value="23">23:00</option><option value="24">24:00</option></select></div>
            </div>
            <div class="sub-form" style="margin-top: 12px;">
                <div class="field" style="flex: 2;"><label>Server酱 Key <a href="https://sct.ftqq.com/" target="_blank" style="color:#ffd700;font-size:11px;">(获取)</a></label><input type="text" id="wechatKey" placeholder="开启微信推送需填写"></div>
            </div>
            <div class="sub-form" style="margin-top: 12px;">
                <div class="field" style="display: flex; gap: 20px; align-items: center;">
                    <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;"><input type="checkbox" id="notifyEmail" checked style="width: 18px; height: 18px;"> 邮件通知</label>
                    <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;"><input type="checkbox" id="notifyWechat" style="width: 18px; height: 18px;"> 微信推送</label>
                </div>
                <button class="btn-sub" onclick="subscribe()">开启推送</button>
                <button class="btn-test" onclick="testEmail()">测试邮件</button>
                <button class="btn-test" onclick="testWechat()" style="background: #07c160;">测试微信</button>
                <button class="btn-unsub" onclick="unsubscribe()">取消</button>
            </div>
            <div class="sub-status" id="subStatus">💡 开启后，有新成绩会自动发邮件/微信通知</div>
        </div>
        
        <div class="gpa-card" style="background: linear-gradient(135deg, #11998e, #38ef7d); border-radius: 16px; padding: 24px; margin-bottom: 20px; color: #fff;">
            <h3 style="margin-bottom: 16px;">🎯 GPA 计算器</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 16px;">
                <div style="background: rgba(255,255,255,0.15); border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 32px; font-weight: 700;" id="currentGpa">-</div>
                    <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">当前绩点</div>
                    <div style="font-size: 12px; opacity: 0.7; margin-top: 2px;" id="gpaLevel">-</div>
                </div>
                <div style="background: rgba(255,255,255,0.15); border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 32px; font-weight: 700;" id="totalCredits">-</div>
                    <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">已修学分</div>
                </div>
                <div style="background: rgba(255,255,255,0.15); border-radius: 12px; padding: 16px; text-align: center;">
                    <div style="font-size: 32px; font-weight: 700;" id="totalPoints">-</div>
                    <div style="font-size: 13px; opacity: 0.9; margin-top: 4px;">总绩点</div>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 16px;">
                <div style="font-size: 14px; margin-bottom: 12px; font-weight: 500;">📊 目标绩点计算</div>
                <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end;">
                    <div style="flex: 1; min-width: 100px;">
                        <label style="display: block; font-size: 12px; margin-bottom: 6px; opacity: 0.9;">目标绩点</label>
                        <input type="number" id="targetGpa" placeholder="3.5" step="0.1" min="0" max="5" style="width: 100%; padding: 10px; border-radius: 8px; border: none; font-size: 14px;">
                    </div>
                    <div style="flex: 1; min-width: 100px;">
                        <label style="display: block; font-size: 12px; margin-bottom: 6px; opacity: 0.9;">剩余学分</label>
                        <input type="number" id="remainingCredits" placeholder="30" min="1" style="width: 100%; padding: 10px; border-radius: 8px; border: none; font-size: 14px;">
                    </div>
                    <button onclick="calcTargetGpa()" style="padding: 10px 20px; border-radius: 8px; border: none; background: #fff; color: #11998e; font-weight: 600; cursor: pointer;">计算</button>
                </div>
                <div id="targetResult" style="margin-top: 12px; font-size: 13px; padding: 8px 12px; background: rgba(255,255,255,0.15); border-radius: 8px; display: none;"></div>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card"><div class="stat-icon">📚</div><div class="stat-value" id="s1">-</div><div class="stat-label">课程数</div></div>
            <div class="stat-card"><div class="stat-icon">📝</div><div class="stat-value" id="s2">-</div><div class="stat-label">总学分</div></div>
            <div class="stat-card"><div class="stat-icon">📈</div><div class="stat-value" id="s3">-</div><div class="stat-label">平均绩点</div></div>
            <div class="stat-card"><div class="stat-icon">✅</div><div class="stat-value" id="s4">-</div><div class="stat-label">及格率</div></div>
        </div>
        
        <div class="panel">
            <div class="panel-row">
                <div class="field"><label>学年</label><select id="xnm"><option value="">全部学年</option><option value="2025">2025-2026</option><option value="2024">2024-2025</option><option value="2023">2023-2024</option><option value="2022">2022-2023</option><option value="2021">2021-2022</option><option value="2020">2020-2021</option></select></div>
                <div class="field"><label>学期</label><select id="xqm"><option value="">全部学期</option><option value="3">第一学期</option><option value="12">第二学期</option></select></div>
                <button class="btn-query" onclick="loadGrades()">🔍 查询</button>
                <button class="btn-export" onclick="exportExcel()">📥 导出</button>
            </div>
        </div>
        
        <div class="table-card">
            <div class="table-header"><h2>📋 成绩明细</h2><span class="badge" id="countBadge">0门</span></div>
            <div id="loading" class="loading"><div class="spinner"></div><p>加载中...</p></div>
            <div id="empty" class="empty" style="display:none;">暂无数据</div>
            <div id="tableWrap" style="display:none;overflow-x:auto;">
                <table><thead><tr><th>学年</th><th>学期</th><th>课程</th><th>学分</th><th>绩点</th><th>成绩</th><th>性质</th></tr></thead><tbody id="tbody"></tbody></table>
            </div>
        </div>
    </main>
    <script>
        let data = [];
        
        async function loadPinStatus() {
            try {
                const res = await fetch('/api/pin/status');
                const d = await res.json();
                if (d.has_pin) {
                    document.getElementById('pinStatus').innerHTML = '✅ 已设置密钥，可用密钥登录（修改教务密码后需重新设置）';
                }
            } catch(e) {}
        }
        
        async function setPin() {
            const pin = document.getElementById('newPin').value.trim();
            if (pin.length < 4 || pin.length > 16) { alert('密钥长度需要4-16位'); return; }
            try {
                const res = await fetch('/api/pin/set', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ pin }) });
                const d = await res.json();
                if (d.status === 'ok') {
                    document.getElementById('pinStatus').innerHTML = '✅ 密钥设置成功！';
                    document.getElementById('newPin').value = '';
                    alert('密钥设置成功！下次可直接用密钥登录');
                } else { alert(d.msg); }
            } catch(e) { alert('网络错误'); }
        }
        
        async function deletePin() {
            if (!confirm('确定删除密钥？')) return;
            try {
                await fetch('/api/pin/delete', { method: 'POST' });
                document.getElementById('pinStatus').innerHTML = '💡 密钥已删除';
                alert('密钥已删除');
            } catch(e) { alert('网络错误'); }
        }
        
        async function loadSubStatus() {
            try {
                const res = await fetch('/api/subscribe/status');
                const d = await res.json();
                if (d.subscribed) {
                    document.getElementById('subEmail').value = d.email || '';
                    document.getElementById('subInterval').value = d.interval || 30;
                    document.getElementById('subStart').value = d.start_hour || 8;
                    document.getElementById('subEnd').value = d.end_hour || 22;
                    document.getElementById('notifyEmail').checked = d.notify_email !== false;
                    document.getElementById('notifyWechat').checked = d.notify_wechat === true;
                    if (d.wechat_key_masked) {
                        document.getElementById('wechatKey').placeholder = '已保存: ' + d.wechat_key_masked;
                    }
                    let st = d.status === 'active' ? '运行中' : (d.status === 'login_failed' ? '登录失败' : d.status);
                    let methods = [];
                    if (d.notify_email !== false) methods.push('邮件');
                    if (d.notify_wechat) methods.push('微信');
                    document.getElementById('subStatus').innerHTML = '✅ 推送已开启 | ' + d.email + ' | ' + methods.join('+') + ' | ' + st;
                }
            } catch(e) {}
        }
        
        async function subscribe() {
            const email = document.getElementById('subEmail').value.trim();
            const notifyEmail = document.getElementById('notifyEmail').checked;
            const notifyWechat = document.getElementById('notifyWechat').checked;
            const wechatKey = document.getElementById('wechatKey').value.trim();
            if (!notifyEmail && !notifyWechat) { alert('请至少选择一种通知方式'); return; }
            if (notifyEmail && !email.includes('@')) { alert('请输入有效邮箱'); return; }
            if (notifyWechat && !wechatKey) { alert('请填写你的 Server酱 SendKey'); return; }
            try {
                const res = await fetch('/api/subscribe', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ email, interval: +document.getElementById('subInterval').value, start_hour: +document.getElementById('subStart').value, end_hour: +document.getElementById('subEnd').value, notify_email: notifyEmail, notify_wechat: notifyWechat, wechat_key: wechatKey }) });
                const d = await res.json();
                if (d.status === 'ok') { document.getElementById('subStatus').innerHTML = '✅ 订阅成功！'; document.getElementById('wechatKey').value = ''; alert('订阅成功！'); loadSubStatus(); } else { alert(d.msg); }
            } catch(e) { alert('网络错误'); }
        }
        
        async function testEmail() {
            const email = document.getElementById('subEmail').value.trim();
            if (!email.includes('@')) { alert('请先输入邮箱'); return; }
            try {
                const res = await fetch('/api/test-email', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ email }) });
                alert((await res.json()).msg);
            } catch(e) { alert('发送失败'); }
        }
        
        async function testWechat() {
            const wechatKey = document.getElementById('wechatKey').value.trim();
            if (!wechatKey) { alert('请先填写你的 Server酱 SendKey'); return; }
            try {
                const res = await fetch('/api/test-wechat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ wechat_key: wechatKey }) });
                const d = await res.json();
                alert(d.msg);
            } catch(e) { alert('发送失败'); }
        }
        
        async function unsubscribe() {
            if (!confirm('确定取消推送？')) return;
            await fetch('/api/unsubscribe', { method: 'POST' });
            document.getElementById('subStatus').innerHTML = '💡 推送已关闭';
            alert('已取消');
        }
        
        async function loadGrades() {
            const loading = document.getElementById('loading'), empty = document.getElementById('empty'), wrap = document.getElementById('tableWrap');
            loading.style.display = 'block'; empty.style.display = 'none'; wrap.style.display = 'none';
            try {
                const res = await fetch('/api/grades', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ xnm: document.getElementById('xnm').value, xqm: document.getElementById('xqm').value }) });
                loading.style.display = 'none';
                if (res.status === 401) { alert('登录过期'); location.href = '/'; return; }
                const d = await res.json();
                if (d.status === 'ok') { data = d.data || []; if (data.length) { wrap.style.display = 'block'; render(data); stats(data); document.getElementById('countBadge').textContent = data.length + '门'; } else { empty.style.display = 'block'; } }
                else { alert(d.msg); }
            } catch(e) { loading.style.display = 'none'; alert('网络错误'); }
        }
        
        function render(items) {
            let html = '';
            items.forEach(i => { const s = i.cj || '-'; let c = ''; const n = parseFloat(s); if (!isNaN(n)) c = n >= 60 ? 'score-good' : 'score-bad'; html += '<tr><td>'+(i.xnmmc||'-')+'</td><td>'+(i.xqmmc||'-')+'</td><td class="course-name">'+(i.kcmc||'-')+'</td><td>'+(i.xf||'-')+'</td><td>'+(i.jd||'-')+'</td><td class="'+c+'">'+s+'</td><td>'+(i.kcxzmc||'-')+'</td></tr>'; });
            document.getElementById('tbody').innerHTML = html;
        }
        
        function stats(items) {
            let cr = 0, w = 0, p = 0, v = 0;
            items.forEach(i => { const xf = parseFloat(i.xf)||0, jd = parseFloat(i.jd)||0, cj = parseFloat(i.cj); cr += xf; if (jd > 0 && xf > 0) w += jd * xf; if (!isNaN(cj)) { v++; if (cj >= 60) p++; } });
            document.getElementById('s1').textContent = items.length;
            document.getElementById('s2').textContent = cr.toFixed(1);
            const gpa = cr > 0 ? (w/cr) : 0;
            document.getElementById('s3').textContent = cr > 0 ? gpa.toFixed(2) : '-';
            document.getElementById('s4').textContent = v > 0 ? Math.round(p/v*100)+'%' : '-';
            
            // 更新 GPA 卡片
            document.getElementById('currentGpa').textContent = cr > 0 ? gpa.toFixed(2) : '-';
            document.getElementById('totalCredits').textContent = cr.toFixed(1);
            document.getElementById('totalPoints').textContent = w.toFixed(1);
            // 绩点等级判断
            let level = '-';
            if (gpa >= 4.5) level = '🏆 优秀';
            else if (gpa >= 4.0) level = '🥇 良好';
            else if (gpa >= 3.5) level = '🥈 中等偏上';
            else if (gpa >= 3.0) level = '🥉 中等';
            else if (gpa >= 2.0) level = '📘 及格';
            else if (cr > 0) level = '⚠️ 需要努力';
            document.getElementById('gpaLevel').textContent = level;
        }
        
        async function calcTargetGpa() {
            const targetGpa = parseFloat(document.getElementById('targetGpa').value);
            const remainingCredits = parseFloat(document.getElementById('remainingCredits').value);
            const resultDiv = document.getElementById('targetResult');
            
            if (isNaN(targetGpa) || targetGpa < 0 || targetGpa > 5) { alert('请输入有效的目标绩点（0-5）'); return; }
            if (isNaN(remainingCredits) || remainingCredits <= 0) { alert('请输入有效的剩余学分'); return; }
            
            try {
                const res = await fetch('/api/gpa/target', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ grades: data, target_gpa: targetGpa, remaining_credits: remainingCredits }) });
                const d = await res.json();
                resultDiv.style.display = 'block';
                if (d.status === 'ok') {
                    const r = d.data;
                    if (r.achievable) {
                        const avgScore = r.needed_avg_gpa <= 3.0 ? '约75分' : (r.needed_avg_gpa <= 4.0 ? '约85分' : '约90分以上');
                        resultDiv.innerHTML = '✅ 可以达成！剩余课程需要平均绩点 <b>' + r.needed_avg_gpa.toFixed(2) + '</b>（' + avgScore + '）';
                    } else {
                        const maxGpa = ((r.current_gpa * r.current_credits + 5.0 * remainingCredits) / (r.current_credits + remainingCredits)).toFixed(2);
                        resultDiv.innerHTML = '❌ 无法达成。即使剩余课程全部满绩（5.0），最高可达 <b>' + maxGpa + '</b>';
                    }
                } else {
                    resultDiv.innerHTML = '⚠️ ' + d.msg;
                }
            } catch(e) { alert('计算失败'); }
        }
        
        function exportExcel() {
            if (!data.length) { alert('没有数据'); return; }
            const rows = data.map(i => ({ 学年: i.xnmmc, 学期: i.xqmmc, 课程: i.kcmc, 学分: i.xf, 绩点: i.jd, 成绩: i.cj, 性质: i.kcxzmc }));
            const ws = XLSX.utils.json_to_sheet(rows), wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "成绩");
            XLSX.writeFile(wb, "成绩单.xlsx");
        }
        
        window.onload = () => { loadGrades(); loadSubStatus(); loadPinStatus(); };
    </script>
</body>
</html>
'''
