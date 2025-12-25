beat_schedule = {
    'add-every-10-seconds': {
        'task': 'app.worker.tasks.arithmetic.add',
        'schedule': 10.0,
        'args': (16, 16),
    },
}
