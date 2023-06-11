from datetime import datetime, timedelta

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views.generic import CreateView

from .forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm, \
    UserProfileForm, SentimentAnalyzerForm
from .models import History


from transformers import pipeline


# sentiment_model = pipeline("text-classification", model="federicopascual/finetuning-sentiment-model-3000-samples")
# sentiment_model = pipeline("text-classification", model="Ghost1/bert-base-uncased-finetuned_for_sentiment_analysis1-sst2")
sentiment_model = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment")


def index(request):
    context = {
        'segment': 'index',
        'history': get_history(request, periods=['day', 'week', 'month']),
        'delete_redirect': False,
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


def get_history(request, periods=[]):
    response = {}
    if not request.user.is_authenticated:
        return response

    now_date = datetime.now()
    if 'day' in periods:
        history = request.user.history_set.filter(
            created_at__gte=datetime(year=now_date.year, month=now_date.month, day=now_date.day)
        ).order_by('-created_at')[:10]
        if history:
            response['Today'] = history
    if 'week' in periods:
        history = request.user.history_set.filter(
            created_at__gte=datetime(year=now_date.year, month=now_date.month, day=now_date.day) - timedelta(days=6)
        ).order_by('-created_at')[:30]
        if history:
            response['Week'] = history
    if 'month' in periods:
        history = request.user.history_set.filter(
            created_at__gte=datetime(year=now_date.year, month=now_date.month, day=now_date.day) - timedelta(days=30)
        ).order_by('-created_at')[:100]
        if history:
            response['Month'] = history

    return response


@login_required(login_url='/accounts/login/')
def sentiment_analyzer(request):
    sentiment_sores = {
        '1 star': 'Strongly Negative',
        '2 stars': 'Negative',
        '3 stars': 'Neutral',
        '4 stars': 'Positive',
        '5 stars': 'Strongly Positive',
    }
    sentiment_response = None
    form = None
    if request.method == 'POST':
        form = SentimentAnalyzerForm(request.POST, instance=History())
        if form.is_valid():
            text_data = form.cleaned_data['text_data']
            sentiment = analyzer(text_data)
            sentiment_response = sentiment_sores.get(sentiment['label'], 'Neutral')
            if request.POST.get('save_analise', 'off') == 'on':
                History.objects.create(user=request.user, text_data=text_data, sentiment=sentiment_response)
    elif request.GET.get('history_id'):
        try:
            obj = History.objects.get(id=request.GET['history_id'])
            form = SentimentAnalyzerForm(instance=obj)
            sentiment_response = obj.sentiment
        except ObjectDoesNotExist:
            pass

    if not form:
        form = SentimentAnalyzerForm(instance=History())

    context = {
        'segment': 'sentiment_analyzer',
        'form': form,
        'sentiments': list(sentiment_sores.values()),
        'sentiment_response': sentiment_response,
        'history': get_history(request, periods=['day']),
        'delete_redirect': True,
    }
    return render(request, 'pages/sentiment-analyzer.html', context)


@login_required(login_url='/accounts/login/')
def delete_history(request, history_id):
    try:
        obj = History.objects.get(id=history_id)
        if obj.user.id == request.user.id:
            obj.delete()
    except ObjectDoesNotExist:
        pass
    finally:
        if request.META.get('HTTP_REFERER'):
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect('sentiment_analyzer')


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
#             sentiment = analyzer(form.cleaned_data['text_data'])
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


def analyzer(input_text):
    # model_path = "./fine_tuned_model"
    # tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
    # model = DistilBertForSequenceClassification.from_pretrained(model_path)
    # sentiment_model = pipeline("text-classification", model=model, tokenizer=tokenizer)
    global sentiment_model
    resp = sentiment_model(input_text)
    print(resp)
    return resp[0]
