from flask import Blueprint, jsonify, request

from db.mongo.card_manager import CardManager

payment = Blueprint('payment', __name__)


@payment.route('/add-card', methods=['POST'])
def add_card():
    card_info = request.json

    authorization = request.headers.get('Authorization')
    filo = request.headers.get('Filo')
    user_no = request.headers.get('UserNo')

    if not all([authorization, filo, user_no]):
        return jsonify({"error": "Header bilgileri eksik."}), 400

    required_fields = ["cardNo", "expiryMonth", "expiryYear", "cvc"]
    if not all(field in card_info for field in required_fields):
        return jsonify({"error": "Kart bilgisi eksik veya hatalı."}), 400

    try:
        CardManager.add_card_to_user(user_no, card_info)
        return jsonify({"message": f"{user_no} numaralı kullanıcıya kart bilgisi eklendi!"}), 200
    except ValueError as ve:  # ValueError hatasını yakala
        if str(ve) == "Kullanıcı bulunamadı!":
            return jsonify({"error": "Kullanıcı bulunamadı!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment.route('/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    amount = data.get("amount")

    # Header'dan gerekli bilgileri al
    authorization = request.headers.get('Authorization')
    filo = request.headers.get('Filo')
    user_no = request.headers.get('UserNo')

    # Eğer header'da belirtilen bilgiler eksikse hata döndür
    if not all([authorization, filo, user_no]):
        return jsonify({"error": "Header bilgileri eksik."}), 400

    if not amount or amount <= 0:
        return jsonify({"error": "Geçersiz miktar."}), 400

    try:
        new_balance = CardManager.withdraw_from_card(user_no, amount)
        return jsonify({
                           "message": f"{user_no} numaralı kullanıcıdan {amount} miktarında para çekildi. Yeni bakiye: {new_balance}"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment.route('/refund', methods=['POST'])
def refund():
    amount = request.json.get("amount")

    authorization = request.headers.get('Authorization')
    filo = request.headers.get('Filo')
    user_no = request.headers.get('UserNo')

    if not all([authorization, filo, user_no]):
        return jsonify({"error": "Header bilgileri eksik."}), 400

    try:
        new_balance = CardManager.refund_to_card(user_no, amount)
        return jsonify({"message": f"{user_no} numaralı kullanıcının yeni bakiyesi: {new_balance}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment.route('/get-all-cards', methods=['POST'])
def get_all_cards():
    authorization = request.headers.get('Authorization')
    filo = request.headers.get('Filo')
    user_no = request.headers.get('UserNo')

    if not all([authorization, filo, user_no]):
        return jsonify({"error": "Header bilgileri eksik."}), 400

    try:
        cards = CardManager.get_all_cards(user_no)
        return jsonify({"cards": cards}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
