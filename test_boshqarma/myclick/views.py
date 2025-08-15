from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from . import serializers
from .methods_merchant_api import Services
from .models import ClickTransaction, UserSessionAccess, MonthSession
from .status import (ORDER_FOUND, INVALID_AMOUNT, ORDER_NOT_FOUND)
from .utils import PyClickMerchantAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.models import User
import json
import logging
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class CreateClickTransactionView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ClickTransactionSerializer

    def post(self, request, session_id, *args, **kwargs):
        amount = request.POST.get('amount')

        # session_id = request.POST.get('session_id')
        
        # Ensure we have a valid user
        user_id = request.user.id
            
        if not session_id:
            return JsonResponse({'error': 'Session ID is required'}, status=400)
            
        # Prepare extra_data with user and session information
        extra_data = json.dumps({
            'user_id': user_id,
            'session_id': session_id
        })
        
        # Create transaction record
        order = ClickTransaction.objects.create(
            amount=amount,
            extra_data=extra_data,
            action="session_purchase",
            status=ClickTransaction.WAITING
        )
        
        return_url = "https://www.testtime.uz/dashboard/student"  # Replace with your actual return URL
        url = PyClickMerchantAPIView.generate_url(order_id=order.id, amount=str(amount), return_url=return_url)
        return Response({'url': url}, status=201)


class TransactionCheck(PyClickMerchantAPIView):
    @classmethod
    def check_order(cls, order_id: str, amount: str):
        """
        Verify if order exists and amount is correct
        """
        if order_id:
            try:
                order = ClickTransaction.objects.get(id=order_id)
                # Convert to integers or decimals for comparison based on your requirements
                if int(float(amount)) == int(float(order.amount)):
                    return ORDER_FOUND
                else:
                    return INVALID_AMOUNT
            except ClickTransaction.DoesNotExist:
                return ORDER_NOT_FOUND
        return ORDER_NOT_FOUND

    @classmethod
    def successfully_payment(cls, transaction: ClickTransaction):
        """
        This function is called after successful payment
        Grant access to the purchased session
        """
        # Update transaction status
        transaction.change_status(transaction.CONFIRMED, "Payment confirmed successfully")
        
        # Process the extra_data to get user and session information
        try:
            data = json.loads(transaction.extra_data)
            user_id = data.get('user_id')
            session_id = data.get('session_id')
            
            if not user_id or not session_id:
                transaction.message = "Missing user_id or session_id in transaction data"
                transaction.save(update_fields=["message"])
                logger.error(f"Payment successful but missing user_id or session_id for transaction {transaction.id}")
                return False
                
            # Fetch user and session objects
            try:
                user = User.objects.get(id=user_id)
                session = MonthSession.objects.get(id=session_id)
                
                # Create user session access if it doesn't exist
                access, created = UserSessionAccess.objects.get_or_create(
                    user=user,
                    session=session
                )
                
                if created:
                    logger.info(f"Access granted: User {user.username} now has access to session {session.name}")
                else:
                    logger.info(f"Access already exists: User {user.username} already had access to session {session.name}")
                    
                return True
                
            except User.DoesNotExist:
                transaction.message = f"User with ID {user_id} does not exist"
                transaction.save(update_fields=["message"])
                logger.error(f"Payment successful but user {user_id} not found for transaction {transaction.id}")
                return False
                
            except MonthSession.DoesNotExist:
                transaction.message = f"Session with ID {session_id} does not exist"
                transaction.save(update_fields=["message"])
                logger.error(f"Payment successful but session {session_id} not found for transaction {transaction.id}")
                return False
                
        except json.JSONDecodeError:
            transaction.message = "Invalid extra_data format"
            transaction.save(update_fields=["message"])
            logger.error(f"Payment successful but extra_data is not valid JSON for transaction {transaction.id}")
            return False
            
        except Exception as e:
            transaction.message = f"Error granting access: {str(e)}"
            transaction.save(update_fields=["message"])
            logger.error(f"Unexpected error granting access for transaction {transaction.id}: {str(e)}")
            return False


class ClickTransactionTestView(PyClickMerchantAPIView):
    VALIDATE_CLASS = TransactionCheck


class ClickMerchantServiceView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, service_type, *args, **kwargs):
        service = Services(request.POST, service_type)
        response = service.api()
        return JsonResponse(response)


# Make sure to update the ClickTransaction model if necessary to include extra fields
# But based on your shared model, it already has the necessary fields