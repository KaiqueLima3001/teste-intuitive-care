from flask import Blueprint, request, jsonify
from api.services.operadoras_service import listar_operadoras, obter_operadora_por_cnpj
from api.services.despesas_service import listar_despesas_por_operadora

operadoras_bp = Blueprint("operadoras", __name__)

@operadoras_bp.route("/", methods=["GET"])
def get_operadoras():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        search = request.args.get("search", "")

        resultado = listar_operadoras(page, limit, search)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ROTA POR CNPJ 
@operadoras_bp.route("/<cnpj>", methods=["GET"])
def get_operadora_por_cnpj(cnpj):
    try:
        operadora = obter_operadora_por_cnpj(cnpj)
        if not operadora:
            return jsonify({'message': 'Operadora não encontrada'}), 404
        return jsonify(operadora)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ROTA DE DESPESAS
@operadoras_bp.route("/<cnpj>/despesas", methods=["GET"])
def get_despesas_operadora(cnpj):
    despesas = listar_despesas_por_operadora(cnpj)
    return jsonify(despesas)