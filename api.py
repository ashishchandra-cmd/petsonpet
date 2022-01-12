from django.shortcuts import render
import json

# Create your views here.
from petsapp.models import *
from django.contrib.auth.models import User
from petsapp.serializers import *
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView,ListAPIView
from rest_framework.views import APIView
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages,auth
from django.contrib.auth.hashers import make_password,check_password
from django.db import IntegrityError
from rest_framework.authentication import BasicAuthentication,TokenAuthentication,SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from petsapp.signals import create_auth_token
from rest_framework.authtoken.models import Token
from geopy.distance import geodesic


 


class CustomerRegister(ViewSet):
    def list(self,request):
        query=Customer.objects.all()
        serilizer=CustomerSerializers(query,many=True)
        serv={'customer':serilizer.data}
        return Response(serv)
    
    def create(self,request):
        data=request.data
        username1=data.get("username")
        email1=data.get("email")
        password1=data.get("password")
        phone1=data.get("phone")
        if username1=='' or email1=='' or password1=='' or phone1=='':
            response_data = {'response_code':200,'comments':'Category is required',"status": False}
            return Response(response_data)
        try:
            user1=User(username=username1,email=email1,password=make_password(password1))
            user1.save()
            user_inst=User.objects.get(username=username1)#instance
            servive=Customer(user=user_inst,phone=phone1)
            servive.save()
            response_data = {'response_code':200,'comments':'register is succeefull',"status": True}
            return Response(response_data)
        except :
            response_data = {'response_code':400,'comments':'All ready created',"status": False}
            return Response(response_data)


class UserLogin(APIView):
    # authentication_classes=[TokenAuthentication]
    # permission_classes=[IsAuthenticated]
    def post(self,request): 
        data=request.data
        email=data.get('email')
        password=data.get('password')
        user_obj=User.objects.get(email=email)
        print(user_obj)
        if email=='' or password=='':
            response_data = {'response_code':200,'comments':'Category is required',"status": False}
            return Response(response_data)
        if user_obj.check_password(password):
            login(request,user_obj)
            response_data = {'response_code':200,'id':user_obj.id,'email':user_obj.email,'comments':'login is succeefull',"status": True}
            return Response(response_data)
        response_data = {'response_code':400,'comments':'user is not authenticated',"status": False}
        return Response(response_data)
class LogoutView(APIView):
    def get(self, request):
        logout(request)
        response_data = {'response_code':200,'comments':'logout is succeefull',"status": True}
        return Response(response_data)




class ServiceRegister(ViewSet):
    #aaj ka list
    # authentication_classes=[TokenAuthentication]
    # permission_classes=[IsAuthenticated]
    def list(self,request):
        query=ServiceProdiver.objects.all()
        serilizer=ServiceProvderSerializerlist(query,many=True)
        serv={'servicprovider':serilizer.data}
        return Response(serv)

    def retrieve(self,request,id=None):
        user_inst=User.objects.get(id=id)
        cust_inst=Customer.objects.get(user=user_inst)
        mp_customer=GoogleMapModelCust.objects.get(service=cust_inst)
        cust_dis=(mp_customer.letitude,mp_customer.longitude)
        print('cust_dis',cust_dis)
        mp_servive=GoogleMapModel.objects.filter(status=True)
        li=[]
        for x in mp_servive:
            print(x.service)
            service_dis = (x.letitude, x.longitude)
            print('service_dis',service_dis)
            c = geodesic(cust_dis, service_dis).miles
            print('c',c)
            Km = c / 0.62137
            print(Km)
            
            if Km<=5:
                ur=User.objects.get(username=x.service)
                sr=ServiceProdiver.objects.get(user=ur)
                li.append(sr)
        serialize=ServiceProvderSerializerlist(li,many=True)
        return Response(serialize.data)
        
    def create(self,request):
        data=request.data
        username=data.get("username")
        email=data.get("email")
        password=data.get("password")
        phone=data.get("phone")
        whatsapp=data.get("whatsapp")
        aadharnumber=data.get("aadharnumber")
       
        try:
            user1=User(username=username,email=email,password=make_password(password))
            servive=ServiceProdiver(user=user1,phone=phone,whatsapp=whatsapp,aadharnumber=aadharnumber)
            user1.save()
            servive.save()
            user_inst=User.objects.get(username=username)
            tk=Token.objects.get(user=user_inst)
            response_data = {'response_code':200,'comments':'register is succeefull','Token':tk.key,"status": True}
            return Response(response_data)
        except IntegrityError:
            response_data = {'response_code':400,'comments':'All ready created',"status": False}
            return Response(response_data)
    




