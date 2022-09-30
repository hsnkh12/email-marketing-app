from django.http.response import JsonResponse
from django.shortcuts import render,redirect
from django.views.generic import View
from ..accounts.models import User
from django.views.generic.detail import DetailView
from django.http import HttpResponseNotFound
from .forms import EmailForm,SubscriberForm
from django.contrib import messages
from .models import Campaign,Email, Message,Subscriber
from django.views.generic import DetailView , CreateView , ListView 
from django.contrib.auth.mixins import (
    LoginRequiredMixin)
from .forms import EmailForm
from django.utils import timezone
from ..email_sender.celery import send_mail_async_task
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator




# Email Views


class EmailView(LoginRequiredMixin,View):       # Email General View


    def get(self,request):      # Email List View
        
        emails = self.get_queryset()    # Get list of emails related to user

        context = { 'emails' : emails }
        return render(request,"messenger/emails_list.html",context)


    def delete(self,request,pk):    # Email Delete View
        
        email = Email.objects.get_or_404('user', user=request.user, pk=pk)      # Using custom manager method to get the wanted email

        email.delete()
        return JsonResponse("Deleted",safe=False)


    def get_queryset(self,**kwargs):

        user = self.request.user

        return Email.objects.filter_by(     # 'user' for select_related , other are the filter kwargs
            'user'  , user=user, **kwargs
        )



class EmailCreateView(LoginRequiredMixin,CreateView):     # Email Create View


    form_class = EmailForm
    template_name="messenger/email_create.html"


    def get(self,request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
   

    def form_valid(self,form):
        form.instance.user = self.request.user
        return super().form_valid(form)


    def get_success_url(self):
        messages.success(self.request, 'Email Added')
        return '/messenger/emails/'



# Campaign Views


class CampaignListView(LoginRequiredMixin,ListView):     # Campaign List View


    template_name = "messenger/campaigns_list.html"
    context_object_name = "camps"


    def get_queryset(self):

        return Campaign.objects.filter_by(      # Same method used in email view get_queryset
            'from_email', user=self.request.user
        )

    

class CampaignDetailView(LoginRequiredMixin,DetailView):     # Campaign Detail View


    template_name = "messenger/msg_form_steps/step3.html"
    context_object_name = 'camp'


    def get_object(self):       # Get the wanted object using get_or_404 method

        pk = self.kwargs.get('pk')
        user = self.request.user
        return Campaign.objects.get_or_404( 'from_email' , pk=pk,user=user)


def CampaignDelete(request,pk):

    obj = Campaign.objects.get_or_404( 'from_email' , pk=pk,user=request.user)
    obj.delete()

    messages.success(request , 'Campaign deleted')
    return JsonResponse('Deleted',safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CampaignCreateView(LoginRequiredMixin,View):       # Campaign Genral Create View

    

    def get(self,request):      # Campaign Get Step View

        user = self.get_user()
        step = self.get_qparm('step')       # Getting which step is provided by the query parametes    
        
        
        if step == '1':     # Step 1 is for choosing to send from which email to who, context needed
            

            emails = Email.objects.filter_by( 'user'  , user=user)      # If custom we will provide the user with his custom emails to choose
            subs = Subscriber.objects.filter_by( 'user'  , user=user)    # List of subscribers to choose

            if emails.count() == 0 :    # If he doesnot have an email, he has to create one first
                return redirect('messenger:email-create')

            elif subs.count() == 0 :
                
                messages.info(request, 'You should have at least one subscriber')
                return redirect('messenger:subscribers')


            context = { 'emails' : emails , 'subs' : subs , 'step':step }

        else:

            try:
                camp = self.get_queryset()
            except:
                return redirect('/messenger/campaign-create/?step=1')

            if step == '2':   
                
                msg = camp.message
                context = { 'type' : msg.type , 'camp_id' : camp.id, 'body' : msg.body , 'step':step}

            elif step == '3':

                context = { 'camp' : camp , 'step':step}

            else:
                return HttpResponseNotFound('Page Not Found')


        return render(request,f'messenger/msg_form_steps/step{step}.html',context)

    
    def post(self,request):     # Campaign Post View

        user = self.get_user()
        step = self.get_qparm('step')
        camp_id = self.get_qparm('camp')

        if step == '1':   
            
            data = request.POST
            
            email = Email.objects.get_or_404( 'user' , id = data.get('email') , user = user)
            camp , created = Campaign.objects.get_or_create(  
                user = user,
                from_email = email,
                completed = False
            )

            camp.to_emails.set(data.get('subs'))  

            msg , created = Message.objects.get_or_create(
                camp = camp,
            )

            msg.subject = data.get('subject')

            if msg.type != data.get('type'):
                msg.body = ''
                msg.type = data.get('type')
            msg.save()
            
                 
            return redirect(f'/messenger/campaign-create/?step=2&camp={str(camp.id)}' )   
        
        elif step == '2':

            data = json.loads(request.body)
            
            camp = self.get_queryset()

            msg = camp.message
            msg.body = data['body']
            msg.save()

            return JsonResponse(str(camp_id), safe=False)
            
        elif step == '3':

            camps = Campaign.objects.filter_by( 'from_email' , id = camp_id , user = user , completed = False )
            camp = camps.last()

            camps.update(
                completed = True,
                status = 'p',
                date_sent = timezone.now().date()
            ) 

            camp.refresh_from_db()

            send_mail_async_task.delay(str(camp.id))  
            return redirect('messenger:success-campaign-sent')

        else:
            return HttpResponseNotFound('Page Not Found')
    
    
    def get_qparm(self,key):  # Get query parameters

        q = dict(self.request.GET)
        
        try:
            return q[key][0]
        except:
            return None


    def get_queryset(self):

        camp_id = self.get_qparm('camp')

        return Campaign.objects.get_or_404(
                'user',
                id = camp_id,
                user= self.get_user(),
                completed = False
            )


    def get_user(self):
        return self.request.user


# Subscribers Views


class SubscriberView(LoginRequiredMixin,View):  # Subscriber General View
    

    def get(self,request):      # Subscriber List View

        subs = self.get_queryset()

        context = { 'subs' : subs }
        return render(request,"messenger/subs_list.html",context)


    def delete(self,request,pk):   # Subscriber Delete View

        sub = Subscriber.objects.get_or_404('user'  , user=self.get_user(), pk=pk)

        sub.delete()
        return JsonResponse("Deleted",safe=False)


    def get_queryset(self,**kwargs):

        user = self.get_user()

        return Subscriber.objects.filter_by(
            'user'  , user=user, **kwargs
        )

    def get_user(self):
        return self.request.user



class SubscriberJoinView(CreateView):   # Subscriber Join Form View

    form_class = SubscriberForm
    template_name = 'messenger/sub_form.html'


    def get_context_data(self, **kwargs):     
        
        context = super().get_context_data(**kwargs)
        context['user'] = self.get_object()  # Giving the username to the subscribtion form
        return context
   

    def form_valid(self,form):
        
        form.instance.user = self.get_object()
        form.instance.date_joined = timezone.now().date()
        user = self.get_object()

        if Subscriber.objects.filter(user=user, email=form.instance.email):
            messages.error(self.request, "This email already subscribed")
            return redirect(f'/messenger/subscriber-join/{user.id}')

        # SEND EMAIL CONFIRMATION

        return super().form_valid(form)


    def get_object(self):

        pk = self.kwargs.get('pk')
        return User.objects.get(pk=pk)  # Getting the user wanted


    def get_success_url(self):
        user = self.get_object()
        return f'/messenger/success-subscribed/?email={user.email}'



    

