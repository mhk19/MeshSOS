from pickle import TRUE
from backend.settings import SECRET_KEY, TTN_APP_ID, TTN_DOWNLINK_API_KEY, TTN_WEBHOOK_ID
from mainapp.decorator import check_user
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as rf_status

from .models import request_logs, UserProfile
from .serializers import UserProfileSerializer, rlogSerializer

from datetime import datetime
import pytz
import requests
import jwt

def getUserFromJWT(token):
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = UserProfile.objects.get(name=decoded_jwt["username"])
        return UserProfileSerializer(user).data
    except Exception as error:
        print("Error occurred while parsing user token", error)
        return None


class Register(APIView):
    def post(self, request):
        userProfile = UserProfile(name=request.data['name'], password=request.data['password'], email=request.data['email'], service=request.data['service'], location=request.data['location'], phone=request.data['phone'])
        userProfile.save()
        user = UserProfileSerializer(userProfile).data
        token = jwt.encode({"username": userProfile.name, "email": userProfile.email}, SECRET_KEY, algorithm="HS256")
        return Response({"token": token, "user": user})

class Login(APIView):
    def get(self, request):
        user = UserProfile.objects.get(name=request.GET.get('username'), password=request.GET.get('password'))
        if user is not None:
            token = jwt.encode({"username": user.name, "email": user.email}, SECRET_KEY, algorithm="HS256")
            userData = UserProfileSerializer(user).data
            return Response({"token": token, "user": userData})
        else:
            return Response(rf_status.HTTP_404_NOT_FOUND)
        
class User(APIView):
    @check_user
    def get(self, request):
        token = request.headers["Authorization"].split(" ")[1]
        user = getUserFromJWT(token)
        return Response(user)
    
    @check_user
    def post(self, request):
        userProfile = UserProfile.objects.get(name=request.data['username'])
        userProfile.service = request.data['service']
        userProfile.phone = request.data['phone']
        userProfile.location = request.data['location']
        userProfile.save()
        return Response(UserProfileSerializer(userProfile).data)
        

class SendDownlinkMsg(APIView):
    @check_user
    def post(self, request):
        msg = request.data['msg']
        request_id = request.data['request_id']
        print(msg, request_id)
        if request_id:
            log = request_logs.objects.get(id=request_id)
            print(log.core_id)
            dev_id = log.core_id
            url = 'https://eu1.cloud.thethings.network/api/v3/as/applications/' + TTN_APP_ID + '/webhooks/'+ TTN_WEBHOOK_ID +'/devices/' + dev_id + '/down/push'
            headers = {'Authorization' : 'Bearer ' + TTN_DOWNLINK_API_KEY, 'Content-Type': 'application/json', 'User-Agent': 'mesh-sos/v1'}
            requests.post(url, headers=headers, json={"downlinks": [{"decoded_payload":{"message": msg}, "f_port":1}]})
        return Response(TRUE)
        

class rloglist(APIView):
    @check_user
    def get(self, request):
        status = request.GET.get('status')
        emergency_type = request.GET.get('emergency_type')
        id = request.GET.get('id')

        # if status came and was a BAD status
        if status and (not (status=='a' or status=='r' or status=='w')):
            return Response(rf_status.HTTP_400_BAD_REQUEST)

        # PATCH
        if id and status:
            # update status
            log = request_logs.objects.get(id=id)
            log.status = status
            log.save()
            serializer = rlogSerializer(log)
            return Response(serializer.data)


        if (not status) and (not emergency_type):
            rloglist = request_logs.objects.all()
        elif (not status) and (emergency_type):
            rloglist = request_logs.objects.filter(emergency_type = emergency_type)
        elif (status) and (not emergency_type):
            rloglist = request_logs.objects.filter(status=status)
        else:
            rloglist = request_logs.objects.filter(status=status, emergency_type = emergency_type)
            
        serializer = rlogSerializer(rloglist, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        BODY FORMAT:
        
            {
              "timestamp": "{{{PARTICLE_PUBLISHED_AT}}}",
              "emergency": "{{{emergency}}}",
              "latitude": "{{{latitude}}}",
              "longitude": "{{{longitude}}}",
              "accuracy": "{{{accuracy}}}"
            }
        """

        # dictionary of recieved data body
        req_data = request.data['uplink_message']['decoded_payload']
        dev_id = request.data['end_device_ids']['device_id']
        
        url = 'https://eu1.cloud.thethings.network/api/v3/as/applications/' + TTN_APP_ID + '/webhooks/'+ TTN_WEBHOOK_ID +'/devices/' + dev_id + '/down/push'
        headers = {'Authorization' : 'Bearer ' + TTN_DOWNLINK_API_KEY, 'Content-Type': 'application/json', 'User-Agent': 'mesh-sos/v1'}

        # update timestamp to use indian time (UTC -> Asia/Kolkata)
        utc_datetime = datetime.strptime(req_data["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
        utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)

        db_datetime_format = "%Y-%m-%d %H:%M:%S"

        req_data['timestamp']=utc_datetime.strftime(db_datetime_format)
        req_data["core_id"] = dev_id

        # serialize data to save in db
        print("Parsed data:\n", req_data)
        serializer = rlogSerializer(data=req_data)

        # should the log in POST be saved or not (this is only default value, manipulated in code below)
        should_save_logs = True

        # return_val
        if (
            req_data["latitude"] == "-1"
            or req_data["longitude"] == "-1"
            or req_data["accuracy"] == "-1"
        ):
            should_save_logs &= False
            return_val = "/0"
        else:
            return_val = "/1"

        # checking for validity of data
        if serializer.is_valid(raise_exception=True):
            # check for previous log
            query_set = request_logs.objects.filter(
                emergency_type = req_data['emergency_type'],
                core_id = req_data['core_id'],
                status='a',
            )

            if query_set.exists() :
                for log in query_set:
                    log_datetime = datetime.strptime(log.timestamp, '%Y-%m-%d %H:%M:%S')
                    log_datetime = log_datetime.replace(tzinfo=pytz.utc)

                    if isDifLessThanFiveMinutes(utc_datetime, log_datetime) :
                        should_save_logs &= False
                        break
            
            # saving log
            if should_save_logs:
                print("Saving Log")
                saved_obj = serializer.save()
            else :
                print("Not Saving Log")
        # requests.post(url, headers=headers, json={"downlinks": [{"decoded_payload":{"received": 'true'}, "f_port":1}]})
        return Response(return_val,)

def isDifLessThanFiveMinutes(later, before):
    diff = later - before
    seconds_in_day = 24 * 60 * 60
    secs = diff.days * seconds_in_day + diff.seconds
    return  (secs < 300)