class ServiceTimeSlotall(ViewSet):
    def list(self,request):
        timelist=TimeSlot.objects.filter(status=True)
        ts=TimeSlotSerialize(timelist,many=True)
        return Response(ts.data)
    def create(self,request):
        data=request.data
        email1=data.get('email')
        date1=data.get('date')
        time_start1=data.get('time_start')
        time_end1=data.get('time_end')
        status1=data.get('status')
        try:
            user1=User.objects.get(email=email1)#instance
            srv=ServiceProdiver.objects.get(user=user1)#instance
            ts=TimeSlot(serviceProvdr=srv, date=date1,time_start=time_start1,time_end=time_end1,status=status1)
            ts.save()
            response_data = {'response_code':200,'comments':'timeslot is succeefull created',"status": True}
            return Response(response_data)
        except User.DoesNotExist:
            response_data = {'response_code':400,'comments':'provider are not register',"status": False}
            return Response(response_data)
    
    def destroy(self,request,id=None):
        try:
            ts=TimeSlot.objects.get(id=id)
            ts.delete()
            response_data = {'response_code':200,'comments':'timeslot is succeefull deleted',"status": True}
            return Response(response_data)
        except TimeSlot.DoesNotExist:
            response_data = {'response_code':200,'comments':'timeslot is invalid',"status": False}
            return Response(response_data)

    def update(self,request,id=None):
        data=request.data
        email1=data.get('email')
        date1=data.get('date')
        time_start1=data.get('time_start')
        time_end1=data.get('time_end')
        status1=data.get('status')
        try:
            ut=User.objects.get(email=email1) #instance make
            srv=ServiceProdiver.objects.get(user=ut)#instance
            ts=TimeSlot.objects.get(id=id)
            ts.serviceProvdr=srv ##instance use here
            ts.date=date1
            ts.time_start=time_start1
            ts.time_end=time_end1
            ts.status=status1
            ts.save()
            response_data = {'response_code':200,'comments':'timeslot is succeefull update',"status": True}
            return Response(response_data)
        except TimeSlot.DoesNotExist:
            response_data = {'response_code':200,'comments':'service provider not  register',"status": False}
            return Response(response_data)

    
class GoogleMapCreate(ViewSet):
    def create(self,request,id=None):
        data=request.data
        email1=data.get('email')
        longitude1=data.get('longitude')
        letitude1=data.get('letitude')
        status1=data.get('status')
        try:
            user1=User.objects.get(email=email1)#instance
            sp=ServiceProdiver.objects.get(user=user1)#instance
            try:
                gm=GoogleMapModel.objects.get(service=sp)
                gm.longitude=longitude1
                gm.letitude=letitude1
                gm.status=status1
                gm.save()
                response_data = {'response_code':200,'comments':'map is succeefull updated',"status": True}
                return Response(response_data)
            except:
                gmm=GoogleMapModel(service=sp,longitude=longitude1,letitude=letitude1,status=status1)
                gmm.save()
                response_data = {'response_code':200,'comments':'map is succeefull created',"status": True}
                return Response(response_data)
        except User.DoesNotExist:
            response_data = {'response_code':400,'comments':'provider is not register',"status": False}
            return Response(response_data)
    def list(self,request):
        mp_servive=GoogleMapModel.objects.filter(status='ONDUTY')
        serialize=GoogleMapSerializer(mp_servive,many=True)
        return Response(serialize.data)
        #ADDDDDDDD retrive only
    def retrieve(self,request,id=None):
        user_inst=User.objects.get(id=id)
        cust_inst=Customer.objects.get(user=user_inst)
        mp_customer=GoogleMapModelCust.objects.get(service=cust_inst)
     
        cust_dis=(mp_customer.letitude,mp_customer.longitude)
        print('cust_dis',cust_dis)
        mp_servive=GoogleMapModel.objects.filter(status='ONDUTY')
        li=[]
        for x in mp_servive:
            print(x.service)
            service_dis = (x.letitude, x.longitude)
            print('service_dis',service_dis)
            c = geodesic(cust_dis, service_dis).miles
            print('c',c)
            Km = c / 0.62137
            print(Km)
            
            if Km<=5:
                ur=User.objects.get(username=x.service)
                sr=ServiceProdiver.objects.get(user=ur)
                gm=GoogleMapModel.objects.get(service=sr)
                li.append(gm)
        serialize=GoogleMapSerializerMap(li,many=True)
        return Response(serialize.data)
