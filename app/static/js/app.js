function byId(id){return document.getElementById(id);} 
function el(tag, cls){ const e=document.createElement(tag); if(cls) e.className=cls; return e; }

// App config (endpoints)
if(!window.APP_CONFIG){
  window.APP_CONFIG = {
    endpoints: { query: "/api/v1/query", upload: "/api/v1/upload" }
  };
}

// Footer year
document.addEventListener('DOMContentLoaded', ()=>{ const y=byId('year'); if(y) y.textContent = new Date().getFullYear(); });

// Chat logic
function escapeHtml(str){
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderMarkdown(md){
  if(!md) return '';
  const lines = md.split(/\r?\n/);
  let html = '';
  let inCode = false;
  let listOpen = false;
  for(let i=0;i<lines.length;i++){
    let line = lines[i];
    if(/^```/.test(line)){
      if(!inCode){ html += '<pre><code>'; inCode = true; }
      else { html += '</code></pre>'; inCode = false; }
      continue;
    }
    if(inCode){ html += escapeHtml(line) + '\n'; continue; }
    // Lists
    if(/^\s*[-*]\s+/.test(line)){
      if(!listOpen){ html += '<ul>'; listOpen = true; }
      const item = line.replace(/^\s*[-*]\s+/, '');
      html += '<li>' + inlineMd(escapeHtml(item)) + '</li>';
      // Lookahead: if next line is not list, close
      const next = lines[i+1] || '';
      if(!/^\s*[-*]\s+/.test(next)){ html += '</ul>'; listOpen = false; }
      continue;
    } else if(listOpen){ html += '</ul>'; listOpen = false; }
    // Headings
    const h = line.match(/^(#{1,6})\s+(.*)$/);
    if(h){
      const level = h[1].length;
      html += `<h${level}>${inlineMd(escapeHtml(h[2]))}</h${level}>`;
      continue;
    }
    // Paragraph or blank (skip extra spacing on empty lines)
    if(line.trim() === '') { continue; }
    html += '<p>' + inlineMd(escapeHtml(line)) + '</p>';
  }
  if(listOpen) html += '</ul>';
  if(inCode) html += '</code></pre>';
  return html;
}

function inlineMd(s){
  // Links [text](url)
  s = s.replace(/\[(.+?)\]\((https?:[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1<\/a>');
  // Bold **text**
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1<\/strong>');
  // Italic *text*
  s = s.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1<\/em>');
  // Inline code `code`
  s = s.replace(/`([^`]+)`/g, '<code>$1<\/code>');
  return s;
}

function appendMessage(container, role, text){
  const wrap = el('div', 'message ' + role);
  const r = el('div', 'role'); r.textContent = role;
  const t = el('div');
  if(role === 'assistant'){ t.innerHTML = renderMarkdown(String(text)); }
  else { t.textContent = text; }
  wrap.appendChild(r); wrap.appendChild(t);
  container.appendChild(wrap);
  container.scrollTop = container.scrollHeight;
  return t;
}

// Typing indicator: cycles '.', '..', '...'
function showTyping(container){
  const el = appendMessage(container, 'assistant', '');
  const frames = ['.', '..', '...'];
  let i = 0;
  el.textContent = frames[i];
  const id = setInterval(()=>{
    i = (i + 1) % frames.length;
    el.textContent = frames[i];
  }, 400);
  return { el, stop: ()=> clearInterval(id) };
}

// Simple persistence for chat history
const CHAT_HISTORY_KEY = 'rag_chat_history_v1';
function loadChatHistory(){
  try { return JSON.parse(localStorage.getItem(CHAT_HISTORY_KEY) || '[]'); } catch { return []; }
}
function saveChatHistory(history){
  try { localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(history)); } catch {}
}

async function sendQuery(text,onChunk){
  const res = await fetch(window.APP_CONFIG.endpoints.query + '?' + new URLSearchParams({
    stream_mode: true
  }).toString(), {
    method: 'POST', 
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: text })
  });
  // const data = await res.json();
  // // Flexible: handle either {answer} or {response}
  // return data.answer || data.response || JSON.stringify(data);
  
  if(!res.ok){
    const msg = await res.text().catch(()=> '');
    throw new Error(msg || `Request failed: ${res.status}`);
  }

  const ct = res.headers.get('content-type') || '';
  if(ct.includes('application/json')){
    const data = await res.json();
    onChunk((data.answer ?? data.response ?? ''));
    return;
  }

  if(!res.body || !res.body.getReader){
    const textResp = await res.text();
    onChunk(textResp);
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  while(true){
    const { value, done } = await reader.read();
    if(done) break;
    onChunk(decoder.decode(value, { stream: true }));
  }
}


function initChat(windowEl, formEl, inputEl){
  if(!windowEl || !formEl || !inputEl) return;
  // Clear chat history on page reload to start fresh
  // try { localStorage.removeItem(CHAT_HISTORY_KEY); } catch {}
  // windowEl.innerHTML = '';
  // Restore history
  const history = loadChatHistory();
  if(Array.isArray(history)){
    history.forEach(msg => {
      if(msg && msg.role && typeof msg.text === 'string'){
        appendMessage(windowEl, msg.role, msg.text);
      }
    });
  }
  // New chat handling
  const newBtn = byId('new-chat-btn');
  if(newBtn){
    newBtn.addEventListener('click', ()=>{
      localStorage.removeItem(CHAT_HISTORY_KEY);
      windowEl.innerHTML = '';
      inputEl.focus();
    });
  }
  formEl.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const text = inputEl.value.trim();
    if(!text) return;
    appendMessage(windowEl, 'user', text);
    const cur = loadChatHistory();
    cur.push({ role: 'user', text });
    saveChatHistory(cur);
    inputEl.value = '';
    let typing;
    try {
      typing = showTyping(windowEl);
      let buf = '';
      let firstChunk = true;
      await sendQuery(text, (chunk) => {
        if(firstChunk){ typing.stop(); firstChunk = false; typing.el.innerHTML = ''; }
        buf += chunk;
        typing.el.innerHTML = renderMarkdown(buf);
      });
      const cur2 = loadChatHistory();
      cur2.push({ role: 'assistant', text: buf });
      saveChatHistory(cur2);
    } catch (err) {
      const errMsg = 'Error: ' + (err?.message || err);
      try { if(typing && typeof typing.stop === 'function') typing.stop(); } catch {}
      const tEl = typing && typing.el ? typing.el : appendMessage(windowEl, 'assistant', '');
      tEl.textContent = errMsg;
      const cur3 = loadChatHistory();
      cur3.push({ role: 'assistant', text: errMsg });
      saveChatHistory(cur3);
    }
  });
}

