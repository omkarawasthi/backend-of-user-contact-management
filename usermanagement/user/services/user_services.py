from ..serializers import UserSerializer, ContactSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from ..utils.db_logging import log_in_db
from rest_framework import serializers
from django.core.cache import cache
from ..models import User, Contact
from rest_framework import status
from dotenv import load_dotenv
from django.db.models import Q
import json

load_dotenv()


def register_user(data, image=None):
    # print("data is :",data)
    first_name  = data["first_name"]
    last_name = data["last_name"]
    email       = data["email"]
    password    = data["password"]
    phone_no = data["phone_no"]
    aadhar_no = data["aadhar_no"]
    date_of_birth = data["date_of_birth"]
    username = data["username"]
    image = data.get("image")


    # If any field is missing then return all field requireds.
    if not all([first_name, last_name, email, password, phone_no, date_of_birth, aadhar_no, username]):
        log_in_db("User Form Error", "CREATE", "User", {"message": "All fields are required."})
        return {"success":False,"message": "All fields are required."},status.HTTP_400_BAD_REQUEST

    
    validate_email = UserSerializer().validate_email(email)# type: ignore

    print("yaha aa rha hia")
    if not validate_email:
        log_in_db("ERROR", "CREATE", "User", {"message": "Please write correct format of Email."})
        print("yaha ja rha hai na")
        return {"success":False,"message": "Please write correct format of Email."}, status.HTTP_400_BAD_REQUEST
    

    validate_phone = ContactSerializer().validate_phone_no(phone_no)# type: ignore

    if not validate_phone:
        log_in_db("ERROR", "CREATE", "User", {"message": "Please write correct format of Phone no."})
        print("yaha ja rha hai na")
        return {"success":False, "message": "Please write correct format of Phone no."}, status.HTTP_400_BAD_REQUEST


    #if email already exits then send that email already exits.
    if User.objects.filter(email=email).exists():
        log_in_db("ERROR", "CREATE", "User", {"message": "Email already registered."})
        return {"success":False,"error": "Email already registered."}, status.HTTP_400_BAD_REQUEST
    

    # Find user using email.
    user = User.objects.filter(email=email)
    
    
    # make user data to send to Contact model.
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "username":data["username"],
        "password": password
    }


    # make contact data to send to Contact model.
    contact_data = {
        "first_name": first_name,
        "last_name": last_name,
        "phone_no": phone_no,
        "aadhar_no": aadhar_no,
        "date_of_birth": date_of_birth,
        "image":image,
    }
    
    #convert data to db object to insert into db.
    user_serializer = UserSerializer(data=user_data)
    
    # check if data insert correctly then save the user.
    if user_serializer.is_valid():
        user = user_serializer.save()
    else:
        log_in_db("Validation Error", "CREATE", "User", {"Error": user_serializer.errors})
        return {"success": False, "errors": user_serializer.errors}, status.HTTP_400_BAD_REQUEST
    
    contact_data['user'] = user.id# type: ignore
    contact_serializer = ContactSerializer(data=contact_data)
    
    # now we send user data to frontend so remove password field from it for security.
    # del user_data["password"]

    if contact_serializer.is_valid():
        contact_serializer.save(user=user)
        
        data_send = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username":data["username"],
            "phone_no": phone_no,
            "aadhar_no": aadhar_no,
            "date_of_birth": date_of_birth
        }
        
        
        # log_in_db("INFO", "CREATE", "User", {"message": "User created successfully.","User":user_data})

        return {"success":True,"message": "User created successfully.","User":data_send},status.HTTP_201_CREATED
    
    else:
        log_in_db("Validation Error", "CREATE", "User", {"Error": contact_serializer.errors})
        return {"success": False, "errors": contact_serializer.errors},status.HTTP_400_BAD_REQUEST