class ServicProvderCustmStatus(ViewSet):
    def create(self,request):
        sp_email1=request.data.get('sp_email')
        status1=request.data.get('user_status')
        ur_email1=request.data.get('user_email')
        customertime_id=request.data.get('customertime_id')
  
        if (status1=='Confirm' or status1=='Cancle' or status1=='TimeOver'):
            
            try:
                obj = User.objects.get(email=ur_email1)
                user_inst=User.objects.get(email=sp_email1)
                svr_inst=ServiceProdiver.objects.get(user=user_inst)
                gmapinst=GoogleMapModel.objects.get(service=svr_inst)
                cust_inst=Customer.objects.get(user=obj)
                cust_book=CustomerTime.objects.filter(customer=cust_inst).get(id=customertime_id)

                if status1=='Confirm':
                    cust_book.status=status1
                    cust_book.save()
                    gmapinst.status='BOOKED'
                    gmapinst.save()
                    response_data = {'response_code':200,'comments':'provider booking conform',"status": True}
                    return Response(response_data)
                elif status1=='Cancle':
                    cust_book.status=status1
                    cust_book.save()
                    gmapinst.status='ONDUTY'
                    gmapinst.save()
                    response_data = {'response_code':200,'comments':'provider booking cancle',"status": True}
                    return Response(response_data)
                elif status1=='TimeOver':
                    cust_book.status=status1
                    cust_book.save()
                    gmapinst.status='ONDUTY'
                    gmapinst.save()
                    response_data = {'response_code':200,'comments':'service time over',"status": True}
                    return Response(response_data)
            except:
                response_data = {'response_code':200,'comments':'time not match',"status": False}
                return Response(response_data)
        else:
            response_data = {'response_code':200,'comments':'user_status,user_email is required',"status": False}
            return Response(response_data)
        

class ServiceProviderOffOn(ViewSet):
    def create(self,request):
        email1=request.data.get('sp_email')
        status1=request.data.get('sp_satatus')

        if status1=='':
            response_data = {'response_code':200,'comments':'status is required',"status": False}
            return Response(response_data)
        try:
            user_inst=User.objects.get(email=email1)
            svr_inst=ServiceProdiver.objects.get(user=user_inst)
            gmapinst=GoogleMapModel.objects.get(service=svr_inst)
        
            if status1=='ONDUTY':
                gmapinst.status=status1
                gmapinst.save()
                response_data = {'response_code':200,'comments':'provider is ONDUTY',"status": True}
                return Response(response_data)
            elif status1=='OFFDUTY':
                gmapinst.status=status1
                gmapinst.save()
                response_data = {'response_code':200,'comments':'provider is OFFDUTY',"status": True}
                return Response(response_data)
        except GoogleMapModel.DoesNotExist:
            response_data = {'response_code':200,'comments':'service provider not  register',"status": False}
            return Response(response_data)
    def list(self,request):
        mp_servive=GoogleMapModel.objects.all()
        serialize=GoogleMapSerializer(mp_servive,many=True)
        gd={'servicemap':serialize.data}
        return Response(gd)




class GoogleMapCreateCust(ViewSet):
    def create(self,request,id=None):
        data=request.data
        email1=data.get('email')
        longitude1=data.get('longitude')
        letitude1=data.get('letitude')

        try:
            user1=User.objects.get(email=email1)#instance
            sp=Customer.objects.get(user=user1)#instance
            try:
                gm=GoogleMapModelCust.objects.get(service=sp)
                gm.longitude=longitude1
                gm.letitude=letitude1
        
                gm.save()
                response_data = {'response_code':200,'comments':'map is succeefull updated',"status": True}
                return Response(response_data)
            except:
                gmm=GoogleMapModelCust(service=sp,longitude=longitude1,letitude=letitude1)
                gmm.save()
                response_data = {'response_code':200,'comments':'map is succeefull created',"status": True}
                return Response(response_data)
        except User.DoesNotExist:
            response_data = {'response_code':400,'comments':'provider is not register',"status": False}
            return Response(response_data)



