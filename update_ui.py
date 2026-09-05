import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_css = '''    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f4f7f6;
            color: #333333;
            min-height: 100vh;
            display: flex;
        }
        .sidebar {
            width: 250px;
            background: #ffffff;
            border-right: 1px solid #e0e5e9;
            padding: 30px 20px;
            display: flex;
            flex-direction: column;
            box-shadow: 2px 0 10px rgba(0,0,0,0.02);
            height: 100vh;
            position: sticky;
            top: 0;
        }
        .sidebar h1 {
            font-size: 1.8rem;
            color: #2c3e50;
            margin-bottom: 5px;
            text-align: center;
        }
        .sidebar p {
            color: #6c7a89;
            font-size: 0.9rem;
            text-align: center;
            margin-bottom: 40px;
        }
        .main-content {
            flex: 1;
            padding: 40px;
            max-width: 1000px;
        }
        .tabs {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .tab-btn {
            padding: 14px 20px;
            background: #ffffff;
            border: 1px solid transparent;
            border-radius: 10px;
            color: #6c7a89;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
            text-align: left;
        }
        .tab-btn:hover {
            background: #f0f4f8;
            color: #3498db;
        }
        .tab-btn.active {
            background: #3498db;
            color: #ffffff;
            box-shadow: 0 4px 15px rgba(52,152,219,0.3);
        }
        .tab-content {
            display: none;
            background: #ffffff;
            border-radius: 16px;
            padding: 40px;
            border: 1px solid #e0e5e9;
            box-shadow: 0 5px 20px rgba(0,0,0,0.03);
            animation: fadeIn 0.3s;
        }
        .tab-content.active {
            display: block;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: 600;
        }
        input[type="file"], textarea, select {
            width: 100%;
            padding: 12px;
            background: #f9fbfd;
            border: 1px solid #dce1e5;
            border-radius: 10px;
            color: #333333;
            font-size: 14px;
            transition: all 0.3s;
        }
        input[type="file"]:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52,152,219,0.1);
            background: #ffffff;
        }
        textarea {
            min-height: 100px;
            resize: vertical;
            font-family: 'Courier New', monospace;
        }
        .btn-submit {
            width: 100%;
            padding: 14px;
            background: #3498db;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(52,152,219,0.2);
        }
        .btn-submit:hover {
            background: #2980b9;
            box-shadow: 0 6px 20px rgba(41,128,185,0.3);
            transform: translateY(-1px);
        }
        .btn-submit:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .result-box {
            margin-top: 20px;
            padding: 20px;
            background: #f8fafc;
            border-radius: 12px;
            border-left: 4px solid #3498db;
            display: none;
            word-wrap: break-word;
            font-weight: 500;
            color: #2c3e50;
        }
        .result-box.show {
            display: block;
        }
        .result-box.success {
            border-left-color: #2ecc71;
            background: #f0fdf4;
        }
        .result-box.error {
            border-left-color: #e74c3c;
            background: #fef2f2;
        }
        .download-link {
            display: inline-block;
            margin-top: 10px;
            padding: 10px 20px;
            background: #2ecc71;
            color: #ffffff;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: background 0.3s;
            border: none;
            cursor: pointer;
        }
        .download-link:hover {
            background: #27ae60;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            background: #e8f4fd;
            color: #3498db;
            border-radius: 20px;
            font-size: 12px;
            margin-left: 10px;
            font-weight: 600;
        }
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            border-bottom: 1px solid #e0e5e9;
            padding-bottom: 10px;
        }
        h3 {
            color: #34495e;
            margin-bottom: 15px;
        }
        @media (max-width: 768px) {
            body {
                flex-direction: column;
            }
            .sidebar {
                width: 100%;
                height: auto;
                position: relative;
                padding: 20px;
                border-right: none;
                border-bottom: 1px solid #e0e5e9;
            }
            .sidebar p { margin-bottom: 20px; }
            .tabs {
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: center;
            }
            .grid-2 {
                grid-template-columns: 1fr;
            }
            .main-content {
                padding: 20px;
            }
        }
        .icon {
            margin-right: 12px;
            width: 20px;
            text-align: center;
        }
    </style>'''

content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)

html_structure = '''<body>
    <div class="sidebar">
        <h1>🔐 StegoSuite</h1>
        <p>Hide secrets in media</p>
        <div class="tabs">
            <button class="tab-btn active" data-tab="image"><i class="fas fa-image icon"></i>Image</button>
            <button class="tab-btn" data-tab="audio"><i class="fas fa-music icon"></i>Audio</button>
            <button class="tab-btn" data-tab="video"><i class="fas fa-video icon"></i>Video</button>
            <button class="tab-btn" data-tab="text"><i class="fas fa-font icon"></i>Text</button>
        </div>
    </div>
    
    <div class="main-content">
'''

idx_start_tabs = content.find('<!-- ==================== IMAGE TAB ==================== -->')
idx_end_tabs = content.find('<script>')
tabs_content = content[idx_start_tabs:idx_end_tabs]

idx_end_scripts = content.find('</body>')
scripts = content[idx_end_tabs:idx_end_scripts]

head_end = content.find('</head>')
new_full_content = content[:head_end+7] + "\n" + html_structure + tabs_content + "    </div>\n\n    " + scripts + "</body>\n</html>"

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(new_full_content)

print('Updated index.html to sidebar layout successfully.')
