from flask import Blueprint

from app.controllers.auth_controller import login, logout, usuario_autenticado

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

auth_bp.route('/login', methods=['POST'])(login)
auth_bp.route('/logout', methods=['POST'])(logout)
auth_bp.route('/me', methods=['GET'])(usuario_autenticado)