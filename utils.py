from datetime import datetime
import shortuuid

def generate_payment_reference(payment_type: str) -> str:
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = shortuuid.uuid()
    return f"{payment_type.upper()}-{current_datetime}-{unique_id}"
