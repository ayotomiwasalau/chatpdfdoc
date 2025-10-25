// Auto-delete after being away this long (e.g., 30 minutes)
const AWAY_DELETE_AFTER_MS = 45 * 60 * 1000;
const AWAY_SINCE_KEY = 'rag_away_since_v1';


function byId(id){return document.getElementById(id);} 
function el(tag, cls){ const e=document.createElement(tag); if(cls) e.className=cls; return e; }

// App config (endpoints)
if(!window.APP_CONFIG){
  window.APP_CONFIG = {
    endpoints: { query: "/api/v1/query", upload: "/api/v1/upload", del: "/api/v1/delete" },
    maxUploadMB: 25
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
  const run_ids = getRunIds();
  const res = await fetch(window.APP_CONFIG.endpoints.query + '?' + new URLSearchParams({
    stream_mode: true
  }).toString(), {
    method: 'POST', 
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: text, run_ids: run_ids })
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

function startAssistantIntro(windowEl){
  const historyNow = loadChatHistory();
  if(Array.isArray(historyNow) && historyNow.length) return;

  const uploads = loadUploads();
  let intro;
  if(Array.isArray(uploads) && uploads.length){
    const names = uploads.map((x,i)=> `${i+1}. ${x.name}`).join('\n');
    intro = `Greet the user briefly. Then list the available documents and ask which one they want to chat with:\n${names}\nFinish with a single, clear question asking them to pick a document.`;
  } else {
    intro = `Greet the user briefly. Explain there are no uploaded documents yet. Ask them to upload a document to chat with from the Upload Document page, then suggest kinds of documents (reports, papers, contracts, etc ) they can upload`;
  }

  let typing;
  (async ()=>{
    try{
      typing = showTyping(windowEl);
      let buf = '';
      let firstChunk = true;
      await sendQuery(intro, (chunk)=>{
        if(firstChunk){ typing.stop(); firstChunk=false; typing.el.innerHTML=''; }
        buf += chunk;
        typing.el.innerHTML = renderMarkdown(buf);
      });
      const cur2 = loadChatHistory();
      cur2.push({ role: 'assistant', text: buf });
      saveChatHistory(cur2);
    }catch(err){
      const errMsg = 'Error: ' + (err?.message || err);
      try { if(typing && typeof typing.stop === 'function') typing.stop(); } catch {}
      const tEl = typing && typing.el ? typing.el : appendMessage(windowEl, 'assistant', '');
      tEl.textContent = errMsg;
      const cur3 = loadChatHistory();
      cur3.push({ role: 'assistant', text: errMsg });
      saveChatHistory(cur3);
    }
  })();
}

function convertHistoryToString(history){
  let historyString = history.map(x=> `${x.role}: ${x.text}`).join('\n');
  return "\nChatHistory:\n" + historyString;
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
  startAssistantIntro(windowEl);
  // New chat handling
  const newBtn = byId('new-chat-btn');
  if(newBtn){
    newBtn.addEventListener('click', ()=>{
      localStorage.removeItem(CHAT_HISTORY_KEY);
      windowEl.innerHTML = '';
      inputEl.focus();
      startAssistantIntro(windowEl);
    });
  }

  inputEl.addEventListener('keydown', (e)=>{
    if(e.key === 'Enter' && !e.shiftKey){
      e.preventDefault();
      if (typeof formEl.requestSubmit === 'function') {
        formEl.requestSubmit();
      } else {
        formEl.submit();
      }
    }
  });
  formEl.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const text = inputEl.value.trim();
    if(!text) return;
    appendMessage(windowEl, 'user', text);
    const cur = loadChatHistory();
    let history = convertHistoryToString(cur)
    cur.push({ role: 'user', text })
    saveChatHistory(cur);
    inputEl.value = '';
    let typing;
    let fullquery = history + "\n User question: " + text;
    try {
      typing = showTyping(windowEl);
      let buf = '';
      let firstChunk = true;
      await sendQuery(fullquery, (chunk) => {
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

function getRunIds(){
  const items = loadUploads();
  if(!Array.isArray(items)) return [];
  return items.map(x=> x && x.run_id).filter(Boolean);
}

async function deleteRunIds(runIds){
  if(!Array.isArray(runIds) || !runIds.length) return { ok: true };
  const url = new URL(window.APP_CONFIG.endpoints.del, window.location.origin);
  const res = await fetch(url.toString(), {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ run_ids: runIds })
  });
  if(!res.ok){
    const t = await res.text().catch(()=> '');
    throw new Error(t || `Delete failed: ${res.status}`);
  }
  return res.json().catch(()=> ({}));
}


async function maybeDeleteAfterAway(){
  const since = Number(localStorage.getItem(AWAY_SINCE_KEY) || 0);
  if(!since) return;

  // one-shot per away session
  localStorage.removeItem(AWAY_SINCE_KEY);

  if(Date.now() - since < AWAY_DELETE_AFTER_MS) return;

  const ids = getRunIds();

  // Clear local storage and, if present, the uploader UI
  try { localStorage.removeItem(UPLOADS_KEY); } catch {}
  const list = byId('uploads-row');
  if(list){ list.innerHTML = ''; }
  const empty = byId('uploads-empty');
  if(empty){ empty.style.display = 'block'; }

  if(!ids.length) return;

  try{
    await deleteRunIds(ids);
  }catch(err){
    console.warn('Auto-delete failed:', err?.message || err);
  }
}

// Attach per-item delete button to an upload card
function attachDeleteButton(card, listEl, name, runId){
  if(!runId) return;
  const delBtn = el('button', 'btn btn-danger');
  delBtn.textContent = 'Delete';
  delBtn.addEventListener('click', async ()=>{
    const original = delBtn.textContent;
    delBtn.disabled = true;
    delBtn.textContent = 'Deleting...';
    try{
      await deleteRunIds([runId]);
      const remaining = (loadUploads() || []).filter(x => x && x.run_id !== runId);
      saveUploads(remaining);
      if(card && card.parentNode === listEl){ listEl.removeChild(card); }
      const empty = byId('uploads-empty');
      if(empty){ empty.style.display = remaining && remaining.length ? 'none' : 'block'; }
    } catch (err){
      alert('Failed to delete: ' + (err?.message || err));
      delBtn.disabled = false;
      delBtn.textContent = original;
    }
  });
  card.appendChild(delBtn);
}

function renderUploadItem(listEl, item){
  const card = el('div', 'upload-card');
  const name = el('div', 'upload-name'); name.textContent = item.name;
  const status = el('div', 'upload-status');
  status.textContent = item.run_id ? `Uploaded successfully (run_id: ${item.run_id})` : 'Uploaded';
  card.appendChild(name); card.appendChild(status);
  if(item.run_id){ attachDeleteButton(card, listEl, item.name, item.run_id); }
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

  const clearBtn = byId('clear-btn');
  if(clearBtn){
    clearBtn.addEventListener('click', async ()=>{
      const ids = getRunIds();
      // Clear local storage and UI immediately
      try { localStorage.removeItem(UPLOADS_KEY); } catch {}
      list.innerHTML = '';
      const empty = byId('uploads-empty'); if(empty){ empty.style.display = 'block'; }
      if(!ids.length){ return; }
      clearBtn.disabled = true;
      const originalText = clearBtn.textContent;
      clearBtn.textContent = 'Clearing...';
      try{
        await deleteRunIds(ids);
      }catch(err){
        alert('Failed to clear: ' + (err?.message || err));
      }finally{
        clearBtn.textContent = originalText;
        clearBtn.disabled = false;
      }
    });
  }

  async function handleFiles(files){
    const maxMB = window.APP_CONFIG.maxUploadMB;
    const existingNames = new Set(((loadUploads() || [])).map(x => x && x.name).filter(Boolean));
  
    for(const file of files){
      const card = el('div', 'upload-card');
      const name = el('div', 'upload-name'); name.textContent = file.name;
      const status = el('div', 'upload-status'); status.textContent = 'Uploading...';
      card.appendChild(name); card.appendChild(status);
      list.prepend(card);
  
      if (existingNames.has(file.name)) {
        status.textContent = 'Skipped: Already uploaded';
        continue;
      }
  
      if (file.size > maxMB * 1024 * 1024) {
        status.textContent = `Failed: File too large. Max ${maxMB} MB`;
        continue;
      }
  
      try{
        const resp = await uploadFile(file);
        const runId = resp.run_id || 'n/a';
        status.textContent = `Upload successful: (run_id: ${runId})`;
        // persist
        const items = loadUploads();
        items.push({ name: file.name, run_id: runId, ts: Date.now() });
        saveUploads(items);
        existingNames.add(file.name);
        const empty = byId('uploads-empty');
        if(empty){ empty.style.display = 'none'; }
        attachDeleteButton(card, list, file.name, runId);
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


document.addEventListener('visibilitychange', ()=>{
  if(document.hidden){
    try { localStorage.setItem(AWAY_SINCE_KEY, String(Date.now())); } catch {}
  } else {
    // user came back
    maybeDeleteAfterAway();
  }
});

// On BFCache restore or regular navigation back to the site
window.addEventListener('pageshow', ()=> {
  maybeDeleteAfterAway();
});

// Also run once on initial load
document.addEventListener('DOMContentLoaded', ()=>{
  maybeDeleteAfterAway();
});

