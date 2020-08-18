from django.contrib.auth.models import User
from .models import Follow
import re
import django
from django.utils.text import wrap
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def get_next(request):
    """
    1. If there is a variable named ``next`` in the *POST* parameters, the
    view will redirect to that variable's value.
    2. If there is a variable named ``next`` in the *GET* parameters, the 
    view will redirect to that variable's value.
    3. If Django can determine the previous page from the HTTP headers, the 
    view will redirect to that previous page.
    
    """
    return request.POST.get('next', request.GET.get('next', 
        request.META.get('HTTP_REFERER', None)))


def get_people_user_follows(user):
    """
    Returns a ``QuerySet`` representing the users that the given user follows.
    
    """
    ul = Follow.objects.filter(from_user=user).values_list('user', 
        flat=True)
    return User.objects.filter(id__in=ul)


def get_people_following_user(user):
    """
    Returns a ``QuerySet`` representing the users that follow the given user.
    
    """
    ul = Follow.objects.filter(to_user=user).values_list('target', 
        flat=True)
    return User.objects.filter(id__in=ul)


def get_mutual_followers(user):
    """
    Returns a ``QuerySet`` representing the users that the given user follows,
    who also follow the given user back.
    
    """
    follows = Follow.objects.filter(from_user=user).values_list('user',
        flat=True)
    following = Follow.objects.filter(to_user=user).values_list('target',
        flat=True)
    return User.objects.filter(
        id__in=set(follows).intersection(set(following)))



def format_quote(sender, body):
    """
    Wraps text at 55 chars and prepends each
    line with `> `.
    Used for quoting messages in replies.
    """
    lines = wrap(body, 55).split('\n')
    for i, line in enumerate(lines):
        lines[i] = "> %s" % line
    quote = '\n'.join(lines)
    return u"%(sender)s wrote:\n%(body)s" % {
        'sender': sender,
        'body': quote
    }

def format_subject(subject):
    """
    Prepends 'Re:' to the subject. To avoid multiple 'Re:'s
    a counter is added.
    NOTE: Currently unused. First step to fix Issue #48.
    FIXME: Any hints how to make this i18n aware are very welcome.
    """
    subject_prefix_re = r'^Re\[(\d*)\]:\ '
    m = re.match(subject_prefix_re, subject, re.U)
    prefix = u""
    if subject.startswith('Re: '):
        prefix = u"[2]"
        subject = subject[4:]
    elif m is not None:
        try:
            num = int(m.group(1))
            prefix = u"[%d]" % (num+1)
            subject = subject[6+len(str(num)):]
        except:
            # if anything fails here, fall back to the old mechanism
            pass

    return ugettext(u"Re%(prefix)s: %(subject)s") % {
        'subject': subject,
        'prefix': prefix
    }

def new_message_email(sender, instance, signal,
        subject_prefix=u'New Message: %(subject)s',
        template_name="hotel/messages/new_message.html",
        default_protocol=None,
        *args, **kwargs):
    """
    This function sends an email and is called via Django's signal framework.
    Optional arguments:
        ``template_name``: the template to use
        ``subject_prefix``: prefix for the email subject.
        ``default_protocol``: default protocol in site URL passed to template
    """
    if default_protocol is None:
        default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')

    if 'created' in kwargs and kwargs['created']:
        try:
            from django.contrib.sites.models import Site
            current_domain = Site.objects.get_current().domain
            subject = subject_prefix % {'subject': instance.subject}
            message = render_to_string(template_name, {
                'site_url': '%s://%s' % (default_protocol, current_domain),
                'message': instance,
            })
            if instance.recipient.email != "":
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                    [instance.recipient.email,])
        except Exception as e:
            #print e
            pass #fail silently



def get_username_field():
    if django.VERSION[:2] >= (1, 5):
        return User.USERNAME_FIELD
    else:
        return 'username'
