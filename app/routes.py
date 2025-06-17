from flask import Blueprint, render_template, request, jsonify
from app.extensions import db,socketio
from app.models import Server
from flask_socketio import emit
from .monitor import start_background_thread
import logging

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/servers')
def servers():
    return render_template('servers.html')


@main.route('/add_server', methods=['POST'])
def add_server():
    data = request.get_json()
    name = data.get('name')
    ip_address = data.get('ip_address')
    
    if not name or not ip_address:
        return jsonify({'success': False, 'error': 'Name and IP address are required'}), 400
    
    try:
        server = Server(name=name, ip_address=ip_address)
        db.session.add(server)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@main.route('/get_servers', methods=['GET'])
def get_servers():
    servers = Server.query.all()
    return jsonify({
        'servers': [
            {
                'name': server.name,
                'ip_address': server.ip_address,
                'status': server.status,
                'last_updated': server.last_updated.isoformat()
            } for server in servers
        ]
    })

@main.route('/monitor')
def start_monitoring():
    start_background_thread()
    return jsonify({'success': True})

logger = logging.getLogger(__name__)
@socketio.on('connect')
def handle_connect():
    print("🔌 Client connected to SocketIO")
    logger.info("Client connected")
    
    # Start monitoring when first client connects
    try:
        start_background_thread()
        print("✅ Background monitoring ensured running")
    except Exception as e:
        print(f"❌ Error starting background monitoring: {e}")
    
    emit('connection_response', {'status': 'connected'})
    
@socketio.on('disconnect')
def handle_disconnect():
    print("🔌 Client disconnected from SocketIO")
    logger.info("Client disconnected")
    
@socketio.on('request_update')
def handle_request_update():
    """Allow frontend to request immediate update"""
    print("📡 Client requested immediate update")
    # The background thread will send updates automatically
    emit('update_requested', {'status': 'processing'})
    
    
    


# @main.route('/test')
# def test():
#     return render_template('test.html')

# @main.route('/emit-test')
# def emit_test():
#     from app.extensions import socketio
#     socketio.emit('server_update', {
#         'active_servers': 3,
#         'uptime': 75.0,
#         'critical_alerts': 1,
#         'total_monitors': 4
#     })
#     return "Event emitted"


# @main.route('/test_monitor')
# def test_monitor():
#     from app.monitor import server_monitor
#     # Run one cycle manually
#     return "Check console logs"




# from flask_socketio import emit, disconnect
# from app.extensions import socketio
# from app.monitor import start_background_thread


# logger = logging.getLogger(__name__)

# @socketio.on('connect')
# def handle_connect():
#     print("🔌 Client connected to SocketIO")
#     logger.info("Client connected")
    
#     # Start monitoring when first client connects
#     try:
#         start_background_thread()
#         print("✅ Background monitoring ensured running")
#     except Exception as e:
#         print(f"❌ Error starting background monitoring: {e}")
    
#     emit('connection_response', {'status': 'connected'})

# @socketio.on('disconnect')
# def handle_disconnect():
#     print("🔌 Client disconnected from SocketIO")
#     logger.info("Client disconnected")

# @socketio.on('request_update')
# def handle_request_update():
#     """Allow frontend to request immediate update"""
#     print("📡 Client requested immediate update")
#     # The background thread will send updates automatically
#     emit('update_requested', {'status': 'processing'})
    
    



