// ----------------------
// Создание sessionId
// ----------------------
if (!localStorage.getItem("sessionId")) {
  localStorage.setItem("sessionId", crypto.randomUUID());
}

const input = document.getElementById("questionInput");
const chatBox = document.getElementById("chat-history");
const historyList = document.getElementById("history-list");

// ----------------------
// Отправка текстового сообщения
// ----------------------
// ----------------------
// Защита от двойной отправки
// ----------------------
let isSending = false;

async function sendMessage() {
  if (isSending) return;

  const sessionId = localStorage.getItem("sessionId");
  const question = input.value.trim();

  if (!question) return;

  isSending = true;
  input.value = "";

  const userDiv = document.createElement("div");
  userDiv.classList.add("message", "user");
  userDiv.textContent = question;
  chatBox.appendChild(userDiv);

  const assistantDiv = document.createElement("div");
  assistantDiv.classList.add("message", "assistant");
  assistantDiv.textContent = "";
  chatBox.appendChild(assistantDiv);

  const res = await fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ sessionId, question })
  });

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    assistantDiv.textContent += chunk;
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  isSending = false;
}

// ----------------------
// Загрузка истории
// ----------------------
async function loadHistory() {
  const sessionId = localStorage.getItem("sessionId");

  const res = await fetch("/history", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessionId })
  });

  const history = await res.json();
  renderHistory(history);
  renderSidebar(history);
}

// ----------------------
// Рендер чата справа
// ----------------------
function renderHistory(history) {
  chatBox.innerHTML = "";

  history.forEach(msg => {
    const div = document.createElement("div");
    div.classList.add("message");
    div.classList.add(msg.role === "user" ? "user" : "assistant");
    div.textContent = msg.content;
    chatBox.appendChild(div);
  });

  chatBox.scrollTop = chatBox.scrollHeight;
}

// ----------------------
// Рендер списка сообщений слева
// ----------------------
function renderSidebar(history) {
  historyList.innerHTML = "";

  history.forEach((msg, i) => {
    if (msg.role === "user") {
      const item = document.createElement("div");
      item.textContent = "• " + msg.content.slice(0, 25) + "...";
      item.style.marginBottom = "8px";
      item.style.cursor = "pointer";

      item.onclick = () => {
        chatBox.scrollTop = chatBox.children[i].offsetTop - 20;
      };

      historyList.appendChild(item);
    }
  });
}

// ----------------------
// Отправка изображения
// ----------------------
async function sendImage() {
  const file = document.getElementById("imageInput").files[0];
  if (!file) {
    alert("Выберите изображение");
    return;
  }

  const sessionId = localStorage.getItem("sessionId");

  const formData = new FormData();
  formData.append("image", file);
  formData.append("sessionId", sessionId);

  document.getElementById("result").textContent = "Обработка...";

  const res = await fetch("/analyze", {
    method: "POST",
    body: formData
  });

  const text = await res.text();
  document.getElementById("result").textContent = text;

  await loadHistory();
}

// ----------------------
// Кнопка отправки
// ----------------------
document.getElementById("sendBtn").addEventListener("click", sendMessage);

// Enter для отправки
input.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

// ----------------------
// Загрузка истории при старте
// ----------------------
loadHistory();