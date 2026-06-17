const API_URL = window.AGENT_API_URL || 'http://127.0.0.1:8000';

const demoPrompts = [
  'how many products do you have?',
  'where is order #1001?',
  'can I return my purchase?',
  'I have frizzy hair, which product should I get?',
  'this is unacceptable, I want a refund dispute reviewed',
];

const intentLabels = {
  PRODUCT_COUNT: 'Commerce API',
  ORDER_STATUS: 'Commerce API',
  ESCALATE: 'Escalation',
  RAG: 'RAG',
};

const chat = document.querySelector('#chat');
const composer = document.querySelector('#composer');
const input = document.querySelector('#message-input');
const platform = document.querySelector('#platform');
const prompts = document.querySelector('#prompts');
const error = document.querySelector('#error');
const setup = document.querySelector('#setup');
const storeForm = document.querySelector('#store-form');
const storeUrl = document.querySelector('#store-url');
const setupStatus = document.querySelector('#setup-status');
const downloadLink = document.querySelector('#download-link');
const enterChat = document.querySelector('#enter-chat');
const useDemo = document.querySelector('#use-demo');

function formatJson(value) {
  return JSON.stringify(value, null, 2);
}

function createMessage({ role, text, intent, toolResult, sources }) {
  const isUser = role === 'user';
  const article = document.createElement('article');
  article.className = `message ${isUser ? 'message-user' : 'message-agent'}`;

  const header = document.createElement('div');
  header.className = 'message-header';
  const label = document.createElement('span');
  label.textContent = isUser ? 'Customer' : 'Agent';
  header.appendChild(label);

  if (intent) {
    const badge = document.createElement('span');
    badge.className = `intent intent-${intent.toLowerCase()}`;
    badge.textContent = `${intent} · ${intentLabels[intent] || 'Router'}`;
    header.appendChild(badge);
  }

  const paragraph = document.createElement('p');
  paragraph.textContent = text;

  article.appendChild(header);
  article.appendChild(paragraph);

  if (toolResult) {
    const details = document.createElement('details');
    const summary = document.createElement('summary');
    const pre = document.createElement('pre');
    summary.textContent = 'Tool result';
    pre.textContent = formatJson(toolResult);
    details.appendChild(summary);
    details.appendChild(pre);
    article.appendChild(details);
  }

  if (sources?.length) {
    const details = document.createElement('details');
    const summary = document.createElement('summary');
    const sourceList = document.createElement('div');
    summary.textContent = 'Sources';
    sourceList.className = 'sources';

    sources.forEach((source) => {
      const section = document.createElement('section');
      const title = document.createElement('strong');
      const sourceText = document.createElement('p');
      title.textContent = source.file_name || 'source';
      sourceText.textContent = source.text;
      section.appendChild(title);
      section.appendChild(sourceText);
      sourceList.appendChild(section);
    });

    details.appendChild(summary);
    details.appendChild(sourceList);
    article.appendChild(details);
  }

  chat.appendChild(article);
  chat.scrollTop = chat.scrollHeight;
}

function setLoading(isLoading) {
  composer.querySelector('button').disabled = isLoading || !input.value.trim();
  input.disabled = isLoading;
  document.querySelectorAll('.prompt-row button').forEach((button) => {
    button.disabled = isLoading;
  });
}

function setChatVisible(isVisible) {
  prompts.hidden = !isVisible;
  chat.hidden = !isVisible;
  composer.hidden = !isVisible;
  error.hidden = !isVisible;
  setup.hidden = isVisible;
  if (isVisible) input.focus();
}

function setSetupLoading(isLoading) {
  storeUrl.disabled = isLoading;
  storeForm.querySelector('button').disabled = isLoading || !storeUrl.value.trim();
  useDemo.disabled = isLoading;
}

async function generateKnowledge(event) {
  event.preventDefault();
  const url = storeUrl.value.trim();
  if (!url) return;

  setupStatus.textContent = 'Generating store knowledge files...';
  downloadLink.hidden = true;
  enterChat.hidden = true;
  setSetupLoading(true);

  try {
    const response = await fetch(`${API_URL}/knowledge/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ store_url: url, output_format: 'markdown' }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail?.suggestion || `Request failed with ${response.status}`);
    }

    const fileNames = Object.keys(data.files || {}).join(', ') || 'products.md, policy.md, faq.md';
    setupStatus.textContent = `Knowledge base ready. Generated ${fileNames}. Found ${data.product_count} product records.`;
    downloadLink.href = `${API_URL}${data.download_url}`;
    downloadLink.hidden = false;
    enterChat.hidden = false;
  } catch (requestError) {
    setupStatus.textContent = requestError.message || 'Could not generate store knowledge.';
  } finally {
    setSetupLoading(false);
  }
}

async function sendMessage(message) {
  const text = message.trim();
  if (!text) return;

  input.value = '';
  error.textContent = '';
  createMessage({ role: 'user', text });
  setLoading(true);

  const typing = document.createElement('div');
  typing.className = 'typing';
  typing.textContent = 'Routing request...';
  chat.appendChild(typing);

  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, platform: platform.value }),
    });

    if (!response.ok) {
      throw new Error(`Request failed with ${response.status}`);
    }

    const data = await response.json();
    typing.remove();
    createMessage({
      role: 'agent',
      text: data.answer,
      intent: data.intent,
      toolResult: data.tool_result,
      sources: data.sources,
    });
  } catch (requestError) {
    typing.remove();
    error.textContent = requestError.message || 'Something went wrong.';
    createMessage({
      role: 'agent',
      text: 'I could not reach the backend. Check that FastAPI is running on port 8000.',
    });
  } finally {
    setLoading(false);
    input.focus();
  }
}

demoPrompts.forEach((prompt) => {
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = prompt;
  button.addEventListener('click', () => sendMessage(prompt));
  prompts.appendChild(button);
});

composer.addEventListener('submit', (event) => {
  event.preventDefault();
  sendMessage(input.value);
});

input.addEventListener('input', () => setLoading(false));
storeUrl.addEventListener('input', () => setSetupLoading(false));
storeForm.addEventListener('submit', generateKnowledge);
enterChat.addEventListener('click', () => setChatVisible(true));
useDemo.addEventListener('click', () => {
  setupStatus.textContent = 'Using the current demo knowledge files.';
  setChatVisible(true);
});

createMessage({
  role: 'agent',
  text: 'Hi, what can I help with today?',
});
setLoading(false);
setSetupLoading(false);
setChatVisible(false);
