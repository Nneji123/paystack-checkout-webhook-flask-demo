from abc import ABC, abstractmethod
import requests
import time
from loguru import logger
from utils import generate_payment_reference

class PaymentService(ABC):
    @abstractmethod
    def initialize_payment(
        self, amount: float, currency: str, customer_email: str, metadata, **kwargs
    ):
        pass

    @abstractmethod
    def verify_payment(self, reference: str):
        pass


class KoraPayService(PaymentService):
    def __init__(self, api_key: str = os.environ.get("KORAPAY_SECRET_KEY")):
        self.api_key = api_key

    def initialize_payment(
        self, amount: float, currency: str, customer_email: str, metadata, **kwargs
    ):
        reference = generate_payment_reference("korapay")
        url = "https://api.korapay.com/merchant/api/v1/charges/initialize"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "amount": amount,
            "currency": currency,
            "reference": reference,
            "customer": {
                "name": kwargs.get("customer_name", "Anonymous"),
                "email": customer_email,
            },
            "metadata": metadata,
        }

        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def verify_payment(self, reference: str):
        url = f"{self.base_url}/charges/{reference}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data["status"]:
                return {
                    "status": data["data"]["status"],
                    "reference": data["data"]["reference"],
                    "amount": data["data"]["amount"],
                    "amount_paid": data["data"]["amount_paid"],
                    "currency": data["data"]["currency"],
                    "fee": data["data"]["fee"],
                    "description": data["data"].get("description", ""),
                    "payer_bank_account": data["data"].get("payer_bank_account", {}),
                }
            else:
                return {"status": "error", "message": data["message"]}
        else:
            return {"status": "error", "message": "Failed to verify payment"}


class PaystackService(PaymentService):
    def __init__(self, api_key: str = os.environ.get("PAYSTACK_SECRET_KEY")):
        self.api_key = api_key

    def initialize_payment(
        self,
        amount: float,
        currency: str,
        customer_email: str,
        metadata: dict,
        **kwargs,
    ):
        reference = generate_payment_reference("paystack")
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "amount": int(
                amount * 100
            ),  # Paystack requires amount in the smallest currency unit
            "currency": currency,
            "email": customer_email,
            "reference": reference,
            "metadata": metadata,
        }
        logger.info(data)
        response = requests.post(url, json=data, headers=headers)
        logger.info(response)
        response.raise_for_status()
        return response.json()

    def verify_payment(self, reference: str):
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data["status"]:
                return {
                    "status": data["data"]["status"],
                    "reference": data["data"]["reference"],
                    "amount": data["data"]["amount"] / 100,  # Convert back to float
                    "currency": data["data"]["currency"],
                    "fee": data["data"]["fees"],
                    "channel": data["data"]["channel"],
                    "paid_at": data["data"]["paid_at"],
                    "customer": {
                        "id": data["data"]["customer"]["id"],
                        "email": data["data"]["customer"]["email"],
                        "customer_code": data["data"]["customer"]["customer_code"],
                    },
                    "authorization": {
                        "authorization_code": data["data"]["authorization"][
                            "authorization_code"
                        ],
                        "card_type": data["data"]["authorization"]["card_type"],
                        "bank": data["data"]["authorization"]["bank"],
                        "country_code": data["data"]["authorization"]["country_code"],
                    },
                }
            else:
                return {"status": "error", "message": data["message"]}
        else:
            return {"status": "error", "message": "Failed to verify payment"}


class Payment:
    def __init__(self, service: str, api_key: str):
        if service == "korapay":
            self.service = KoraPayService(api_key)
        elif service == "paystack":
            self.service = PaystackService(api_key)
        else:
            raise ValueError("Invalid payment service specified")

    def initialize_payment(self, amount, currency, email, metadata, **kwargs):
        return self.service.initialize_payment(
            amount, currency, email, metadata, **kwargs
        )

    def verify_payment(self, reference):
        return self.service.verify_payment(reference)
