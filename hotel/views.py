from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ContactForm, LoginForm, ComposeForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.utils import timezone
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse
    from django.conf import settings
from django.views.generic import (
    View,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView
)
from .models import Post, Profile, Tweet, Follow, Like, Message
from .utils import (get_next, get_people_user_follows, 
                             get_people_following_user, get_mutual_followers,
                            format_quote, get_username_field)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'hotel/auth/register.html', {'form': form})



@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    qs = get_object_or_404(Profile, user=user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile', username=username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile) 

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user' : user,
        'qs' : qs,
        }

    return render(request, 'hotel/profile.html', context)



def like_post(request, **kwargs):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj= Post.objects.get(id=post_id)

        if user in post_obj.liked.all():
            post_obj.liked.remove(user)
        else:
            post_obj.liked.add(user)

        like, created = Like.objects.get_or_create(user=user, post_id=post_id)

        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
        like.save()

    return redirect('hotel:post-detail', pk=post_id, **kwargs)



@login_required
def follow(request, username):
    r_user = request.user
    user = get_object_or_404(User, username=username)
    obj = Profile.objects.get(user=user)

    if r_user not in obj.followed.all():
        obj.followed.add(r_user)

    created, follow = Follow.objects.get_or_create(user=r_user, target=user)

    if not created:
        if created.value == 'Unfollow':
            created.value = 'Follow'
    created.save()
        
    return redirect('profile', username=username)
    
    
   
@login_required
def unfollow(request, username):
    r_user = request.user
    user = get_object_or_404(User, username=username)
    obj = Profile.objects.get(user=user)

    if r_user in obj.followed.all():
        obj.followed.remove(r_user)

    try:
        created = Follow.objects.get(user=r_user, target=user)
        created.delete()
        deleted = True
    except Follow.DoesNotExist:
        deleted = False

    return redirect('profile', username=username)



def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, email, ['ciapivan@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            messages.success(request, 'Your email has been sent!')
            return redirect('hotel:contact')
    else:
        form = ContactForm()
        
    return render(request, "hotel/contact.html", {'form': form})



class PostListView(ListView):
    model = Post
    template_name = 'hotel/blog.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5



class UserPostListView(ListView):
    model = Post
    template_name = 'hotel/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')



class PostDetailView(DetailView):
    model = Post



class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(PostCreateView, self).form_valid(form)



class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False



class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_success_url(self):
        return reverse('hotel:blog')



class IndexView(TemplateView):
    template_name = 'hotel/index.html'
    

class MessagesView(TemplateView):
    template_name = 'hotel/messages.html'


class NotificationsView(TemplateView):
    template_name = 'hotel/notifications.html'
    

class About_usView(TemplateView):
    template_name = 'hotel/about_us.html'


class StayView(TemplateView):
    template_name = 'hotel/stay.html'
    

class GalleryView(TemplateView):
    template_name = 'hotel/gallery.html'


class Unforgettable_locationView(TemplateView):
    template_name = 'hotel/unforgettable_location.html'


class Extraordinary_momentsView(TemplateView):
    template_name = 'hotel/extraordinary_moments.html'


class Exciting_attractionsView(TemplateView):
    template_name = 'hotel/exciting_attractions.html'


class Unbelievable_offersView(TemplateView):
    template_name = 'hotel/unbelievable_offers.html'



@login_required
def inbox(request, template_name='hotel/messages/inbox.html'):
    message_list = Message.objects.inbox_for(request.user)

    return render(request, template_name, {'message_list': message_list})



@login_required
def outbox(request, template_name='hotel/messages/outbox.html'):
    message_list = Message.objects.outbox_for(request.user)

    return render(request, template_name, {'message_list': message_list})



@login_required
def trash(request, template_name='hotel/messages/trash.html'):
    message_list = Message.objects.trash_for(request.user)

    return render(request, template_name, {'message_list': message_list})



@login_required
def compose(request, recipient=None, form_class=ComposeForm,
        template_name='hotel/messages/compose.html', success_url=None,
        recipient_filter=None):
    """
    ``recipient_filter``: a function which receives a user object and
                              returns a boolean wether it is an allowed
                              recipient or not
    Passing GET parameter ``subject`` to the view allows pre-filling the
    subject field of the form.
    """
    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST, recipient_filter=recipient_filter)
        if form.is_valid():
            form.save(sender=request.user)
            messages.info(request, u"Message successfully sent.")
            if success_url is None:
                success_url = reverse('hotel:messages_inbox')
            if 'next' in request.GET:
                success_url = request.GET['next']
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(initial={"subject": request.GET.get("subject", "")})
        if recipient is not None:
            recipients = [u for u in User.objects.filter(**{'%s__in' % get_username_field(): [r.strip() for r in recipient.split('+')]})]
            form.fields['recipient'].initial = recipients
    return render(request, template_name, {'form': form})

