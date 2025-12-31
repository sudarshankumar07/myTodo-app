// Grab button once
const addTaskBtn = document.querySelector(".add-task-btn");
const todoList = document.querySelector(".todo-list");

// ================= ADD TASK =================
addTaskBtn.addEventListener("click", async () => {
  const title = document.querySelector("#title").value.trim();
  const task = document.querySelector("#task").value.trim();
  const description = document.querySelector("#desc").value.trim();

  if (!title || !task) {
    alert("Title and Task are required");
    return;
  }

  try {
    const res = await fetch("/api/add_task", {
      method: "POST",
      credentials: "include",   // ✅ REQUIRED
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, task, description })
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Failed to add task");
    }

    clearInputs();
    loadTasks();

  } catch (err) {
    console.error(err);
    alert(err.message);
  }
});

// ================= CLEAR INPUTS =================
function clearInputs() {
  document.querySelector("#title").value = "";
  document.querySelector("#task").value = "";
  document.querySelector("#desc").value = "";
}

// ================= LOAD TASKS =================
async function loadTasks() {
  try {
    const res = await fetch("/api/show_task", {
      method: "GET",
      credentials: "include"   // ✅ REQUIRED
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Failed to fetch tasks");
    }

    re

