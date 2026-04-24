import json
from pathlib import Path
from typing import Any

from flask import Flask, redirect, render_template, request

app = Flask(__name__)

DATA_FILE = Path("tasks.json")
tasks: list[dict[str, Any]] = []
next_id = 1


def save_data() -> None:
    payload = {"next_id": next_id, "tasks": tasks}
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def load_data() -> None:
    global next_id, tasks

    if not DATA_FILE.exists():
        return

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return

    next_id = int(data.get("next_id", 1))
    tasks = list(data.get("tasks", []))


def add_task(text: str) -> None:
    global next_id

    tasks.append({"id": next_id, "text": text, "done": False})
    next_id += 1
    save_data()


def complete_task(task_id: int) -> None:
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            save_data()
            return


def get_sorted_tasks() -> list[dict[str, Any]]:
    return sorted(tasks, key=lambda task: task["done"])


@app.route("/")
def index() -> str:
    return render_template("index.html", tasks=get_sorted_tasks())


@app.route("/add", methods=["POST"])
def add() -> Any:
    task_text = request.form.get("task_text", "").strip()
    if task_text:
        add_task(task_text)
    return redirect("/")


@app.route("/complete/<int:task_id>", methods=["POST", "GET"])
def complete(task_id: int) -> Any:
    complete_task(task_id)
    return redirect("/")


if __name__ == "__main__":
    load_data()
    app.run(debug=True)