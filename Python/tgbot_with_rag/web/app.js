let EMBEDDING_PRESETS = [];

async function loadEmbeddingPresets() {
  try {
    const res = await fetch('/api/embedding_presets');
    const json = await res.json();
    if (json.ok && Array.isArray(json.presets)) EMBEDDING_PRESETS = json.presets;
  } catch (_) {}
}

function toast(msg, ok = true) {
  const el = document.getElementById('saveResult');
  if (!el) return;
  el.textContent = msg;
  el.style.color = ok ? 'green' : 'red';
  setTimeout(() => {
    el.textContent = '';
  }, 3000);
}

async function fillEmbeddingPresets() {
  if (!EMBEDDING_PRESETS.length) await loadEmbeddingPresets();
  const sel = document.getElementById('EMBEDDINGS_MODEL_PRESET');
  if (!sel) return;
  sel.innerHTML = '';
  EMBEDDING_PRESETS.forEach((m) => {
    const opt = document.createElement('option');
    opt.value = m.pull || m.name || '';
    opt.textContent = m.title || m.name || opt.value;
    sel.appendChild(opt);
  });
  const info = document.getElementById('EMBED_INFO');
  function updateInfo() {
    const val = sel.value;
    const m = EMBEDDING_PRESETS.find((x) => (x.pull || x.name) === val);
    if (m && info) {
      const size = m.size || '—';
      const ctx = m.ctx || '—';
      const params = m.params || '—';
      const vram = m.vram || '—';
      info.textContent = `Размер: ${size} · Контекст: ${ctx} · Параметры: ${params} · VRAM: ${vram}`;
    }
    const fld = document.getElementById('EMBEDDINGS_MODEL');
    if (fld) fld.value = val;
  }
  sel.addEventListener('change', updateInfo);
  // выставить сохранённое значение
  const saved = document.getElementById('EMBEDDINGS_MODEL')?.value || '';
  if (saved) sel.value = saved;
  updateInfo();
}

async function refreshLLMModels() {
  try {
    const res = await fetch('/api/llm_models');
    const json = await res.json();
    const sel = document.getElementById('OPENAI_RESPONSE_MODEL_SELECT');
    if (!sel) return;
    sel.innerHTML = '';
    let modelsArr = [];
    if (json.ok && json.data) {
      if (Array.isArray(json.data.data)) {
        modelsArr = json.data.data;
      } else if (Array.isArray(json.data)) {
        modelsArr = json.data;
      }
    }
    if (modelsArr.length > 0) {
      modelsArr.forEach((m) => {
        const id = m.id || m.name || '';
        if (!id) return;
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = id;
        sel.appendChild(opt);
      });
      const saved = document.getElementById('OPENAI_RESPONSE_MODEL')?.value || '';
      if (saved) {
        const exists = Array.from(sel.options).some((o) => o.value === saved);
        if (!exists) {
          const opt = document.createElement('option');
          opt.value = saved;
          opt.textContent = saved;
          sel.appendChild(opt);
        }
        sel.value = saved;
      }
    } else {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'нет данных';
      sel.appendChild(opt);
    }
    sel.addEventListener('change', () => {
      const fld = document.getElementById('OPENAI_RESPONSE_MODEL');
      if (fld) fld.value = sel.value;
    });
    const fld = document.getElementById('OPENAI_RESPONSE_MODEL');
    if (fld) fld.value = sel.value;
    toast('Список моделей обновлен', true);
  } catch (_) {
    toast('Не удалось загрузить список моделей', false);
  }
}

