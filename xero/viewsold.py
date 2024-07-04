from django.shortcuts import render,HttpResponse,redirect
from .otp import generate_otp
import pyrebase
from mailjet_rest import Client
from django.core.files.storage import FileSystemStorage
import fitz
import uuid
import random
import os
firebase_config = {
    "apiKey": "AIzaSyCWMvP2Xz07RtKLChY7m0TT7M79VRK_e_A",
    "authDomain": "xerocart.firebaseapp.com",
    "databaseURL": "https://xerocart-default-rtdb.firebaseio.com",
    "projectId": "xerocart",
    "storageBucket": "xerocart.appspot.com",
    "messagingSenderId": "464907504515",
    "appId": "1:464907504515:web:cfcde08411bf41f4af84b6"
}

api_key = 'da023e0f6ee795fe02542f204bad7d97'
api_secret = '3780a1c3f0751249fc0858b9c9a039a6'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()
def count_pages(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        num_pages = pdf_document.page_count
        pdf_document.close()

        return num_pages

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
def send_mail(email, otp):
    try:
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "riza@rizad.ml",
                        "Name": "riza"
                    },
                    "To": [
                        {
                            "Email": email,
                            "Name": "Xero user"
                        }
                    ],
                    "Subject": "Xero Cart OTP Confirmation",
                    "TextPart": f"Hello, Your OTP code for Xero Cart is: {otp}",
                    "HTMLPart": f"<h3>Hello,</h3><p>Your OTP code for Xero Cart is: <strong>{otp}</strong></p>"
                }
            ]
        }
        result = mailjet.send.create(data=data)
        data = {"code" : otp,"status" : "pending"}
        email = email.split("@")
        db.child("otp").child(email[0]).set(data)
        return "OTP Send Succesfully"
    except Exception as e:
        print(e)
        return "Try after some time"
def home(request):
    if request.session.get('is_authenticated') == True:
        cartlist = []
        paidcartlist = []
        if request.method == "POST":
                uploaded_file = request.FILES['file']
                fs = FileSystemStorage()
                fs.save(os.path.join(request.session.get("username"), uploaded_file.name), uploaded_file)
                price = count_pages("media/"+request.session.get("username")+f"/{uploaded_file.name}")
                print(price)
                orientation = request.POST.get("orient")
                no_of_copy = request.POST.get("input2")
                priority = request.POST.get("priority")
                dataup = {"file":uploaded_file.name,"orientation":orientation,"copies":no_of_copy,"priority":priority,"price":price}
                db.child("currentcart").child(request.session.get("username")).child(str(random.randint(10000, 99999))).set(dataup)
        currentcartdb = db.child("currentcart").get().val().keys()
        print(currentcartdb)
        paidcartdb = db.child("paidcart").get().val().keys()
        print(paidcartdb)
        if request.session.get("username") in currentcartdb:
            usercurrentcardb = db.child("currentcart").child(request.session.get("username")).get().val().keys()
            print("kkkkk")
            for i in range(len(usercurrentcardb)):
                filename = db.child("currentcart").child(request.session.get("username")).child(list(usercurrentcardb)[i]).get().val().get("file")
                orientation = db.child("currentcart").child(request.session.get("username")).child(list(usercurrentcardb)[i]).get().val().get("orientation")
                copies = db.child("currentcart").child(request.session.get("username")).child(list(usercurrentcardb)[i]).get().val().get("copies")
                prioritydb = db.child("currentcart").child(request.session.get("username")).child(list(usercurrentcardb)[i]).get().val().get("priority")
                pricedb = db.child("currentcart").child(request.session.get("username")).child(list(usercurrentcardb)[i]).get().val().get("price")
                currentcartdict = {"file":filename,"orient":orientation,"copy":copies,"priority":prioritydb,"price":pricedb}
                cartlist.append(currentcartdict)
        if request.session.get("username") in paidcartdb:
            userpaidcardb = db.child("paidcart").child(request.session.get("username")).get().val().keys()
            
            for i in range(len(userpaidcardb)):
                status = db.child("paidcart").child(request.session.get("username")).child(list(userpaidcardb)[i]).get().val().get("status")
                orderid = list(userpaidcardb)[i]
                print(orderid)
                username = db.child("users").child(request.session.get("username")).get().val().get("name")
                paidcartdb = {"status":status,"orderid":orderid,"name":username}
                paidcartlist.append(paidcartdb)
        
        return render(request,"index.html",context={"context":cartlist,"paidcart":paidcartlist })
    else:
        return render(request,"home.html") 
def logout(request):
    request.session.flush()
    return redirect(home) 
def login(request):
    if request.method == "POST":
        input_otp = request.POST.get("otp")
        phno = request.POST.get("phno")
        print(phno)
        if phno != None:
            print("helllllllllllll")
            name = request.POST.get("name")
            mail2db = request.POST.get("mail")
            mailsplitted = mail2db.split("@")[0]
            data = {"name" : name,"mobile" : phno,"mail":mail2db}
            db.child("users").child(mailsplitted).set(data)
            request.session['user_id'] = 1
            request.session['username'] = 'example_user'
            request.session['is_authenticated'] = True
            return redirect(home)
        if input_otp == None and phno == None:
            email =request.POST.get("email")
            otp = generate_otp()
            mail_status=send_mail(email,otp)
            context = {"status":mail_status,"mail":email}
            return render(request,"login.html",context=context)
        elif request.POST.get("email") != None:
            mail =request.POST.get("email")
            email = mail.split("@")
            otp_code = db.child("otp").child(email[0]).get().val().get("code")
            print(email[0])
            users = db.child("users").get().val().keys()
            print(users)
            if otp_code == input_otp:
                if email[0] in users:
                    request.session['user_id'] = 1
                    request.session['username'] = email[0]
                    request.session['is_authenticated'] = True
                    return redirect(home)
                else:
                    return render(request,"newuser.html",{"mail":mail})
            else:
                return HttpResponse("Invalid Otp")
    else:
        return render(request,"login.html")