// Uploader logic
const UPLOADS_KEY = 'rag_uploads_v1';
function loadUploads(){
  try { return JSON.parse(localStorage.getItem(UPLOADS_KEY) || '[]'); } catch { return []; }
}
function saveUploads(list){
  try { localStorage.setItem(UPLOADS_KEY, JSON.stringify(list)); } catch {}
}

function renderUploadItem(listEl, item){
  const card = el('div', 'upload-card');
  const name = el('div', 'upload-name'); name.textContent = item.name;
  const status = el('div', 'upload-status');
  status.textContent = item.run_id ? `Uploaded (run_id: ${item.run_id})` : 'Uploaded';
  card.appendChild(name); card.appendChild(status);
  listEl.prepend(card);
}

async function uploadFile(file){
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(window.APP_CONFIG.endpoints.upload, { method: 'POST', body: form });
  const data = await res.json();
  return data;
}

function initUploader({dropZone, input, browseBtn, list}){
  if(!dropZone || !input || !browseBtn || !list) return;

  function setDrag(over){ dropZone.classList.toggle('dragover', !!over); }

  // Restore previously uploaded items
  const persisted = loadUploads();
  if(Array.isArray(persisted) && persisted.length){
    // render oldest first so the newest ends up right-most before new uploads
    persisted.forEach(item => renderUploadItem(list, item));
  }

  ['dragenter','dragover'].forEach(ev=> dropZone.addEventListener(ev, (e)=>{ e.preventDefault(); e.stopPropagation(); setDrag(true); }));
  ;['dragleave','drop'].forEach(ev=> dropZone.addEventListener(ev, (e)=>{ e.preventDefault(); e.stopPropagation(); setDrag(false); }));

  dropZone.addEventListener('drop', (e)=>{
    const files = Array.from(e.dataTransfer.files || []);
    if(files.length) handleFiles(files);
  });

  browseBtn.addEventListener('click', ()=> input.click());
  input.addEventListener('change', ()=>{
    const files = Array.from(input.files || []);
    if(files.length) handleFiles(files);
    input.value = '';
  });

  async function handleFiles(files){
    for(const file of files){
      const card = el('div', 'upload-card');
      const name = el('div', 'upload-name'); name.textContent = file.name;
      const status = el('div', 'upload-status'); status.textContent = 'Uploading...';
      card.appendChild(name); card.appendChild(status);
      list.prepend(card);
      try{
        const resp = await uploadFile(file);
        const runId = resp.run_id || 'Error: ' + resp?.detail || 'n/a';
        status.textContent = `Uploaded (run_id: ${runId})`;
        // persist
        const items = loadUploads();
        items.push({ name: file.name, run_id: runId, ts: Date.now() });
        saveUploads(items);
        const empty = byId('uploads-empty');
        if(empty){ empty.style.display = 'none'; }
      }catch(err){
        status.textContent = 'Failed: ' + (err?.message || err);
      }
    }
  }
}

// Export to window for inline init calls in templates
window.initChat = initChat;
window.initUploader = initUploader;

// Auto-initialize per page when elements are present
document.addEventListener('DOMContentLoaded', ()=>{
  const cw = byId('chat-window');
  const cf = byId('chat-form');
  const ct = byId('chat-text');
  if(cw && cf && ct){ initChat(cw, cf, ct); }

  const dz = byId('drop-zone');
  const fi = byId('file-input');
  const bb = byId('browse-btn');
  const ur = byId('uploads-row');
  if(dz && fi && bb && ur){ initUploader({ dropZone: dz, input: fi, browseBtn: bb, list: ur });
    // toggle empty state
    const empty = byId('uploads-empty');
    const items = loadUploads();
    if(empty){ empty.style.display = items && items.length ? 'none' : 'block'; }
  }
});

