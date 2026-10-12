import json
import re
import os

input_path = '/home/zia/.gemini/antigravity-ide/brain/b64519ea-ca5d-49bd-90ef-2472ccc65f19/.system_generated/logs/transcript_full.jsonl'
output_md = 'docs/nuada_proje_sohbet_gecmisi.md'
output_html = 'docs/nuada_proje_sohbet_gecmisi.html'

def clean_user_text(raw_text):
    # Extract content between <USER_REQUEST> and </USER_REQUEST>
    match = re.search(r'<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>', raw_text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    else:
        # Fallback: remove additional metadata
        text = re.sub(r'<ADDITIONAL_METADATA>.*', '', raw_text, flags=re.DOTALL).strip()
    return text

turns = []
seen_user = set()

with open(input_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            item = json.loads(line)
            stype = item.get('type')
            source = item.get('source')
            content = item.get('content', '')
            
            if stype == 'USER_INPUT' and source == 'USER_EXPLICIT':
                cleaned = clean_user_text(content)
                if cleaned and len(cleaned) > 2:
                    turns.append(('USER', cleaned))
            elif stype == 'PLANNER_RESPONSE' and content:
                # avoid empty or pure tool notifications
                if not content.startswith('[Notice]') and len(content.strip()) > 10:
                    turns.append(('ASSISTANT', content.strip()))
        except Exception:
            pass

# Deduplicate immediate identical user turns
filtered_turns = []
for role, text in turns:
    if filtered_turns and filtered_turns[-1][0] == role and filtered_turns[-1][1] == text:
        continue
    filtered_turns.append((role, text))

# 1. Write Markdown
with open(output_md, 'w', encoding='utf-8') as f:
    f.write('# Nuada Bionic Hand - Antigravity Proje Sohbet Geçmişi\n\n')
    f.write('> Bu belge, Nuada Bionic Hand projesinin donanım seçimi, sEMG tasarımı, AD8232 modifikasyonu ve bitirme tezi planlama sürecindeki tüm teknik tartışma ve kararların derlenmiş sohbet geçmişidir.\n\n---\n\n')
    
    turn_num = 1
    for role, text in filtered_turns:
        if role == 'USER':
            f.write(f'### 👤 Nuri Ziya (Soru #{turn_num})\n\n')
            f.write(f'{text}\n\n')
            turn_num += 1
        else:
            f.write(f'### 🤖 Antigravity Asistan (Yanıt)\n\n')
            f.write(f'{text}\n\n---\n\n')

# 2. Write Beautiful Standalone HTML
import html

html_content = '''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nuada Bionic Hand - Proje Sohbet Geçmişi</title>
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #0f141c;
    color: #e6edf3;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
  }
  .container {
    max-width: 900px;
    margin: 0 auto;
  }
  header {
    background: linear-gradient(135deg, #1f2937, #111827);
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 25px;
    border: 1px solid #374151;
  }
  h1 { margin-top: 0; color: #60a5fa; font-size: 24px; }
  .desc { color: #9ca3af; font-size: 14px; margin-bottom: 0; }
  .message {
    margin-bottom: 20px;
    padding: 18px 22px;
    border-radius: 12px;
    position: relative;
  }
  .user {
    background-color: #1e293b;
    border-left: 5px solid #3b82f6;
    margin-left: 30px;
  }
  .assistant {
    background-color: #18202f;
    border-left: 5px solid #10b981;
    margin-right: 30px;
  }
  .sender {
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
  }
  .user .sender { color: #60a5fa; }
  .assistant .sender { color: #34d399; }
  pre {
    background-color: #0b0f17;
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    border: 1px solid #1f2937;
    font-size: 13px;
  }
  code {
    background-color: rgba(255,255,255,0.1);
    padding: 2px 5px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 13px;
  }
  pre code { background: none; padding: 0; }
  blockquote {
    border-left: 4px solid #f59e0b;
    margin: 10px 0;
    padding: 8px 15px;
    background: rgba(245, 158, 11, 0.1);
    color: #fbbf24;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 15px 0;
  }
  th, td {
    border: 1px solid #374151;
    padding: 8px 12px;
    text-align: left;
  }
  th { background-color: #1f2937; color: #93c5fd; }
  a { color: #38bdf8; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Nuada Bionic Hand: Proje Sohbet ve Karar Geçmişi</h1>
    <p class="desc">Nuri Ziya Kırtepe & Evrim Doğa Solmaz | Antigravity AI Çift Programlama Oturumu</p>
  </header>
'''

import markdown

for role, text in filtered_turns:
    # Convert markdown to HTML
    body_html = markdown.markdown(text, extensions=['fenced_code', 'tables'])
    if role == 'USER':
        html_content += f'''
  <div class="message user">
    <div class="sender">👤 Nuri Ziya</div>
    <div class="content">{body_html}</div>
  </div>
'''
    else:
        html_content += f'''
  <div class="message assistant">
    <div class="sender">🤖 Antigravity Asistan</div>
    <div class="content">{body_html}</div>
  </div>
'''

html_content += '''
</div>
</body>
</html>
'''

with open(output_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Exported clean chat to:\n  - {output_md}\n  - {output_html}")
