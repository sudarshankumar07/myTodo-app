// ---------------- SELECT ELEMENTS ----------------
const todoList = document.querySelector(".todo-list");
const addBtn = document.querySelector(".add-task-btn");

const titleInput = document.querySelector("#title");
const taskInput = document.querySelector("#task");
const descInput = document.querySelector("#desc");

// ---------------- ADD TASK ----------------
addBtn.addEventListener("click", async () => {
  const title = titleInput.value.trim();
  const task = taskInput.value.trim();
  const description = descInput.value.trim();

  if (!title || !task) {
    alert("Title and Task are required");
    return;
  }

  try {
    const res = await fetch("/api/add_task", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        title: title,
        task: task,
        description: description
      })
    });

    const data = await res.json();   // 🔥 REQUIRED

    if (!res.ok) {
      alert(data.error || "Failed to add task");
      return;
    }

    clearInputs();
    await loadTasks();               // 🔥 MUST await

  } catch (err) {
    console.error(err);
    alert("Server error while adding task");
  }
});

// ---------------- LOAD TASKS ----------------
async function loadTasks() {
  try {
    const res = await fetch("/api/show_task", {
      method: "GET",
      credentials: "include"
    });

    const data = await res.json();

    if (!res.ok) {
      console.error(data.error);
      return;
    }

    renderTasks(data.tasks);

  } catch (err) {
    console.error("Failed to load tasks:", err);
  }
}

// ---------------- RENDER TASKS ----------------
function renderTasks(tasks) {
  todoList.innerHTML = "";

  if (!tasks || tasks.length === 0) {
    todoList.innerHTML = "<p>No tasks found</p>";
    return;
  }

  tasks.forEach(task => {
    const div = document.createElement("div");
    div.className = "todo-item";

    div.innerHTML = `
      <small>${task.created_at || ""}</small><br>
      <h4>${task.title}</h4>
      <p>${task.task}</p>
      <small>${task.description || ""}</small><br>
      <button type="button" class="task-del-btn" data-id="${task.id}">Delete</button>
      <button type="button" class="task-update-btn" data-id="${task.id}">Update</button>
    `;

    todoList.appendChild(div);
  });
}

// ---------------- DELETE & UPDATE ----------------
todoList.addEventListener("click", async (e) => {

  // ---------- DELETE ----------
  if (e.target.classList.contains("task-del-btn")) {
    const taskId = e.target.dataset.id;

    try {
      const res = await fetch("/delete-task", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ task_id: taskId })
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        alert("Delete failed");
        return;
      }

      await loadTasks();

    } catch (err) {
      console.error(err);
      alert("Server error while deleting");
    }
  }

  // ---------- UPDATE ----------
  if (e.target.classList.contains("task-update-btn")) {
    const taskId = e.target.dataset.id;

    const payload = {};
    if (titleInput.value.trim()) payload.title = titleInput.value.trim();
    if (taskInput.value.trim()) payload.task = taskInput.value.trim();
    if (descInput.value.trim()) payload.description = descInput.value.trim();

    if (Object.keys(payload).length === 0) {
      alert("Enter at least one field to update");
      return;
    }

    try {
      const res = await fetch(`/update-task/${taskId}`, {
        method: "PATCH",
        credentials: "include",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.error || "Update failed");
        return;
      }

      clearInputs();
      await loadTasks();

    } catch (err) {
      console.error(err);
      alert("Server error while updating");
    }
  }
});

// ---------------- LOGOUT ----------------
document.querySelector(".logout").addEventListener("click", async () => {
  try {
    await fetch("/api/logout", {
      method: "POST",
      credentials: "include"
    });
    window.location.href = "/login_page";
  } catch (err) {
    console.error(err);
  }
});

// ---------------- HELPERS ----------------
function clearInputs() {
  titleInput.value = "";
  taskInput.value = "";
  descInput.value = "";
}

// ---------------- INITIAL LOAD ----------------
loadTasks();
