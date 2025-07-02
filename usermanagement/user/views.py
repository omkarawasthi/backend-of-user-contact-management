from user.celery_task import scheduled_log_deletion, send_upcoming_birthday_reminder
from .utils.helper_functions import find_birthday_next_week
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils.db_logging import log_in_db
from .services.user_services import *
from rest_framework import status
from dotenv import load_dotenv

load_dotenv()

class RegisterAPIView(APIView):
    
    def post(self,request):
        try:
           image = request.FILES.get("image")
           response, statuscode = register_user(request.data,image)
           return Response({**response}, status=statuscode)
        except Exception as e:
            log_in_db("Error", "CREATE", "User", {"message": "Something went wrong.", "error": str(e)})
            return Response({"success":False,"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginAPIView(APIView):
    def post(self, request):
        try:
            response, statuscode = login_user(request.data)
            return Response({**response}, status=statuscode)

        except Exception as e:
            log_in_db("Error", "LOGIN", "User", {"message": "Something went wrong.", "error": str(e)})
            return Response({"success":False,"message": "Something went wrong.", "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# This view is to get the data of Particular user using {id}.
class UserDetailedAPIView(APIView):
    def get(self, request, id):
        try:
            response, statuscode = get_user_by_id(id)
            return Response({**response}, status=statuscode)
        except Exception as e:
            return Response({"success": False, "message": "Something went wrong.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            response, statuscode = get_all_users()
            return Response({**response}, status=statuscode)
        except Exception as e:
            return Response({"success": False, "message": "Something went wrong.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            response, statuscode = delete_user_by_id(id)
            return Response({**response}, status=statuscode)
        except Exception as e:
            log_in_db("Error", "DELETE", "User", {"message": "Something went wrong.", "error": str(e)})
            return Response({"success": False, "message": "Something went Wrong.", "error": str(e)}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, id):
        try:
            response, statuscode = update_user_and_contact(id, request.data)
            return Response({**response}, status=statuscode)
        except Exception as e:
            log_in_db("Error", "UPDATE", "User", {"message": "Something went wrong.", "error": str(e)})
            return Response({"success": False, "message": "Something went wrong.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogDeletionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request,id):
        try:
            scheduled_log_deletion.delay(int(id))  # type: ignore

            return Response({
                "status":True,
                "message": f"Log deletion task for logs older than {id} hours scheduled.",
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class SearchUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            filters = request.query_params
            # print("filters are :", filters)
            response = search_users(filters)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False,"message": "Something went wrong.","error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class BirthdayAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,id):
        try:
            print("id is :",id)
            response = find_birthday_next_week(id)
            print(response)
            return Response(response,status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"success": False,"message": "Something went wrong.","error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SendingEmailToAllView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        try:
            send_upcoming_birthday_reminder()
            return Response({"status":True,"message":"send reminders successfully"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False,"message": "Something went wrong.","error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)