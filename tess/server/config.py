class Config:
    def __init__(self, config: dict):
        self.port = config['port']
        self.host = config['host']
        self.task_queue = config['task_queue']
        self.tables = config['tables']
