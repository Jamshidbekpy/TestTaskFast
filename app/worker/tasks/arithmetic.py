from app.worker.celery_app import celery_app

@celery_app.task
def add(x, y):
    print(f"add task: {x + y}")
    return x + y

@celery_app.task
def mul(x, y):
    add.apply_async((x, y))
    print(f"mul task: {x * y}")
    return x * y