class CustomerTimes(ViewSet):
    def create(self,request):
        data=request.data
        ur_email=data.get('ur_email')
        date1=data.get('date')
        time1=data.get('time')
        sp_email=data.get('sp_email')
        if  ur_email=='' or date1=='' or time1=='' or sp_email=='':
            response_data = {'response_code':200,'comments':'Category is required',"status": False}
            return Response(response_data)
        try:            
            user1=User.objects.get(email=ur_email)#instance
            sp=Customer.objects.get(user=user1)#instance
            sp_user=User.objects.get(email=sp_email)
            sp_ser=ServiceProdiver.objects.get(user=sp_user)                    
            gmm=CustomerTime(customer=sp,date=date1,time=time1,serviceProvdr=sp_ser)
            gmm.save()   
            shop_dict = {'response_code':200, 'comments':'customer time is succeefull created',"status": True}
            return Response(shop_dict)
        except User.DoesNotExist:
            response_data = {'response_code':400,'comments':'customer  is not register',"status": False}
            return Response(response_data)
    def list(self,request):
        timelist=CustomerTime.objects.filter(status='Confirm')
        ts=CustomerTimeSerializer(timelist,many=True)
        dt={'custTime':ts.data}
        return Response(dt)
    def retrieve(self,request,id):
        try:
            user_inst=User.objects.get(id=id)
            cust_inst=Customer.objects.get(user=user_inst)
            mp_customer=CustomerTime.objects.filter(customer=cust_inst,status='Confirm')
            serialize=CustomerTimeSerializer(mp_customer,many=True)
            dt={'custTime':serialize.data}
            return Response(dt)
        except:
            response_data = {'response_code':400,'comments':'customer  is not exist',"status": False}
            return Response(response_data)

    def destroy(self,request,id=None):
        try:
            ts=CustomerTime.objects.get(id=id)
            ts.delete()
            response_data = {'response_code':200,'comments':'CustomerTime is succeefull deleted',"status": True}
            return Response(response_data)
        except CustomerTime.DoesNotExist:
            response_data = {'response_code':200,'comments':'CustomerTime is invalid',"status": False}
            return Response(response_data)

class CustomerTimeslistAll(ViewSet):
    def list(self,request):
        timelist=CustomerTime.objects.all()
        ts=CustomerTimeSerializer(timelist,many=True)
        dt={'custTime':ts.data}
        return Response(dt)

##add karna hai
class Serviceprovidelist(ViewSet):
    def create(self,request):
        email=request.data.get('sp_email')
        try:
            user_inst=User.objects.get(email=email)
            serv_inst=ServiceProdiver.objects.get(user=user_inst)
            sr_object=CustomerTime.objects.filter(serviceProvdr=serv_inst).filter(status='Panding')
            if sr_object:

                dat_dict={}
                data_list=[]
                for x in sr_object:
                    u_gmail=x.customer.user.email    
                    usr_inst=User.objects.get(email=u_gmail)
                    custr_inst=Customer.objects.get(user=usr_inst)
                    googmpcust=GoogleMapModelCust.objects.get(service=custr_inst)
                    # print(googmpcust.letitude)
                    dat_dict={'customerTime_id':x.id,'user_id':x.customer.user.id,'user_email':x.customer.user.email,'username':x.customer.user.username,'date':x.date,'time':x.time,'booking':x.status,
                    'user_letitude':googmpcust.letitude,'user_longitude':googmpcust.longitude}
                    data_list.append(dat_dict)
                book_dict={"user_details":data_list,'response_code':200,'comments':'all panding list',"status": True}
                return Response(book_dict)
            else:
                book_dicts={'response_code':200,'comments':'no panding list',"status": False}
                return Response(book_dicts)

        except:
            book_dict={'response_code':200,'comments':'provider is not register',"status": False}
            return Response(book_dict)

