import express from "express";
import multer from "multer";
import fs from "fs";
import fetch from "node-fetch";

const app = express();
app.use(express.static("public"));
app.use(express.json());

const MAX_HISTORY = 10;

// Хранилище всех диалогов
let sessions = {};

// ----------------------
// Вспомогательные функции
// ----------------------

function getSession(sessionId) {
  if (!sessions[sessionId]) {
    sessions[sessionId] = [];
  }
  return sessions[sessionId];
}

function saveHistoryToFile(data) {
  fs.writeFileSync("history.json", JSON.stringify(data, null, 2));
}

function loadHistoryFromFile() {
  try {
    return JSON.parse(fs.readFileSync("history.json", "utf8"));
  } catch {
    return {};
  }
}

function trimHistory(history) {
  if (history.length > MAX_HISTORY) {
    return history.slice(-MAX_HISTORY);
  }
  return history;
}

function imageToBase64(path) {
  return fs.readFileSync(path).toString("base64");
}

function chooseModel(hasImage) {
  return hasImage ? "llava" : "llama3";
}

async function askOllama(sessionId, question, imageBase64 = null) {
  const history = getSession(sessionId);
  const hasImage = Boolean(imageBase64);
  const model = chooseModel(hasImage);

  const userMessage = {
    role: "user",
    content: question,
  };

  if (hasImage) {
    userMessage.images = [imageBase64];
  }

  history.push(userMessage);

  

  const response = await fetch("http://localhost:11434/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      messages: history,
      stream: false,
    }),
  });

  const data = await response.json();
  const answer = data.message?.content || "Нет ответа";

  history.push({
    role: "assistant",
    content: answer,
  });

  sessions[sessionId] = trimHistory(history);

  return answer;
}

// ----------------------
// Настройка загрузки файлов
// ----------------------

const upload = multer({
  dest: "uploads/",
  limits: { fileSize: 5 * 1024 * 1024 },
});

// ----------------------
// Маршруты
// ----------------------

app.post("/analyze", upload.single("image"), async (req, res) => {
  try {
    const sessionId = req.body.sessionId;
    const filePath = req.file.path;
    const base64 = imageToBase64(filePath);

    const result = await askOllama(
      sessionId,
      "What do you see on this picture? Give a full detailed answer.",
      base64
    );

    fs.unlinkSync(filePath);
    res.send(result);
  } catch (err) {
    res.status(500).send("Ошибка: " + err.message);
  }
});

async function loadHistory() {
  const sessionId = localStorage.getItem("sessionId");

  const res = await fetch("/history", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessionId })
  });

  const history = await res.json();
  renderHistory(history);
}

function renderHistory(history) {
  const box = document.getElementById("chat-history");
  box.innerHTML = "";

  history.forEach(msg => {
    const div = document.createElement("div");
    div.classList.add("message");
    div.classList.add(msg.role === "user" ? "user" : "assistant");
    div.textContent = msg.content;
    box.appendChild(div);
  });
}

app.post("/ask", async (req, res) => {
  const { question } = req.body;

  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.setHeader("Transfer-Encoding", "chunked");

const ollamaRes = await fetch("http://localhost:11434/api/generate", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    model: "llama3",
    prompt: question,
    stream: true
  })
});

for await (const chunk of ollamaRes.body) {

  const lines = chunk.toString().split("\n").filter(Boolean);

  for (const line of lines) {

    const data = JSON.parse(line);

    if (typeof data.response === "string") {
      res.write(data.response);
    }

    if (data.done === true) {
      res.end();
      return;
    }
  }
}
});



app.post("/history", express.json(), (req, res) => {
  const { sessionId } = req.body;

  if (!sessions[sessionId]) {
    return res.send([]);
  }

  res.send(sessions[sessionId]);
});

// ----------------------
// Запуск сервера
// ----------------------

app.listen(3000, () =>
  console.log("Сервер запущен на http://localhost:3000")
);