@login_required
def reply(request, message_id, form_class=ComposeForm,
        template_name='hotel/messages/compose.html', success_url=None,
        recipient_filter=None, quote_helper=format_quote,
        subject_template=(u"Re: %(subject)s"),):
    """
    Prepares the ``form_class`` form for writing a reply to a given message
    (specified via ``message_id``). Uses the ``format_quote`` helper from
    ``messages.utils`` to pre-format the quote. To change the quote format
    assign a different ``quote_helper`` kwarg in your url-conf.
    """
    parent = get_object_or_404(Message, id=message_id)

    if parent.sender != request.user and parent.recipient != request.user:
        raise Http404

    if request.method == "POST":
        sender = request.user
        form = form_class(request.POST, recipient_filter=recipient_filter)
        if form.is_valid():
            form.save(sender=request.user, parent_msg=parent)
            messages.info(request, u"Message successfully sent.")
            if success_url is None:
                success_url = reverse('hotel:messages_inbox')
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(initial={
            'body': quote_helper(parent.sender, parent.body),
            'subject': subject_template % {'subject': parent.subject},
            'recipient': [parent.sender,]
            })
    return render(request, template_name, {'form': form})

@login_required
def delete(request, message_id, success_url=None):
    """
    Marks a message as deleted by sender or recipient. The message is not
    really removed from the database, because two users must delete a message
    before it's save to remove it completely.
    A cron-job should prune the database and remove old messages which are
    deleted by both users.
    As a side effect, this makes it easy to implement a trash with undelete.
    You can pass ?next=/foo/bar/ via the url to redirect the user to a different
    page (e.g. `/foo/bar/`) than ``success_url`` after deletion of the message.
    """
    user = request.user
    now = timezone.now()
    message = get_object_or_404(Message, id=message_id)
    deleted = False
    if success_url is None:
        success_url = reverse('hotel:messages_inbox')
    if 'next' in request.GET:
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = now
        deleted = True
    if message.recipient == user:
        message.recipient_deleted_at = now
        deleted = True
    if deleted:
        message.save()
        messages.info(request, u"Message successfully deleted.")
        return HttpResponseRedirect(success_url)
    raise Http404

@login_required
def undelete(request, message_id, success_url=None):
    """
    Recovers a message from trash. This is achieved by removing the
    ``(sender|recipient)_deleted_at`` from the model.
    """
    user = request.user
    message = get_object_or_404(Message, id=message_id)
    undeleted = False
    if success_url is None:
        success_url = reverse('hotel:messages_inbox')
    if 'next' in request.GET:
        success_url = request.GET['next']
    if message.sender == user:
        message.sender_deleted_at = None
        undeleted = True
    if message.recipient == user:
        message.recipient_deleted_at = None
        undeleted = True
    if undeleted:
        message.save()
        messages.info(request, u"Message successfully recovered.")
        return HttpResponseRedirect(success_url)
    raise Http404

@login_required
def view(request, message_id, form_class=ComposeForm, quote_helper=format_quote,
        subject_template=(u"Re: %(subject)s"),
        template_name='hotel/messages/view.html'):
    """
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either
    the sender or the recipient. If the user is not allowed a 404
    is raised.
    If the user is the recipient and the message is unread
    ``read_at`` is set to the current datetime.
    If the user is the recipient a reply form will be added to the
    tenplate context, otherwise 'reply_form' will be None.
    """
    user = request.user
    now = timezone.now()
    message = get_object_or_404(Message, id=message_id)
    if (message.sender != user) and (message.recipient != user):
        raise Http404
    if message.read_at is None and message.recipient == user:
        message.read_at = now
        message.save()

    context = {'message': message, 'reply_form': None}
    if message.recipient == user:
        form = form_class(initial={
            'body': quote_helper(message.sender, message.body),
            'subject': subject_template % {'subject': message.subject},
            'recipient': [message.sender,]
            })
        context['reply_form'] = form
    return render(request, template_name, context)