from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

app = FastAPI(title="Tasks API", version="1.0")

# -----------------------
# MODELS
# -----------------------

class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: int = 1  # 1 = baixa | 2 = média | 3 = alta
    created_at: datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 1

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = None

# -----------------------
# DATABASE (fake)
# -----------------------

tasks: List[Task] = []

# -----------------------
# ROUTES
# -----------------------

@app.get("/")
def home():
    return {
        "message": "🚀 API de tarefas rodando",
        "total_tasks": len(tasks)
    }

# Criar tarefa
@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    new_task = Task(
        id=str(uuid4()),
        title=task.title,
        description=task.description,
        priority=task.priority,
        completed=False,
        created_at=datetime.now()
    )
    tasks.append(new_task)
    return new_task

# Listar tarefas com filtros
@app.get("/tasks", response_model=List[Task])
def get_tasks(
    completed: Optional[bool] = Query(None),
    priority: Optional[int] = Query(None)
):
    result = tasks

    if completed is not None:
        result = [t for t in result if t.completed == completed]

    if priority is not None:
        result = [t for t in result if t.priority == priority]

    return result

# Buscar tarefa por ID
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")

# Atualizar tarefa
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, data: TaskUpdate):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            updated = task.model_copy(update=data.dict(exclude_unset=True))
            tasks[index] = updated
            return updated
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")

# Marcar como concluída
@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            task.completed = True
            return {"message": "✅ Tarefa concluída"}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")

# Deletar tarefa
@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            return {"message": "🗑️ Tarefa removida"}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")
