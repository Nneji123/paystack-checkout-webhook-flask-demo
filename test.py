from payment import PaystackService
from dotenv import load_dotenv
import os

load_dotenv()


# Paystack example:
api_key_paystack = os.getenv("PAYSTACK_SECRET_KEY")
paystack_service = PaystackService(api_key_paystack)
response = paystack_service.initialize_payment(amount=2000, customer_email="chidi@gmail.com", currency="NGN")
print(response)
