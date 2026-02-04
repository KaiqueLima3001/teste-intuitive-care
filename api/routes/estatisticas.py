from flask import Blueprint, jsonify
from api.services.estatisticas_service import obter_estatisticas_gerais

estatisticas_bp = Blueprint("estatisticas", __name__)

@estatisticas_bp.route('/', methods=['GET'])
def get_estatisticas():
    try:
        dados = obter_estatisticas_gerais()
        return jsonify(dados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@estatisticas_bp.route("/estatisticas/despesas-por-uf", methods=["GET"])
def grafico_uf():
    return jsonify(obter_estatisticas_gerais()["despesas_por_uf"])
