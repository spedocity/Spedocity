from .models import Customer
from django.contrib.sessions.models import Session
from django.utils.crypto import constant_time_compare
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def customer_profile(request):
    # Retrieve customer information from session
    customer_id = request.session.get('customer_id')
    phone_number = request.session.get('phone_number')
    first_name = request.session.get('first_name')

    # Log session details for debugging
    logger.debug(f"Session data - customer_id: {customer_id}, phone_number: {phone_number}, first_name: {first_name}")

    # Check if session data exists
    if not (customer_id and phone_number and first_name):
        logger.debug("Session data is incomplete or missing.")
        return {}

    # Validate the session
    try:
        session_key = request.session.session_key
        if not session_key:
            logger.debug("Session key is missing.")
            return {}

        session = Session.objects.get(session_key=session_key)
        if session.expire_date <= timezone.now():
            logger.debug("Session has expired.")
            return {}

    except Session.DoesNotExist:
        logger.debug("Session does not exist in the database.")
        return {}

    # Fetch the customer from the database based on session data
    try:
        customer = Customer.objects.get(
            id=customer_id,
            phone_number=phone_number,
            first_name=first_name
        )
        logger.debug(f"Customer found: {customer}")
        return {'customer': customer}

    except Customer.DoesNotExist:
        logger.debug("Customer not found in the database.")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {}