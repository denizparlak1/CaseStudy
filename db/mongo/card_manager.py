import datetime
import random
from db.mongo.config.mongo import Mongo


class CardManager:
    @staticmethod
    def log_transaction(user_no, card_no, amount, transaction_type):
        mongo = Mongo().get_db()
        log_data = {
            "userNo": user_no,
            "cardNo": card_no,
            "amount": amount,
            "transactionType": transaction_type,
            "transactionDate": datetime.datetime.now()
        }
        mongo.transaction_logs.insert_one(log_data)

    @staticmethod
    def generate_card_info():
        card_no = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        expiry_month = str(random.randint(1, 12)).zfill(2)
        expiry_year = str(random.randint(22, 30)).zfill(2)
        cvc = ''.join([str(random.randint(0, 9)) for _ in range(3)])

        return {
            "cardNo": card_no,
            "expiryMonth": expiry_month,
            "expiryYear": expiry_year,
            "cvc": cvc
        }

    @classmethod
    def add_card_to_user(cls, user_no, card_info):
        mongo = Mongo().get_db()
        user = mongo.case.find_one({"userNo": user_no})

        if not user:
            raise ValueError("Kullanıcı bulunamadı!")

        if not user["selectedCard"]:
            mongo.case.update_one({"userNo": user_no}, {
                "$set": {"selectedCard": card_info["cardNo"]},
                "$push": {"allCards": card_info}
            })
        else:
            mongo.case.update_one({"userNo": user_no}, {
                "$push": {"allCards": card_info}
            })

        print(f"{user_no} numaralı kullanıcıya kart bilgisi eklendi!")

    @classmethod
    def withdraw_from_card(cls, user_no, amount):
        mongo = Mongo().get_db()
        user = mongo.case.find_one({"userNo": user_no})

        if not user:
            raise ValueError("Kullanıcı bulunamadı!")

        if not user["selectedCard"]:
            raise ValueError("Kullanıcının kayıtlı bir kredi kartı yok!")

        # Kullanıcının seçili kartının detaylarını bul
        selected_card_details = None
        for card in user["allCards"]:
            if card["cardNo"] == user["selectedCard"]:
                selected_card_details = card
                break

        if not selected_card_details:
            raise ValueError("Seçili kartın detayları bulunamadı!")

        # TODO: Burada dış servise kredi kartı bilgileri ile birlikte para çekme isteği gönderilebilir.
        # Örnek: external_service.withdraw(selected_card_details, amount)

        # Bakiyeyi güncelle
        new_balance = user["balance"] + amount
        mongo.case.update_one({"userNo": user_no}, {"$set": {"balance": new_balance}})

        cls.log_transaction(user_no, user["selectedCard"], amount, "purchase")

        return new_balance

    @classmethod
    def refund_to_card(cls, user_no, amount):
        mongo = Mongo().get_db()
        user = mongo.case.find_one({"userNo": user_no})

        if not user:
            raise ValueError("Kullanıcı bulunamadı!")

        if not user["selectedCard"]:
            raise ValueError("Kullanıcının kayıtlı bir kartı yok!")

        new_balance = user["balance"] - amount
        if new_balance < 0:
            raise ValueError("Yetersiz bakiye!")

        mongo.case.update_one({"userNo": user_no}, {"$set": {"balance": new_balance}})

        cls.log_transaction(user_no, user["selectedCard"], amount, "refund")

        return new_balance

    @classmethod
    def get_all_cards(cls, user_no):
        mongo = Mongo().get_db()
        user = mongo.case.find_one({"userNo": user_no})

        if not user:
            raise ValueError("Kullanıcı bulunamadı!")

        return user.get("allCards", [])