class Serviceprovidelist_conf(ViewSet):
    def create(self,request):
        email=request.data.get('sp_email')
        try:
            user_inst=User.objects.get(email=email)
            serv_inst=ServiceProdiver.objects.get(user=user_inst)
            sr_object=CustomerTime.objects.filter(serviceProvdr=serv_inst).filter(status='Confirm')
            if sr_object:

                dat_dict={}
                data_list=[]
                for x in sr_object:
                    u_gmail=x.customer.user.email    
                    usr_inst=User.objects.get(email=u_gmail)
                    custr_inst=Customer.objects.get(user=usr_inst)
                    googmpcust=GoogleMapModelCust.objects.get(service=custr_inst)
                    # print(googmpcust.letitude)
                    dat_dict={'customerTime_id':x.id,'user_id':x.customer.user.id,'user_email':x.customer.user.email,'username':x.customer.user.username,'date':x.date,'time':x.time,'booking':x.status,
                    'user_letitude':googmpcust.letitude,'user_longitude':googmpcust.longitude}
                    data_list.append(dat_dict)
                book_dict={"user_details":data_list,'response_code':200,'comments':'all confirm list',"status": True}
                return Response(book_dict)
            else:
                book_dicts={'response_code':200,'comments':'no confirm list',"status": False}
                return Response(book_dicts)

        except:
            book_dict={'response_code':200,'comments':'provider is not register',"status": False}
            return Response(book_dict)


class Customerbooklist(ViewSet):
    def create(self,request):
        email=request.data.get('ur_email')
        try:
            user_inst=User.objects.get(email=email)
            serv_inst=Customer.objects.get(user=user_inst)
            sr_object=CustomerTime.objects.filter(customer=serv_inst)
            print(sr_object)
            if sr_object:

                dat_dict={}
                data_list=[]
                for x in sr_object:
                    s_gmail=x.serviceProvdr.user.email 
                    print(s_gmail)   
                    usr_inst=User.objects.get(email=s_gmail)
                    custr_inst=ServiceProdiver.objects.get(user=usr_inst)
                    googmpcust=GoogleMapModel.objects.get(service=custr_inst)
                    print(googmpcust.letitude)
                    dat_dict={'customerTime_id':x.id,'provider_id':x.serviceProvdr.user.id,'provider_email':x.serviceProvdr.user.email,'provider_username':x.serviceProvdr.user.username,'date':x.date,'time':x.time,'booking':x.status,
                    'provider_letitude':googmpcust.letitude,'provider_longitude':googmpcust.longitude}
                    data_list.append(dat_dict)
                book_dict={"provider_details":data_list,'response_code':200,'comments':'all  list',"status": True}
                return Response(book_dict)
            else:
                book_dicts={'response_code':200,'comments':'no list',"status": False}
                return Response(book_dicts)

        except:
            book_dict={'response_code':200,'comments':'provider is not register',"status": False}
            return Response(book_dict)


    


class Book(ViewSet):
    def create(self,request):
        data=request.data
        name=data.get('name')
        phone=data.get('phone')
        booking_time=data.get('booking_time')
        leveing_time=data.get('leveing_time')
        book=BookService(name=name,phone=phone,booking_time=booking_time,leveing_time=leveing_time)
        book.save()
        return Response({"book is conformed"})
                
                
                
                
                
                
                
                
 from petsapp.models import *
from rest_framework import serializers
from django.contrib.auth.models import User
from drf_writable_nested import WritableNestedModelSerializer
from django.contrib.auth.hashers import make_password,check_password
from rest_framework.authtoken.models import Token

class UserSerializers(serializers.ModelSerializer):
    @staticmethod
    def validate_password(password: str):
        return make_password(password)
    class Meta:
        model=User
        fields=['id','username','email']
    

class TokenSerializers(serializers.ModelSerializer):
    class Meta:
        model=Token
        fields=['key']

class CustomerSerializers(WritableNestedModelSerializer):
    user=UserSerializers()
    class Meta:
        model=Customer
        fields=['user','phone']
    # def validate_phone(self,value):
    #     if len(value)==10:
    #         return value
    #     else:
    #         raise serializers.ValidationError('set currect phone number')
    
    # def validate_whatsapp(self,value):
    #     if len(value)==10:
    #         return value
    #     else:
    #         raise serializers.ValidationError('set currect whatsapp phone number')
    # def validate_aadharnumber(self,value):
    #     if len(value)==12:
    #         return value
    #     else:
    #         raise serializers.ValidationError('set currect aadhar number')

        
    



