from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.shortcuts import render, redirect
from django.views.generic import CreateView

from .forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm, \
    UserProfileForm, SentimentAnalyzerForm
from .models import History


# from transformers import pipeline


# sentiment_model = pipeline("text-classification", model="federicopascual/finetuning-sentiment-model-3000-samples")
# sentiment_model = pipeline("text-classification", model="Ghost1/bert-base-uncased-finetuned_for_sentiment_analysis1-sst2")
# sentiment_model = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment")


def index(request):
    context = {
        'segment': 'index'
    }
    return render(request, "pages/index.html", context)


class UserRegistrationView(CreateView):
    template_name = 'accounts/auth-signup.html'
    form_class = RegistrationForm
    success_url = '/accounts/login/'


class UserLoginView(LoginView):
    template_name = 'accounts/auth-signin.html'
    form_class = LoginForm


class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/auth-reset-password.html'
    form_class = UserPasswordResetForm


class UserPasswrodResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/auth-password-reset-confirm.html'
    form_class = UserSetPasswordForm


class UserPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/auth-change-password.html'
    form_class = UserPasswordChangeForm


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')


@login_required(login_url='/accounts/login/')
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=request.user)

    context = {
        'segment': 'profile',
        'form': form,
    }
    return render(request, 'pages/profile.html', context)


@login_required(login_url='/accounts/login/')
def sample_page(request):
    sentiment_response = None
    sentiment_sores = {
        '1 star': 'Strongly Negative',
        '2 stars': 'Negative',
        '3 stars': 'Neutral',
        '4 stars': 'Positive',
        '5 stars': 'Strongly Positive',
    }
    if request.method == 'POST':
        form = SentimentAnalyzerForm(request.POST, instance=History())
        if form.is_valid():
            sentiment = sentiment_analyzer(form.cleaned_data['text_data'])
            sentiment_response = sentiment_sores.get(sentiment['label'], 'Neutral')
    else:
        form = SentimentAnalyzerForm(instance=History())

    context = {
        'segment': 'sample_page',
        'form': form,
        'sentiments': list(sentiment_sores.values()),
        'sentiment_response': sentiment_response,
    }
    return render(request, 'pages/sample-page.html', context)


# @login_required(login_url='/accounts/login/')
# def sample_page(request):
#     sentiment_response = None
#     sentiment_sores = {
#         'Strongly Negative': -0.75,
#         'Negative': -0.15,
#         'Neutral': 0.15,
#         'Positive': 0.75,
#         'Strongly Positive': 1,
#     }
#     if request.method == 'POST':
#         form = SentimentAnalyzerForm(request.POST, instance=History())
#         if form.is_valid():
#             sentiment = sentiment_analyzer(form.cleaned_data['text_data'])
#             sentiment_score = sentiment['score']
#             if sentiment['label'] == 'LABEL_0':
#                 sentiment_score *= -1
#
#             for sentiment, score in sentiment_sores.items():
#                 if sentiment_score <= score:
#                     sentiment_response = sentiment
#                     break
#             else:
#                 sentiment_response = 'Neutral'
#     else:
#         form = SentimentAnalyzerForm(instance=History())
#
#     context = {
#         'segment': 'sample_page',
#         'form': form,
#         'sentiments': list(sentiment_sores),
#         'sentiment_response': sentiment_response,
#     }
#     return render(request, 'pages/sample-page.html', context)


def sentiment_analyzer(input_text):
    # model_path = "./fine_tuned_model"
    # tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
    # model = DistilBertForSequenceClassification.from_pretrained(model_path)
    # sentiment_model = pipeline("text-classification", model=model, tokenizer=tokenizer)
    global sentiment_model
    resp = sentiment_model(input_text)
    print(resp)
    return resp[0]
