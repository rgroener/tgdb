from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from .models import Author, Tag, Category, Post
from django.contrib import messages
from .forms import FeedbackForm
from django.core.mail import mail_admins
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django_project import helpers

def index(request):
		return HttpResponse("Hello Django")

def post_list(request):
    posts = Post.objects.order_by("-id").all()
    paginator = Paginator(posts, 10)

    # get the page parameter from the query string
    # if page parameter is available get() method will return empty string ''
    page = request.GET.get('page')

    try:
        # create Page object for the given page
        posts = paginator.page(page)
    except PageNotAnInteger:
        # if page parameter in the query string is not available, return the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if the value of the page parameter exceeds num_pages then return the last page
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post_list.html', {'posts': posts})
	
def post_detail(request, pk): 
	post = get_object_or_404(Post, pk=pk)
	return render(request, 'blog/post_detail.html', {'post': post})
    
# view function to display post by category
def post_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    posts = get_list_or_404(Post.objects.order_by("-id"), category=category)
    posts = helpers.pg_records(request, posts, 5)
    context = {
        'category': category,
        'posts': posts
    }
    return render(request, 'blog/post_by_category.html', context)


# view function to display post by tag
def post_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = get_list_or_404(Post.objects.order_by("-id"), tags=tag)
    posts = helpers.pg_records(request, posts, 5)
    context = {
        'tag': tag,
        'posts': posts
    }
    return render(request, 'blog/post_by_tag.html', context )

def test_redirect(request):
    c = Category.objects.get(name='python')
    return redirect(c)

def feedback(request):
    if request.method == 'POST':
        f = FeedbackForm(request.POST)

        if f.is_valid():
            name = f.cleaned_data['name']
            sender = f.cleaned_data['email']
            subject = "You have a new Feedback from {}:{}".format(name, sender)
            message = "Subject: {}\n\nMessage: {}".format(f.cleaned_data['subject'], f.cleaned_data['message'])
            mail_admins(subject, message)

            f.save()
            messages.add_message(request, messages.INFO, 'Feedback Submitted.')
            return redirect('feedback')

    else:
        f = FeedbackForm()
    return render(request, 'blog/feedback.html', {'form': f})

def test_cookie(request):   
    if not request.COOKIES.get('color'):
        response = HttpResponse("Cookie Set")
        response.set_cookie('color', 'blue')
        return response
    else:
        return HttpResponse("Your favorite color is {0}".format(request.COOKIES['color']))

def track_user(request):
    response = render(request, 'blog/track_user.html') # store the response in response variable
    if not request.COOKIES.get('visits'):        
        response.set_cookie('visits', '1', 3600 * 24 * 365 * 2)
    else:
        visits = int(request.COOKIES.get('visits', '1')) + 1
        response.set_cookie('visits', str(visits),  3600 * 24 * 365 * 2)
    return response
def stop_tracking(request):
    if request.COOKIES.get('visits'):
       response = HttpResponse("Cookies Cleared")
       response.delete_cookie("visits")
    else:
        response = HttpResponse("We are not tracking you.")
    return response
