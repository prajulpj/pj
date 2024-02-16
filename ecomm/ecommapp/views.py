from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views import View
from ecommapp.forms import UserRegister,UserLogin,CartForm,OrderForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from ecommapp.models import Products,Carts,Orders
from django.core.mail import send_mail,settings



# Create your views here.
class Home(View):
    def get(self,request,*args,**kwargs):
        data=Products.objects.all()
        return render(request,'index.html',{'products':data})
    
class UserRegisterView(View):
    def get(self,request):
        form=UserRegister()
        return render(request,'reg.html',{'form':form})
    
    def post(self,request,*args,**kwargs):
        form=UserRegister(request.POST)
        if form.is_valid():
            User.objects.create_user(**form.cleaned_data)
            messages.success(request,'registration successfully')
            return HttpResponse('log_view')
        else:
            messages.error(request,'invalid')
            return redirect('home_view')
        
class UserLoginView(View):
    def get(self,request,*args,**kwargs):
        form=UserLogin()
        return render(request,'userlogin.html',{'form':form})
    
    def post(self,request,*args,**kwargs):
            form=UserLogin(request.POST)
        
            uname=request.POST.get('username')
            pswd=request.POST.get('password')
            User=authenticate(request,username=uname,password=pswd)
            if User:
                login(request,User)
                messages.success(request,'login success')
                return redirect('home_view')
            else:
                messages.error(request,'invalid') 
                return redirect('log_view')   

class LogoutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        messages.success(request,'logout success')
        return redirect('home_view')

class ProductDetailView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('id')
        product=Products.objects.get(id=id)
        return render(request,'productdetail.html',{'product':product})
    
class AddToCartView(View):
    def get(self,request,*args,**kwargs):
         form=CartForm()
         id=kwargs.get('id')
         product=Products.objects.get(id=id)
         return render(request,'addtocart.html',{'form':form,'product':product})
          
    def post(self,request,*args,**kwargs):
        u=request.user
        id=kwargs.get('id')
        p=Products.objects.get(id=id)
        q=request.POST.get('quantity')
        Carts.objects.create(user=u,quantity=q,product=p)
        return redirect('home_view')

class CartListView(View):
    def get(self,request,*args,**kwargs):
        cart=Carts.objects.filter(user=request.user).exclude(status='order-placed')
        return render(request,'cartlist.html',{'cart':cart})
    
class PlaceOrderView(View):
    def get(self,request,*args,**kwargs):
        form=OrderForm()
        return render(request,'placeorder.html',{'form':form})

    def post(self,request,*args,**kwargs):
        cart_id=kwargs.get('cart_id')      
        cart=Carts.objects.get(id=cart_id)
        user=request.user
        address=request.POST.get('address')
        email=request.POST.get('email')
        Orders.objects.create(user=user,cart=cart,address=address,email=email)
        send_mail('confirmation','order placed successfully',settings.EMAIL_HOST_USER,[email])
        cart.status='order-placed'
        cart.save()
        return redirect('home_view')
    
class CartDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get('id')
        data=Carts.objects.get(id=id)
        data.delete()
        return redirect('cartlist_view')

