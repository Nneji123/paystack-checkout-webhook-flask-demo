from flask import Flask, request, jsonify
import hashlib
import hmac
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

app = Flask(__name__)

SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

# Initialize PaystackService
from payment import PaystackService

paystack_service = PaystackService(api_key=SECRET_KEY)

@app.route("/", methods=["GET"])
def home():
    return "Flask Server Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    logger.info("Received webhook data: {}", data)

    # Validate event signature
    signature = request.headers.get('x-paystack-signature')
    if not signature:
        logger.warning("Missing Paystack signature in headers")
        return jsonify({'status': 'error', 'message': 'Missing Paystack signature'}), 400

    expected_signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        request.data,
        hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        logger.warning("Invalid Paystack signature")
        return jsonify({'status': 'error', 'message': 'Invalid Paystack signature'}), 400

    # Example: Process specific Paystack events
    event_type = data.get('event')
    if event_type == 'charge.success':
        payment_data = data.get('data')
        payment_id = payment_data.get('id')
        amount = payment_data.get('amount')
        currency = payment_data.get('currency')
        status = payment_data.get('status')
        logger.info(f"Received successful payment {payment_id} of {amount} {currency}. Status: {status}")
        return jsonify({'status': 'success'}), 200

    else:
        logger.warning("Received unknown event type: {}", event_type)
        return jsonify({'status': 'ignored'}), 200

@app.route('/verify_payment/<reference>', methods=['GET'])
def verify_payment(reference):
    try:
        verification_result = paystack_service.verify_payment(reference)
        status = verification_result.get('data', {}).get('status')
        logger.info(status)
        message = verification_result.get('message', 'Verification successful')
        if status and status != 'pending':
            # Process completion (e.g., update order status, send confirmation email)
            logger.info("Payment verification completed.")
            return jsonify({'status_of_payment': status, 'message': message}), 200
        else:
            # Payment still pending, return status
            logger.info("Payment still pending.")
            return jsonify({'status': 'pending', 'message': message}), 200

    except Exception as e:
        logger.error(f"Error verifying payment for reference {reference}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