def login_user(data):
    email = data.get("email")
    password = data.get("password")

    # if any field is missing give error
    if not all([email, password]):
        log_in_db("ERROR", "LOGIN", "User", {"message": "Email and password are required."})
        return {"success":False,"message": "Email and password are required."}, status.HTTP_400_BAD_REQUEST

    try:
        # if email field is not valid then we return from here. 
        email = UserSerializer().validate_email(email)# type: ignore
    except serializers.ValidationError as e:
        log_in_db("ERROR", "LOGIN", "User", {"message": "Invalid email format."})
        return {"success": False, "message": "Invalid email format."}, status.HTTP_400_BAD_REQUEST
    

    # find User using email 
    user = User.objects.get(email=email)
    contact = Contact.objects.get(user_id = user.id)
    
    # print(user.email)

    
    # If user not exits then return user not exists or invalid credential
    if not User.DoesNotExist:
        log_in_db("ERROR", "LOGIN", "User",{"message":"User with this email does not exist."})
        return {"success": False, "message": "Invalid credentials or User doesn't exist."}, status.HTTP_400_BAD_REQUEST
    
    # now match the password given by user with the stored userd password.
    if not user.check_password(password):
        log_in_db("ERROR", "LOGIN", "User", {"message": "Invalid credentials(password)."})
        return {"success":False,"message": "Invalid credentials (email/password)."}, status.HTTP_400_BAD_REQUEST

    # if everthing goes write convert the object and set to payload to find jwt token
    user_serializer = UserSerializer(user)
    contact_serializer = ContactSerializer(contact)


    # print(type(user_serializer.data))
    user_data = user_serializer.data
    # print(data.get('first_name'))
    contact_data = contact_serializer.data
    # print(contact_data)

    data_send = {}
    data_send['first_name'] = user_data.get('first_name') # type: ignore
    data_send['last_name'] = user_data.get('last_name') # type: ignore
    data_send['email'] = user_data.get('email') # type: ignore
    data_send['user_id'] = contact_data.get('id') # type: ignore
    data_send['phone_no'] = contact_data.get('phone_no')# type: ignore
    data_send['aadhar_no'] = contact_data.get('aadhar_no')# type: ignore
    data_send['date_of_birth'] = contact_data.get('date_of_birth')# type: ignore



    # payload = serializer.data.copy()
    # payload['exp'] = (datetime.now() + timedelta(minutes=15)).isoformat()
    
    # # function to get jwt token.
    # token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm=os.getenv('JWT_ALGORITHM'))

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    log_in_db("INFO", "LOGIN", "User", {"message": "User Login Successfully"})
    return {"success":True,"accessToken": access_token, "user": data_send}, status.HTTP_200_OK



def get_all_users():
    # finding users from redis database cache memory
    cached_users = cache.get("all_users")

    # if found return response of user found from cache, if you want to tell otherwise no need. 
    if cached_users:
        print("Retrieved users from cache")
        return {
            "success": True,
            "message": "Users retrieved from cache.",
            "users": json.loads(cached_users)
        }, status.HTTP_200_OK

    # if not in cache then fetch from the database.
    users = User.objects.all()
    contacts = Contact.objects.select_related("user").all()

    
    user_data = UserSerializer(users, many=True).data
    contact_data = ContactSerializer(contacts, many=True).data

    # Build contact map using user ID
    contact_map = {contact["user"]: contact for contact in contact_data}

    combined_data = []

    for user in user_data:
        contact = contact_map.get(user["id"])
        if contact:
            combined_data.append({
                "user_id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "username": user["username"],
                "phone_no": contact["phone_no"],
                "aadhar_no": contact["aadhar_no"],
                "date_of_birth": contact["date_of_birth"],
                "image_url": contact.get("image")  # Cloudinary image URL
            })

    # Cache and return
    cache.set("all_users", json.dumps(combined_data), timeout=60 * 60)

    return {
        "success": True,
        "message": "Users retrieved from database.",
        "users": combined_data
    }, status.HTTP_200_OK

def get_user_by_id(user_id):
    # finding user from redis database cache memory
    cache_key = f"user_{user_id}"
    cached_user = cache.get(cache_key)
    # cache.delete(f"user_{user_id}")
    # r.delete('your_cache_key')

    # if found return response of user found from cache, if you want to tell otherwise no need. 
    if cached_user:
        print(f"Retrieved user from cache")
        return {
            "success": True,
            "message": f"User retrieved from cache.",
            "user": json.loads(cached_user)
        }, status.HTTP_200_OK

    # if not in cache then fetch from the database.
    user = get_object_or_404(User, id=user_id)
    contact = get_object_or_404(Contact, id = user_id)

    user_serializer = UserSerializer(user)
    user_data = user_serializer.data
    
    contact_serializer = ContactSerializer(contact)
    contact_data = contact_serializer.data

    data_send = {}
    data_send['first_name'] = user_data.get('first_name')# type: ignore
    data_send['last_name'] = user_data.get('last_name')# type: ignore
    data_send['email'] = user_data.get('email')# type: ignore
    data_send['user_id'] = contact_data.get('id')# type: ignore
    data_send['phone_no'] = contact_data.get('phone_no')# type: ignore
    data_send['aadhar_no'] = contact_data.get('aadhar_no')# type: ignore
    data_send['date_of_birth'] = contact_data.get('date_of_birth')# type: ignore
    data_send['image_url'] = contact_data.get('image') # type: ignore


    cache.set(cache_key, json.dumps(data_send), timeout=60)
    return {
        "success": True,
        "message": f"User retrieved from database.",
        "user": data_send
    }, status.HTTP_200_OK


