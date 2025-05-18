from rest_framework import generics, status
from rest_framework.response import Response
from django.db import transaction
from sms.models import SendHistory
from sms.permissions import IsAdminOrAuthenticated
from sms.serializers import SendSmsSerializer
from sms.services.sms import SmsService


class SmsAPIView(generics.ListCreateAPIView):
    serializer_class = SendSmsSerializer
    permission_classes = (IsAdminOrAuthenticated,)

    def create(self, request, *args, **kwargs):
        # 1. Validate incoming data
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # 2. Balance check
            if request.user.sms_balance <= 0:
                return Response({
                    "success": False,
                    "message": "Insufficient balance to send the SMS.",
                }, status=status.HTTP_400_BAD_REQUEST)

            # 3. Perform send + history inside a transaction
            number = serializer.validated_data['number']
            text   = serializer.validated_data['text']
            try:
                with transaction.atomic():
                    response_data = SmsService.send_sms(number, text)
                    SendHistory.objects.create(  # noqa
                        user=request.user,
                        number=number,
                        text=text
                    )
            except Exception as e:
                transaction.set_rollback(True)
                return Response({
                    "success": False,
                    "message": f"Error sending SMS: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # 4. Return success
            return Response({
                "success": True,
                "message": "SMS muvaffaqiyatli yuborildi.",
                "data": response_data
            }, status=status.HTTP_201_CREATED)

        # If serializer is not valid, return custom error messages with form values
        error_messages = serializer.errors
        return Response({
            "success": False,
            "message": "Validation failed.",
            "errors": error_messages,
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        sms_data = SmsService.get_sms()
        sms_data = self.normalize_sms_data(sms_data)

        return Response({
            "success": True,
            "message": "SMS data retrieved successfully.",
            "data": sms_data
        })

    def normalize_sms_data(self, sms_data):
        if sms_data.get("ok") and "result" in sms_data:
            for sms in sms_data["result"]:
                if "holat" in sms:
                    sms["holat"] = 1 - int(sms["holat"])
                if "raqam" in sms:
                    try:
                        sms["raqam"] = int(sms["raqam"])
                    except ValueError:
                        sms["raqam"] = 0
        return sms_data
