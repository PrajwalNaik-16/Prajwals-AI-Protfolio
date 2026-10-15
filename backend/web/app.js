const form = document.querySelector("#chat-form");
const input = document.querySelector("#question");
const messages = document.querySelector("#messages");
const typing = document.querySelector("#typing");
const sendButton = document.querySelector(".send-button");
const history = [];

function addMessage(text, role) {
  const row = document.createElement("div");
  row.className = `message ${role === "user" ? "user-message" : "assistant-message"}`;
  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = role === "user" ? "P" : "p";
  const content = document.createElement("div");
  content.className = "message-content";
  const author = document.createElement("div");
  author.className = "message-author";
  author.textContent = role === "user" ? "YOU" : "PRAJWAL AI";
  const time = document.createElement("span");
  time.textContent = "JUST NOW";
  author.append(time);
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  content.append(author, bubble);
  row.append(avatar, content);
  messages.append(row);
  messages.scrollTop = messages.scrollHeight;
}

async function ask(question) {
  const cleaned = question.trim();
  if (!cleaned || sendButton.disabled) return;
  addMessage(cleaned, "user");
  history.push({ role: "user", content: cleaned });
  input.value = "";
  input.style.height = "25px";
  sendButton.disabled = true;
  typing.hidden = false;
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: cleaned, history: history.slice(0, -1) }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Something went wrong.");
    const answer = payload.answer || "I don't have enough information to answer that.";
    addMessage(answer, "assistant");
    history.push({ role: "assistant", content: answer });
  } catch (error) {
    const answer = error.message || "I couldn't reach the assistant. Please try again.";
    addMessage(answer, "assistant");
    history.push({ role: "assistant", content: answer });
  } finally {
    typing.hidden = true;
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  ask(input.value);
});

input.addEventListener("input", () => {
  input.style.height = "25px";
  input.style.height = `${Math.min(input.scrollHeight, 76)}px`;
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll(".suggestion").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.question;
    ask(input.value);
  });
});
