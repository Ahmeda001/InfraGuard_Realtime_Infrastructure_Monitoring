import time
import logging
from datetime import datetime
from ping3 import ping
from .extensions import db, socketio
from .models import Server
from app import socketio
from app.models import Server, db


# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

_background_app = None

logger = logging.getLogger(__name__)
_background_app = None
monitoring_thread_started = False
ping_cache = {}  # Format: {server_id: (timestamp, status)}

def set_background_app(app):
    global _background_app
    _background_app = app
    logger.info("✅ Background app set successfully")

def _ping_server(server):
    """Ping a single server and update DB if needed. Return True if status changed."""
    server_id = server.id
    now = datetime.utcnow()

    # Use cache if pinged < 20s ago
    if server_id in ping_cache:
        cached_time = ping_cache[server_id]
        if isinstance(cached_time, tuple) and isinstance(cached_time[0], datetime):
            cached_time, cached_status = cached_time
        if (now - cached_time).total_seconds() < 30:
            return False  # No change emitted

    # Perform ping
    try:
        result = ping(server.ip_address, timeout=1.5)
        new_status = 'online' if result else 'offline'
        old_status = server.status
        status_changed = (new_status != old_status)

        if status_changed:
            server.status = new_status
            server.last_updated = now
            db.session.add(server)
            db.session.commit()
            logger.info(f"[PING] {server.name} status changed to {new_status}")

        ping_cache[server_id] = (now, new_status)
        return status_changed

    except Exception as e:
        logger.error(f"[ERROR] Ping failed for {server.name}: {e}")
        db.session.rollback()
        return False

def ping_all_servers():
    """Ping all servers and emit updates only if changes occurred."""
    if not _background_app:
        return

    with _background_app.app_context():
        servers = Server.query.all()
        changes_detected = False

        for server in servers:
            if _ping_server(server):
                changes_detected = True

        if changes_detected:
            emit_server_stats()
            logger.info("🔄 Status change detected and emitted.")
        else:
            logger.debug("✅ No status changes; no socket emission.")

def monitor_servers_continuous():
    """Background ping every 60s."""
    global monitoring_thread_started
    monitoring_thread_started = True

    while True:
        ping_all_servers()
        socketio.sleep(60)  # Background check every 60s

def start_background_thread():
    global monitoring_thread_started
    if not monitoring_thread_started:
        socketio.start_background_task(monitor_servers_continuous)
        logger.info("🚀 Background monitoring thread started")

def emit_server_stats():
    """Emit stats to client if there are any updates."""
    total = Server.query.count()
    online = Server.query.filter_by(status='online').count()
    offline = Server.query.filter_by(status='offline').count()
    uptime = round((online / total) * 100, 2) if total else 0

    socketio.emit("server_update", {
        "active_servers": online,
        "critical_alerts": offline,
        "uptime": uptime,
        "total_monitors": total
    })



# def set_background_app(app):
#     global _background_app
#     _background_app = app
#     logger.info("✅ Background app set successfully")
#     print("✅ Background app set successfully")


# monitoring_thread_started = False

# def monitor_servers_continuous():
#     global monitoring_thread_started
#     monitoring_thread_started = True

#     while True:
#         if not _background_app:
#             socketio.sleep(10)
#             continue

#         with _background_app.app_context():
#             servers = Server.query.all()
#             total = len(servers)
#             online = 0
#             offline = 0
#             alerts = 0

#             for server in servers:
#                 try:
#                     result = ping(server.ip_address, timeout=1.5)
#                     server.status = 'online' if result else 'offline'
#                     server.last_updated = datetime.utcnow()
#                     if server.status == 'online':
#                         online += 1
#                     else:
#                         offline += 1
#                         alerts += 1
#                     db.session.add(server)
#                     db.session.commit()
#                 except Exception as e:
#                     db.session.rollback()
#                     alerts += 1
#                     print(f"[ERROR] Monitoring {server.name}: {e}")
                    
#             uptime = round((online / total) * 100, 2) if total > 0 else 0
#             socketio.emit("server_update", {
#                 "active_servers": online,
#                 "uptime": uptime,
#                 "critical_alerts": alerts,
#                 "total_monitors": total
#             })

#         print("[Monitor] Server check complete.")
#         socketio.sleep(10)
        
        
# def emit_server_stats():
#     total_monitors = Server.query.count()
#     active_servers = Server.query.filter_by(status='online').count()
#     critical_alerts = Server.query.filter_by(status='offline').count()
#     uptime = round((active_servers / total_monitors) * 100, 2) if total_monitors else 0

#     socketio.emit('server_update', {
#         'total_monitors': total_monitors,
#         'active_servers': active_servers,
#         'critical_alerts': critical_alerts,
#         'uptime': uptime
#     })


# def start_background_thread():
#     global monitoring_thread_started
#     if not monitoring_thread_started:
#         socketio.start_background_task(monitor_servers_continuous)        