class ServiceProvderSerializer(serializers.ModelSerializer):
    # user=UserSerializers
    class Meta:
        model=ServiceProdiver
        fields=['user','phone','whatsapp','aadharnumber','image']
    def validate_phone(self,value):
        if len(value)==10:
            return value
        else:
            raise serializers.ValidationError('set currect phone number')
    def validate_whatsapp(self,value):
        if len(value)==10:
            return value
        else:
            raise serializers.ValidationError('set currect whatsapp phone number')
    def validate_aadharnumber(self,value):
        if len(value)==12:
            return value
        else:
            raise serializers.ValidationError('set currect aadhar number')


class Userlistserilizrlist(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email']
class ServiceProvderSerializerlist(serializers.ModelSerializer):
    user=Userlistserilizrlist()
    class Meta:
        model=ServiceProdiver
        fields=['user','phone','whatsapp','aadharnumber','image']

class GoogleMapSerializer(serializers.ModelSerializer):
    service=ServiceProvderSerializerlist()
    class Meta:
        model=GoogleMapModel
        fields=['service','longitude','letitude','status']
###################################ADD 
# class Userservicemap(serializers.ModelSerializer):
#     class Meta:
#         model=User
#         fields=['username','email']
# class ServiceProvderSermap(serializers.ModelSerializer):
#     user=Userservicemap()
#     class Meta:
#         model=ServiceProdiver
#         fields=['user']

class GoogleMapSerializerMap(serializers.ModelSerializer):
    # service=ServiceProvderSermap()
    class Meta:
        model=GoogleMapModel
        fields=['service','longitude','letitude','status']
###################################ADD tak
# class UserSeriali(serializers.ModelSerializer):
#     class Meta:
#         model=User
#         fields=['username','email']
class CustomerSerial(serializers.ModelSerializer):
    user=UserSerializers()
    class Meta:
        model=Customer
        fields=['user','phone']
class ServiceProvderSerial(serializers.ModelSerializer):
    user=UserSerializers()
    class Meta:
        model=ServiceProdiver
        fields=['user','phone',]

class CustomerTimeSerializer(serializers.ModelSerializer):
    customer=CustomerSerial()
    serviceProvdr=ServiceProvderSerial()
    class Meta:
        model=CustomerTime
        fields=['id','customer','date','time','status','serviceProvdr']




#time slot list ke liye hai new


class TimeSlotSerialize(serializers.ModelSerializer):
    serviceProvdr=ServiceProvderSerializerlist()
    class Meta:
        model=TimeSlot
        fields=['serviceProvdr','date','time_start','time_end','status']









class BookServiceSerialize(serializers.ModelSerializer):
    class Meta:
        model=BookService
        fields=['name','phone','booking_time','leveing_time']
        
        
        
        # from myproject.storage import OverwriteStorage
from django.db import models
# from django.contrib.gis.db import models
from django.contrib.auth.models import User 
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=12 ,unique=True)
    def __str__(self):
        return self.user.username



class ServiceProdiver(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=12, unique=True)
    whatsapp=models.CharField(max_length=12 )
    aadharnumber=models.CharField(max_length=12,unique=True)
    image=models.ImageField(upload_to='photo',blank = True)
    
    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance, created, **kwargs):
        if created:
            Token.objects.create(user=instance)
    def __str__(self):
        return self.user.username
    
    
    
class GoogleMapModel(models.Model):
    STATUS_CHOICES =(
    ("ONDUTY", "ONDUTY"),
    ("OFFDUTY", "OFFDUTY"),
    ("BOOKED", "BOOKED"),
    )
    service=models.OneToOneField(ServiceProdiver,on_delete=models.CASCADE)
    longitude=models.CharField(max_length=100)
    letitude=models.CharField(max_length=100)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES,default='OFFDUTY')
    def __str__(self):
        return self.service.user.username


