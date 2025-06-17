from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
from app.extensions import db,socketio
from ping3 import ping
from app.models import Server
from app import db 
from flask_socketio import emit
from .monitor import start_background_thread, emit_server_stats
from .monitor import ping_all_servers,_ping_server
import logging
import threading

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
def broadcast_server_update():
    servers = Server.query.all()
    data = []
    for s in servers:
        data.append({
            'id': s.id,
            'name': s.name,
            'ip_address': s.ip_address,
            'status': s.status,
            'last_updated': s.last_updated.isoformat()
        })
    # Emit real-time update via SocketIO
    socketio.emit("server_update", {"some": "data"})
    # Return valid HTTP response
    return jsonify({"success": True, "message": "Server update broadcasted."})


@main.route('/servers/<int:server_id>')
def server_detail(server_id):
    server = Server.query.get_or_404(server_id)
    return render_template('server_detail.html', server=server)

@main.route('/servers/<int:server_id>/restart', methods=['POST'])
def restart_server(server_id):
    server = Server.query.get(server_id)
    if not server:
        flash("Server not found", "error")
        return redirect(url_for('main.servers'))
    try:
        # Simulate restarting the server
        # In a real app, you'd run system commands, API calls, or Celery jobs
        server.status = 'restarting'

        # Simulate a delay and then back to online
        # You can integrate Celery task or actual async handler here
        server.status = 'online'
        server.last_updated = datetime.utcnow()

        db.session.commit()
        flash(f"Server '{server.name}' restarted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to restart server: {str(e)}", "error")
    return redirect(url_for('main.server_detail', server_id=server_id))


@main.route('/servers/<int:server_id>/ping', methods=['POST'])
def ping_server(server_id):
    server = Server.query.get(server_id)
    if not server:
        flash("Server not found.", "error")
        return redirect(url_for('main.servers'))

    try:
        response_time = ping(server.ip_address, timeout=1.5)

        if response_time is not None:
            server.status = "online"
            flash(f"{server.name} is reachable (online) - {response_time:.2f} ms", "success")
        else:
            server.status = "offline"
            flash(f"{server.name} is not reachable (offline)", "warning")

        server.last_updated = datetime.utcnow()
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f"Ping failed: {str(e)}", "error")
    return redirect(url_for('main.server_detail', server_id=server_id))



@main.route('/servers/<int:server_id>/delete', methods=['POST'])
def delete_server(server_id):
    server = Server.query.get(server_id)
    
    if not server:
        flash("Server not found.", "error")
        return redirect(url_for('main.servers'))
    try:
        db.session.delete(server)
        db.session.commit()
        flash(f"Server '{server.name}' has been deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting server: {str(e)}", "error")
        
    return redirect(url_for('main.servers'))


@main.route('/add_server', methods=['POST'])
def add_server():
    data = request.get_json()
    name = data.get('name')
    ip_address = data.get('ip_address')
    description = data.get('description')
    
    if not name or not ip_address:
        return jsonify({'success': False, 'error': 'Name and IP address are required'}), 400
    
    try:
        server = Server(name=name, ip_address=ip_address , description=description)
        db.session.add(server)
        db.session.commit()
        _ping_server(server)
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@main.route('/get_servers', methods=['GET'])
def get_servers():
    servers = Server.query.all()
    data = [{
        "id": s.id,
        "name": s.name,
        "ip_address": s.ip_address,
        "status": s.status,
        "last_updated": s.last_updated.isoformat()
    } for s in servers]
    response = jsonify({"servers": data})
    threading.Thread(target=ping_all_servers).start()
    return response


logger = logging.getLogger(__name__)
@socketio.on('connect')
def handle_connect():
    print("🔌 Client connected to SocketIO")
    logger.info("Client connected")
    
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
    
@socketio.on('request_initial_stats')
def handle_initial_request():
    emit_server_stats()
    
    
