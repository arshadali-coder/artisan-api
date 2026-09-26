import uuid
from datetime import datetime
from typing import Dict, Any

class PaymentService:
    @staticmethod
    def process_payout_to_artisan(artisan_id: str, amount: float) -> Dict[str, Any]:
        """
        Simulates direct bank payout transfer using RazorpayX / Cashfree Payout API.
        """
        payout_ref = f"PAY_{uuid.uuid4().hex[:10].upper()}"
        return {
            "payout_id": payout_ref,
            "status": "COMPLETED",
            "amount": amount,
            "message": f"Successfully processed direct bank transfer of ₹{amount} to artisan.",
            "timestamp": datetime.utcnow().isoformat()
        }
