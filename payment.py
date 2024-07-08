from abc import ABC, abstractmethod
import requests
import time
from loguru import logger
from utils import generate_payment_reference

class PaymentService(ABC):
    """Abstract base class for Payment Service providers."""

    @abstractmethod
    def initialize_payment(
        self, amount: float, currency: str, customer_email: str, **kwargs
    ) -> dict:
        """
        Initialize a payment transaction.

        Args:
            amount (float): The amount to be paid.
            currency (str): The currency code (e.g., "NGN", "USD").
            customer_email (str): Email of the customer initiating the payment.
            **kwargs: Additional parameters specific to the payment service.

        Returns:
            dict: Response JSON containing transaction details.
        """
        pass

    @abstractmethod
    def verify_payment(self, reference: str) -> dict:
        """
        Verify the status of a payment transaction.

        Args:
            reference (str): Reference identifier for the payment transaction.

        Returns:
            dict: Response JSON containing verification result.
        """
        pass


class KoraPayService(PaymentService):
    """Payment Service implementation for KoraPay."""

    def __init__(self, api_key: str, base_url: str = "https://api.korapay.com/merchant/api/v1/"):
        """
        Initialize KoraPay service with API key and base URL.

        Args:
            api_key (str): API key for KoraPay authentication.
            base_url (str, optional): Base URL for KoraPay API endpoints. Defaults to "https://api.korapay.com/merchant/api/v1/".
        """
        self.api_key = api_key
        self.base_url = base_url

    def initialize_payment(
        self, amount: float, currency: str, customer_email: str, **kwargs
    ) -> dict:
        """
        Initialize a payment transaction with KoraPay.

        Args:
            amount (float): The amount to be paid.
            currency (str): The currency code (e.g., "NGN", "USD").
            customer_email (str): Email of the customer initiating the payment.
            **kwargs: Additional parameters specific to KoraPay.

        Returns:
            dict: Response JSON containing transaction details.
        """
        reference = generate_payment_reference("korapay")
        url = f"{self.base_url}/charges/initialize"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "amount": amount,
            "currency": currency,
            "reference": reference,
            "customer": {"name": "ifeanyi nneji", "email": customer_email},
            **kwargs,
        }

        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def verify_payment(self, reference: str) -> dict:
        """
        Verify the status of a payment transaction with KoraPay.

        Args:
            reference (str): Reference identifier for the payment transaction.

        Returns:
            dict: Response JSON containing verification result.
        """
        # Simulate the dummy verification process
        logger.info(f"Verifying KoraPay payment with reference: {reference}")
        # Dummy processing block
        # e.g., update order status, send confirmation email, etc.
        logger.info("Dummy process after verification for KoraPay")
        return {"status": "success", "reference": reference}


class PaystackService(PaymentService):
    """Payment Service implementation for Paystack."""

    def __init__(self, api_key: str, base_url: str = "https://api.paystack.co/"):
        """
        Initialize Paystack service with API key and base URL.

        Args:
            api_key (str): API key for Paystack authentication.
            base_url (str, optional): Base URL for Paystack API endpoints. Defaults to "https://api.paystack.co/".
        """
        self.api_key = api_key
        self.base_url = base_url

    def initialize_payment(
        self, amount: float, currency: str, customer_email: str, **kwargs
    ) -> dict:
        """
        Initialize a payment transaction with Paystack.

        Args:
            amount (float): The amount to be paid.
            currency (str): The currency code (e.g., "NGN", "USD").
            customer_email (str): Email of the customer initiating the payment.
            **kwargs: Additional parameters specific to Paystack.

        Returns:
            dict: Response JSON containing transaction details.
        """
        reference = generate_payment_reference("paystack")
        url = f"{self.base_url}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "amount": int(amount * 100),  # Paystack requires amount in the smallest currency unit
            "currency": currency,
            "email": customer_email,
            "reference": reference,
            **kwargs,
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def verify_payment(self, reference: str) -> dict:
        """
        Verify the status of a payment transaction with Paystack.

        Args:
            reference (str): Reference identifier for the payment transaction.

        Returns:
            dict: Response JSON containing verification result.
        """
        url = f"{self.base_url}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        while True:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                verification_result = response.json()
                status = verification_result.get('data', {}).get('status')
                logger.info(f"Verifying Paystack payment with reference: {reference}. Status: {status}")
                logger.info(f"Verification Info: {verification_result}")
                if status != 'pending':
                    # Process payment completion (e.g., update order status, send confirmation email)
                    logger.info("Payment verification completed.")
                    return verification_result

                # Wait for 30 seconds before checking again
                time.sleep(30)

            except Exception as e:
                logger.error(f"Error verifying payment for reference {reference}: {str(e)}")
                raise  # Handle or log the error as per your application's error handling strategy


class Payment:
    """Wrapper class for initializing and verifying payments with different services."""

    def __init__(self, service: str, api_key: str):
        """
        Initialize Payment object with the specified service and API key.

        Args:
            service (str): Name of the payment service ('korapay' or 'paystack').
            api_key (str): API key for authentication with the payment service.
        """
        if service == "korapay":
            self.service = KoraPayService(api_key)
        elif service == "paystack":
            self.service = PaystackService(api_key)
        else:
            raise ValueError("Invalid payment service specified")

    def initialize_payment(self, amount: float, currency: str, email: str) -> dict:
        """
        Initialize a payment transaction.

        Args:
            amount (float): The amount to be paid.
            currency (str): The currency code (e.g., "NGN", "USD").
            email (str): Email of the customer initiating the payment.

        Returns:
            dict: Response JSON containing transaction details.
        """
        return self.service.initialize_payment(amount, currency, email)

    def verify_payment(self, reference: str) -> dict:
        """
        Verify the status of a payment transaction.

        Args:
            reference (str): Reference identifier for the payment transaction.

        Returns:
            dict: Response JSON containing verification result.
        """
        return self.service.verify_payment(reference)
