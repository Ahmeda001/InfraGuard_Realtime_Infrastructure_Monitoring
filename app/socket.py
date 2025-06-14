import threading
import random
import time
from flask_socketio import SocketIO, emit

# socketio instance (we'll initialize this in __init__.py)
socketio = SocketIO()

# Background monitor thread
monitor_thread = None

def server_monitor():
    """Background task to emit server metrics"""
    while True:
        cpu_usage = random.randint(10, 100)
        memory_usage = random.randint(20, 90)
        socketio.emit('server_update', {
            'cpu': cpu_usage,
            'memory': memory_usage
        })
        time.sleep(3)

def start_background_thread():
    """Start background thread once"""
    global monitor_thread
    if monitor_thread is None:
        monitor_thread = threading.Thread(target=server_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()

# SocketIO Events

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'message': 'You are connected to the server'})
