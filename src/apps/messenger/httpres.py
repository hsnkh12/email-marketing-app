
from django.shortcuts import render,redirect




def SuccessSubscribed(request):

    query_params = request.GET

    return render(request,'httpres/success_sub.html',{'email':query_params['email']})

def SuccessMessageSent(request):

    return render(request,'httpres/success_sent.html')


def ObjectNotFound(request):
    pass