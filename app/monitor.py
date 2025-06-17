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
_monitor_thread = None
_thread_running = False
logger = logging.getLogger(__name__)

def set_background_app(app):
    global _background_app
    _background_app = app
    logger.info("✅ Background app set successfully")
    print("✅ Background app set successfully")





monitoring_thread_started = False

def monitor_servers_continuous():
    global monitoring_thread_started
    monitoring_thread_started = True

    while True:
        if not _background_app:
            socketio.sleep(5)
            continue

        with _background_app.app_context():
            servers = Server.query.all()
            total = len(servers)
            online = 0
            offline = 0
            alerts = 0

            for server in servers:
                try:
                    result = ping(server.ip_address, timeout=3)
                    server.status = 'online' if result else 'offline'
                    server.last_updated = datetime.utcnow()
                    if server.status == 'online':
                        online += 1
                    else:
                        offline += 1
                        alerts += 1
                    db.session.add(server)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    alerts += 1
                    print(f"[ERROR] Monitoring {server.name}: {e}")
                    
            uptime = round((online / total) * 100, 2) if total > 0 else 0
            socketio.emit("server_update", {
                "active_servers": online,
                "uptime": uptime,
                "critical_alerts": alerts,
                "total_monitors": total
            })

        print("[Monitor] Server check complete.")
        socketio.sleep(5)


def start_background_thread():
    global monitoring_thread_started
    if not monitoring_thread_started:
        socketio.start_background_task(monitor_servers_continuous)        




