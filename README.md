Here's an updated `README.md` file that includes instructions for running the `test.py` script to initiate a payment and obtain the authorization URL, access code, and reference from Paystack:

---

# Paystack Integration with Flask Server

This repository demonstrates how to integrate Paystack payments with a Flask server, including setting up environment variables and using Ngrok for local testing.

## Setup

### Environment Variables

1. **Create a `.env` File**:
   Create a `.env` file in the root directory of your project. This file will store sensitive credentials and configuration variables.

2. **Add Paystack API Keys**:
   Obtain your Paystack API keys from your Paystack dashboard:
   ```plaintext
   PAYSTACK_PUBLIC_KEY=your_public_key_here
   PAYSTACK_SECRET_KEY=your_secret_key_here
   ```
   Replace `your_public_key_here` and `your_secret_key_here` with your actual Paystack API keys.

3. **Optional**: Add other environment variables as needed for your application.

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your_username/paystack-flask-demo.git
   cd paystack-flask-demo
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Flask Server Locally

1. **Run Flask App**:
   Start the Flask server locally:
   ```bash
   python webhook.py
   ```

2. **Expose Local Server with Ngrok**:
   - Download and install Ngrok from [Ngrok's official website](https://ngrok.com/download).
   - Run Ngrok to expose your local server to the internet:
     ```bash
     ngrok http 5000  # Replace 5000 with your Flask app port if different
     ```
   - Copy the Ngrok URL (`https://abcdef123456.ngrok.io`).

### Testing Paystack Integration

1. **Initiate Payment**:
   - Use the `test.py` script to initiate a payment and obtain the authorization URL, access code, and reference from Paystack:
     ```bash
     python test.py
     ```
     Output:
     ```plaintext
     {'status': True, 'message': 'Authorization URL created', 'data': {'authorization_url': 'https://checkout.paystack.com/0n1aogf0wrvgerd', 'access_code': '0n1aogf0wrvgerd', 'reference': 'PAYSTACK-20240708080509-h8AdWxgHsNxEFNKBJJM27j'}}
     ```

2. **Configure Paystack Webhook**:
   - Log in to your Paystack dashboard.
   - Navigate to `Settings` > `Webhooks`.
   - Add the Ngrok URL (`https://abcdef123456.ngrok.io/webhook`) as your webhook URL.

3. **Perform Test Transactions**:
   - Use Paystack's test mode to perform transactions.
   - Check the console output of your Flask app for logs generated by the webhook endpoint (`/webhook`).

## Endpoints

- **GET `/`**: Displays a simple message confirming that the Flask server is running.
- **POST `/webhook`**: Endpoint to receive Paystack webhook events. Logs events to console using Loguru.

## Troubleshooting

- Ensure all environment variables are correctly set in the `.env` file.
- Verify Ngrok is correctly tunneling to your local Flask server (`ngrok http 5000`).