class GoogleMapModelCust(models.Model):
    service=models.OneToOneField(Customer,on_delete=models.CASCADE)
    longitude=models.CharField(max_length=100)
    letitude=models.CharField(max_length=100)
    def __str__(self):
        return self.service.user.username
#new
class TimeSlot(models.Model):
    serviceProvdr=models.ForeignKey(ServiceProdiver,on_delete=models.CASCADE)
    date=models.DateField(null=True)
    time_start=models.TimeField(null=True)
    time_end=models.TimeField(null=True)
    status=models.BooleanField(default=False)

    def __str__(self):
        return self.serviceProvdr.user.username


class CustomerTime(models.Model):
    STATUS_CHOICES =(
    ("Panding", "Panding"),
    ("Confirm", "Confirm"),
    ("Cancle", "Cancle"),
    ("TimeOver", "TimeOver"),
    )
    
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    date=models.CharField(max_length=100)
    time=models.CharField(max_length=100)
    serviceProvdr=models.ForeignKey(ServiceProdiver,on_delete=models.CASCADE)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES,default='Panding')
    def __str__(self):
        return self.customer.user.username

class BookService(models.Model):
    name=models.CharField(max_length=100)
    phone=models.PositiveIntegerField()
    booking_time=models.DateTimeField()
    leveing_time=models.DateTimeField()
    # location = models.PointField()

"""Petsondog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from petsapp import views
from rest_framework.authtoken import views as au

urlpatterns = [
    path('generate_token/',au.obtain_auth_token),
    path('admin/', admin.site.urls),
    path('customer_register/',views.CustomerRegister.as_view({'post':'create'})),
    path('customer_list/',views.CustomerRegister.as_view({'get':'list'})),
    path('cust_map_create/',views.GoogleMapCreateCust.as_view({'post':'create'})),
    path('service_provide_list/',views.ServiceRegister.as_view({'get':'list'})),
    path('servi_prov_list_by_map/<int:id>/',views.ServiceRegister.as_view({'get':'retrieve'})),
    
    path('servi_prov_map_one/<int:id>/',views.GoogleMapCreate.as_view({'get':'retrieve'})),
    path('servi_prov_cust_status/',views.ServicProvderCustmStatus.as_view({'post':'create'})),
    path('service_register/',views.ServiceRegister.as_view({'post':'create'})),
    
    path('servi_map_create/',views.GoogleMapCreate.as_view({'post':'create'})),
    path('servi_prov_map_onduty_list/',views.GoogleMapCreate.as_view({'get':'list'})),
    path('serv_Prov_map_Off_On/',views.ServiceProviderOffOn.as_view({'post':'create'})),
    path('serv_Prov_map_all_list/',views.ServiceProviderOffOn.as_view({'get':'list'})),
    
    path('customertime_create/',views.CustomerTimes.as_view({'post':'create'})),
    ###add
    path('customertime_list_conf/',views.CustomerTimes.as_view({'get':'list'})),
    path('customertime_one/<int:id>/',views.CustomerTimes.as_view({'get':'retrieve'})),
    path('custo_prv_book_list/',views.CustomerTimeslistAll.as_view({'get':'list'})),
    path('customertimes_delete/<int:id>/',views.CustomerTimes.as_view({'delete':'destroy'})),
    #add krna hai
    path('customer_list_book_to_serv_prod/',views.Serviceprovidelist.as_view({'post':'create'})),
    path('customer_list_book_to_serv_prod_confirm/',views.Serviceprovidelist_conf.as_view({'post':'create'})),
    path('serv_prov_book_list_to_custr/',views.Customerbooklist.as_view({'post':'create'})),

##avi

    path('book/',views.Book.as_view({'post':'create'})),
    path('login/',views.UserLogin.as_view()),
    path('logout/',views.LogoutView.as_view()),


    path('timeslot_list/',views.ServiceTimeSlotall.as_view({'get':'list'})), #viewset
    path('timeslot_create/',views.ServiceTimeSlotall.as_view({'post':'create'})),
    path('timeslot_delete/<int:id>/',views.ServiceTimeSlotall.as_view({'delete':'destroy'})),
    path('timeslot_update/<int:id>/',views.ServiceTimeSlotall.as_view({'put':'update'})),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




    #https://www.dangtrinh.com/2015/11/imagefield-overwrite-image-file-with.html