async function saveConfig() {
  const data = {
    EMBEDDINGS_MODEL: document.getElementById('EMBEDDINGS_MODEL').value,
    OPENAI_BASE_URL: document.getElementById('OPENAI_BASE_URL').value,
    OPENAI_API_KEY: (function () {
      const masked = document.getElementById('OPENAI_API_KEY').value || '';
      const real = document.getElementById('OPENAI_API_KEY_REAL').value || '';
      if (masked.includes('*')) return real;
      return masked;
    })(),
    OPENAI_ORGANIZATION: document.getElementById('OPENAI_ORGANIZATION').value,
    OPENAI_RESPONSE_MODEL: document.getElementById('OPENAI_RESPONSE_MODEL').value,
    ALLOWED_USERS: document.getElementById('ALLOWED_USERS').value,
    HISTORY_MAX_PAIRS: (function () {
      const v = Number(document.getElementById('HISTORY_MAX_PAIRS').value || 10);
      if (!Number.isFinite(v)) return 10;
      if (v < 0) return 0;
      if (v > 50) return 50;
      return Math.floor(v);
    })(),
  };
  try {
    const res = await fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (res.ok && json.ok) toast('Сохранено', true);
    else toast('Ошибка сохранения', false);
  } catch (_) {
    toast('Ошибка сети', false);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('saveBtn')?.addEventListener('click', saveConfig);
  document.getElementById('restartBtn')?.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/restart', { method: 'POST' });
      const json = await res.json();
      toast(json.message || 'Перезапуск…', true);
    } catch (_) {
      toast('Ошибка запроса перезапуска', false);
    }
  });
  document.querySelectorAll('.help').forEach((btn) => {
    btn.addEventListener('click', () => {
      const msg = btn.getAttribute('data-help') || '';
      let pop = btn._popover;
      if (!pop) {
        pop = document.createElement('div');
        pop.className = 'popover-like shadow';
        pop.textContent = msg;
        pop.style.position = 'absolute';
        pop.style.maxWidth = '360px';
        pop.style.background = '#fff';
        pop.style.border = '1px solid #ccc';
        pop.style.padding = '8px';
        pop.style.borderRadius = '6px';
        document.body.appendChild(pop);
        btn._popover = pop;
      }
      const r = btn.getBoundingClientRect();
      pop.style.left = window.scrollX + r.left + 'px';
      pop.style.top = window.scrollY + r.bottom + 6 + 'px';
      pop.style.display = pop.style.display === 'block' ? 'none' : 'block';
      document.addEventListener(
        'click',
        (ev) => {
          if (!btn.contains(ev.target) && pop && !pop.contains(ev.target)) pop.style.display = 'none';
        },
        { once: true }
      );
    });
  });
  fillEmbeddingPresets();
  const refreshBtn = document.getElementById('REFRESH_LLM_MODELS');
  if (refreshBtn) refreshBtn.addEventListener('click', refreshLLMModels);
  refreshLLMModels();

  // Кнопка загрузки и поллинг статуса
  const pullBtn = document.getElementById('EMBED_PULL_BTN');
  const progressEl = document.getElementById('EMBED_PULL_PROGRESS');
  const statusEl = document.getElementById('EMBED_PULL_STATUS');
  let pollTimer = null;

  function setProgress(p) {
    const v = Math.max(0, Math.min(100, Number(p) || 0));
    if (progressEl) {
      progressEl.style.width = v + '%';
      progressEl.setAttribute('aria-valuenow', String(v));
      progressEl.textContent = v ? v + '%' : '';
    }
  }

  async function pollStatusOnce() {
    try {
      const res = await fetch('/api/embeddings/pull_status');
      const json = await res.json();
      if (!json.ok) return;
      const st = json.state || {};
      setProgress(st.progress || 0);
      if (statusEl) statusEl.textContent = (st.status || '').toString();
      if (pullBtn) pullBtn.disabled = !!st.running;
      if (!st.running) {
        if (pollTimer) {
          clearInterval(pollTimer);
          pollTimer = null;
        }
        if (st.error) toast('Ошибка загрузки: ' + st.error, false);
        else if (st.progress >= 100) toast('Модель загружена', true);
      }
    } catch (_) {
      // игнорируем сеть во время поллинга
    }
  }

  async function startPull() {
    const sel = document.getElementById('EMBEDDINGS_MODEL_PRESET');
    const name = sel ? sel.value : '';
    if (!name) return;
    try {
      if (pullBtn) pullBtn.disabled = true;
      setProgress(0);
      if (statusEl) statusEl.textContent = 'Запрос на загрузку…';
      const res = await fetch('/api/embeddings/pull', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      const json = await res.json();
      if (!res.ok || !json.ok) {
        if (pullBtn) pullBtn.disabled = false;
        toast(json.error || 'Не удалось начать загрузку', false);
        return;
      }
      // Старт поллинга
      pollStatusOnce();
      pollTimer = setInterval(pollStatusOnce, 1000);
    } catch (e) {
      if (pullBtn) pullBtn.disabled = false;
      toast('Ошибка сети', false);
    }
  }

  if (pullBtn) pullBtn.addEventListener('click', startPull);
  // при открытии страницы проверить незавершенную загрузку
  pollStatusOnce();

  // Подключение к стриму логов Docker через SSE
  const dockerLogsDiv = document.getElementById('dockerLogs');
  if (dockerLogsDiv) {
    dockerLogsDiv.textContent = 'Подключение к стриму логов...';
    
    const eventSource = new EventSource('/api/docker/logs');
    const maxLines = 200;
    let firstMessage = true;

    eventSource.onmessage = function(event) {
      const line = event.data;
      if (!line) return;
      
      if (firstMessage) {
        dockerLogsDiv.textContent = '';
        firstMessage = false;
      }
      
      const logLine = document.createElement('div');
      logLine.textContent = line;
      logLine.style.marginBottom = '2px';
      logLine.style.wordBreak = 'break-word';
      
      // Вставляем новые логи в начало списка
      if (dockerLogsDiv.firstChild) {
        dockerLogsDiv.insertBefore(logLine, dockerLogsDiv.firstChild);
      } else {
        dockerLogsDiv.appendChild(logLine);
      }
      
      // Удаляем старые логи снизу
      while (dockerLogsDiv.children.length > maxLines) {
        dockerLogsDiv.removeChild(dockerLogsDiv.lastChild);
      }
      
      // Скролл остается наверху (где новые логи)
      dockerLogsDiv.scrollTop = 0;
    };

    eventSource.onerror = function(err) {
      if (firstMessage) {
        dockerLogsDiv.textContent = '';
        firstMessage = false;
      }
      const errorLine = document.createElement('div');
      errorLine.textContent = 'Ошибка подключения к стриму логов. Проверьте права доступа к Docker socket.';
      errorLine.style.color = '#ff6b6b';
      errorLine.style.marginTop = '10px';
      
      // Ошибку тоже показываем сверху
      if (dockerLogsDiv.firstChild) {
        dockerLogsDiv.insertBefore(errorLine, dockerLogsDiv.firstChild);
      } else {
        dockerLogsDiv.appendChild(errorLine);
      }
      
      eventSource.close();
    };
    
    eventSource.onopen = function() {
      console.log('Подключение к стриму логов установлено');
    };
  }
});