def delete_user_by_id(user_id):
    # get the user from the id.
    user = get_object_or_404(User, id=user_id)
    contact = get_object_or_404(Contact, id = user_id)
    
    # delete user send response.
    user.delete()
    contact.delete()

    log_in_db("INFO", "DELETE", "User AND Contact", {"message": "User and it's contact deleted successfully."})
    return {"success":True,"message": "User deleted successfully."}, status.HTTP_204_NO_CONTENT


def update_user_and_contact(id, data):
    # get the data from the id.
    contact = get_object_or_404(Contact, id = id)
    user = get_object_or_404(User, id=id)




    # print("data is :", data)
    
    #if contact not exits with this id, the you are updating wrong User which not exits.
    if not contact.DoesNotExist:
        log_in_db("ERROR", "UPDATE","User AND Contact",{"messsage":"User does not Exists."})
        return {"Success":False, "messsage":"User does not Exists."},status.HTTP_400_BAD_REQUEST

    # Find user with contact model.
    # user = contact.user

    user_fields = ['first_name', 'last_name', 'email', 'password']
    contact_fields = ['first_name', 'last_name', 'phone_no', 'aadhar_no', 'date_of_birth']

    # changed or not.
    # because user and contact both are different field so make different dict for both to update 
    # differently

    user_data = {}
    for field in user_fields:
        if field in data:
            user_data[field] = data[field]

    # print("user is :", user_data)

    contact_data = {}
    for field in contact_fields:    
        if field in data:
            contact_data[field] = data[field]

    # Update User fields via serializer
    user_serializer = UserSerializer(instance=user, data=user_data,partial=True)
    if user_serializer.is_valid():
        user_serializer.save()

    # Update Contact fields via serializer
    contact_serializer = ContactSerializer(instance=contact, data=contact_data, partial=True)

    

    data_send = {}
    data_send['first_name'] = user_data.get('first_name')
    data_send['last_name'] = user_data.get('last_name')
    data_send['email'] = user_data.get('email')
    data_send['user_id'] = contact_data.get('id')
    data_send['phone_no'] = contact_data.get('phone_no')
    data_send['aadhar_no'] = contact_data.get('aadhar_no')
    data_send['date_of_birth'] = contact_data.get('date_of_birth')


    cache_key = f"user_{id}"
    cache.set(cache_key, json.dumps(data_send), timeout=60)


    if contact_serializer.is_valid():
        contact_serializer.save()
        log_in_db("INFO", "UPDATE", "User AND Contact", {"message": "User and Contact updated successfully."})
        return {
                    "success":True,
                    "message": "User and Contact updated successfully.",
                    "user_email": user.email,
                }, status.HTTP_200_OK
    else:
        log_in_db("ERROR", "UPDATE", "User AND Contact", {"message": contact_serializer.errors})
        return {"success": False, "message": contact_serializer.errors},status.HTTP_204_NO_CONTENT
    

def search_users(filters):
    # filter details from query params
    name = filters.get('name').strip()
    
    # names = name.split(' ')

    qs = Contact.objects.all()

    # print("name :", name)
    
    #find all contacts in queryset.
    parts = name.split()
    # print("parts is :", parts)

    name_q = Q()
    for part in parts:
        name_q |= Q(first_name__icontains=part) | Q(last_name__icontains=part)
        qs = qs.filter(name_q)

    
    ContactSerializer(qs, many=True)
    
    # user = contact.user
    results = []
    for contact in qs:
        contact_data = ContactSerializer(contact).data
        contact_data['email'] = contact.user.email# type: ignore
        results.append(contact_data)

    # print("searched data :", serializer.data)

    return {"success": True, "message": "Filtered users retrieved.", "users": results}
