"""
URL configuration for adhd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from adhdApp.views import *


urlpatterns = [
    path('',index),
    path('login_page/',login_page,name='login_page'),
    path('login/',login,name='login'),
    path('register_page/',register_page,name='register_page'),
    path('register/',register,name='register'),
    path('logout/',logout,name='logout'),
    path('index/',index,name='index'),
    path('home_page/',home_page,name='home_page'),
    path('profile/',profile,name='profile'),
    path('story_page/',story_page,name='story_page'),
    path('dashboard_page/',dashboard_page,name='dashboard_page'),
    path('avatar_page/',avatar_page,name='avatar_page'),
    path('learn_page/',learn_page,name='learn_page'),
    path('exercise_page/',exercise_page,name='exercise_page'),
    path('learn_page/',learn_page,name='learn_page'),
    path('learn_page/',learn_page,name='learn_page'),
    path('learn_page/',learn_page,name='learn_page'),
    path('upload_story/',upload_story,name='upload_story'),
    path('math_page/',math_page,name='math_page'),
    path('english_page/',english_page,name='english_page'),
    path('cognitive_page/',cognitive_page,name='cognitive_page'),
    path('mathtest_page/',mathtest_page,name='mathtest_page'),
    path('englishtest_page/',englishtest_page,name='englishtest_page'),
    path('cognitivetest_page/',cognitivetest_page,name='cognitivetest_page'),
    path('generate_audio/',generate_audio,name='generate_audio'),  
    path('get_story/',get_story,name='get_story') ,
    path('qg/',qg,name="qg"),
    path('generate_mcq/',generate_mcq,name="generate_mcq"),
    path('get_latest_quiz/',get_latest_quiz,name="get_latest_quiz"),
    path("submit_english_quiz/", submit_english_quiz, name="submit_english_quiz"),
    path("submit_maths_quiz/", submit_maths_quiz, name="submit_maths_quiz"),
    path("submit_quiz/", submit_quiz, name="submit_quiz"),
    path('get_user_scores/', get_user_scores, name='get_user_scores'),
]