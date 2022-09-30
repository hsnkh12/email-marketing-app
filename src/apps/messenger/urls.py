from django.urls import path
from django.views.generic import TemplateView
from .views import *
from .httpres import *

app_name = 'messenger'

urlpatterns = [
    
    path('',TemplateView.as_view( template_name = 'messenger/main.html'),name="messenger-main"),

    path('campaigns/',CampaignListView.as_view(),name="campaigns"),
    path('campaigns/<pk>',CampaignDetailView.as_view(),name="campaign-detail"),
    path('campaign-create/',CampaignCreateView.as_view(),name="campaign-create"),
    path('campaign-delete/<pk>',CampaignDelete,name="campaign-delete"),
    
    path('emails/',EmailView.as_view(),name="emails"),
    path('emails/<pk>',EmailView.as_view(),name="email-detail"),
    path('email-create/',EmailCreateView.as_view(),name="email-create"),

    path('subscribers/',SubscriberView.as_view(),name="subscribers"),
    path('subscribers/<pk>',SubscriberView.as_view(),name="subscriber-detail"),
    path('subscriber-join/<pk>',SubscriberJoinView.as_view(),name="subscribers"),

    path('success-subscribed/',SuccessSubscribed,name='success-subscribed'),
    path('success-campaign-sent/',SuccessMessageSent,name='success-campaign-sent'),
]