# Add these routes to your main routes file for testing

from flask import Blueprint, jsonify
from app.models import Server
from app.extensions import db
from datetime import datetime
from ping3 import ping

test_bp = Blueprint('test', __name__)

@test_bp.route('/test_ping/<ip>')
def test_ping(ip):
    """Test ping functionality manually"""
    try:
        result = ping(ip, timeout=3)
        return jsonify({
            'ip': ip,
            'ping_result': result,
            'status': 'online' if result else 'offline',
            'type': str(type(result))
        })
    except Exception as e:
        return jsonify({
            'ip': ip,
            'error': str(e),
            'status': 'error'
        })

@test_bp.route('/test_servers')
def test_servers():
    """Check what servers are in the database"""
    servers = Server.query.all()
    server_list = []
    for server in servers:
        server_list.append({
            'id': server.id,
            'name': server.name,
            'ip_address': server.ip_address,
            'status': server.status,
            'last_updated': server.last_updated.isoformat() if server.last_updated else None
        })
    
    return jsonify({
        'total_servers': len(servers),
        'servers': server_list
    })

@test_bp.route('/test_update_server/<int:server_id>')
def test_update_server(server_id):
    """Manually update a specific server"""
    server = Server.query.get_or_404(server_id)
    
    try:
        # Test ping
        result = ping(server.ip_address, timeout=3)
        
        # Update status
        old_status = server.status
        server.status = 'online' if result else 'offline'
        server.last_updated = datetime.utcnow()
        
        # Save to database
        db.session.add(server)
        db.session.commit()
        
        return jsonify({
            'server_name': server.name,
            'ip_address': server.ip_address,
            'old_status': old_status,
            'new_status': server.status,
            'ping_result': result,
            'last_updated': server.last_updated.isoformat(),
            'success': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': str(e),
            'success': False
        })

@test_bp.route('/force_monitor_cycle')
def force_monitor_cycle():
    """Force one monitoring cycle manually"""
    from app.monitor import _background_app
    
    if not _background_app:
        return jsonify({'error': 'Background app not set'})
    
    results = []
    
    with _background_app.app_context():
        servers = Server.query.all()
        
        for server in servers:
            try:
                # Test ping
                result = ping(server.ip_address, timeout=3)
                
                # Update status
                old_status = server.status
                server.status = 'online' if result else 'offline'
                server.last_updated = datetime.utcnow()
                
                # Save
                db.session.add(server)
                db.session.commit()
                
                results.append({
                    'name': server.name,
                    'ip': server.ip_address,
                    'old_status': old_status,
                    'new_status': server.status,
                    'ping_result': result,
                    'success': True
                })
                
            except Exception as e:
                db.session.rollback()
                results.append({
                    'name': server.name,
                    'ip': server.ip_address,
                    'error': str(e),
                    'success': False
                })
    
    return jsonify({'results': results})

# Don't forget to register this blueprint in your app:
# app.register_blueprint(test_bp, url_prefix='/test')