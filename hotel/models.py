from django.db import models
from django.db.models import F
from django.db.models import signals
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.urls import reverse
from PIL import Image

try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    followed = models.ManyToManyField(User, related_name='followed', default=None, blank=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 400 or img.width > 225:
            output_size = (400, 225)
            img.thumbnail(output_size)
            img.save(self.image.path)

    @property
    def num_follows(self):
        return self.followed.all().count()



class Contact(models.Model):
    PURPOSE_CHOICES = [
        ('IN', 'Inquiry'),
        ('CO', 'Complaint'),
        ('FB', 'Feedback'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.TextField()



class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    liked = models.ManyToManyField(User, related_name='liked', default=None, blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('hotel:blog')

    @property
    def num_likes(self):
        return self.liked.all().count()



LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike'),
)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, default='Like', max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.post)



FOLLOW_CHOICES = (
    ('Follow', 'Follow'),
    ('Unfollow', 'Unfollow'),
)

class Follow(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    target = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    value = models.CharField(choices=FOLLOW_CHOICES, default='Follow', max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'target')

    def __str__(self):
        return f'{self.user} following {self.target}'



class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=160)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def print_self(self):
        print(self.text)

    @property
    def activity_object_attr(self):
        return self

    def save(self):
        self.create_hashtags()
        super(Tweet, self).save()

    def create_hashtags(self):
        hashtag_set = set(self.parse_hashtags())
        for hashtag in hashtag_set:
            h, created = Hashtag.objects.get_or_create(name=hashtag)
            h.save()
        Hashtag.objects.filter(name__in=hashtag_set).update(occurrences=F('occurrences')+1)

    def parse_hashtags(self):
        return [slugify(i) for i in self.text.split() if i.startswith("#")]

    def parse_mentions(self):
        mentions = [slugify(i) for i in self.text.split() if i.startswith("@")]
        return User.objects.filter(username__in=mentions)

    def parse_all(self):
        parts = self.text.split()
        hashtag_counter = 0
        mention_counter = 0
        result = {"parsed_text": "", "hashtags": [], "mentions": []}
        for index, value in enumerate(parts):
            if value.startswith("#"):
                parts[index] = "{hashtag" + str(hashtag_counter) + "}"
                hashtag_counter += 1
                result[u'hashtags'].append(slugify(value))
            if value.startswith("@"):
                parts[index] = "{mention" + str(mention_counter) + "}"
                mention_counter += 1
                result[u'mentions'].append(slugify(value))
        result[u'parsed_text'] = " ".join(parts)
        return result

    @property
    def activity_notify(self):
        targets = [feed_manager.get_news_feeds(self.user_id)['timeline']]
        for hashtag in self.parse_hashtags():
            targets.append(feed_manager.get_feed('user', 'hash_%s' % hashtag))
        for user in self.parse_mentions():
            targets.append(feed_manager.get_news_feeds(user.id)['timeline'])
        return targets



class MessageManager(models.Manager):

    def inbox_for(self, user):

        return self.filter(
            recipient=user,
            recipient_deleted_at__isnull=True,
        )

    def outbox_for(self, user):

        return self.filter(
            sender=user,
            sender_deleted_at__isnull=True,
        )

    def trash_for(self, user):

        return self.filter(
            recipient=user,
            recipient_deleted_at__isnull=False,
        ) | self.filter(
            sender=user,
            sender_deleted_at__isnull=False,
        )



@python_2_unicode_compatible
class Message(models.Model):
    subject = models.CharField("Subject", max_length=140)
    body = models.TextField("Body")
    sender = models.ForeignKey(User, related_name='sent_messages', verbose_name="Sender", on_delete=models.PROTECT)
    recipient = models.ForeignKey(User, related_name='received_messages', null=True, blank=True, verbose_name="Recipient", on_delete=models.SET_NULL)
    parent_msg = models.ForeignKey('self', related_name='next_messages', null=True, blank=True, verbose_name="Parent message", on_delete=models.SET_NULL)
    sent_at = models.DateTimeField("sent at", null=True, blank=True)
    read_at = models.DateTimeField("read at", null=True, blank=True)
    replied_at = models.DateTimeField("replied at", null=True, blank=True)
    sender_deleted_at = models.DateTimeField("Sender deleted at", null=True, blank=True)
    recipient_deleted_at = models.DateTimeField("Recipient deleted at", null=True, blank=True)

    objects = MessageManager()

    def new(self):
        """returns whether the recipient has read the message or not"""
        if self.read_at is not None:
            return False
        return True

    def replied(self):
        """returns whether the recipient has written a reply to this message"""
        if self.replied_at is not None:
            return True
        return False

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('hotel:messages_detail', args=[self.id])

    def save(self, **kwargs):
        if not self.id:
            self.sent_at = timezone.now()
        super(Message, self).save(**kwargs)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Message"
        verbose_name_plural = "Messages"



def inbox_count_for(user):

    return Message.objects.filter(recipient=user, read_at__isnull=True, recipient_deleted_at__isnull=True).count()


from .utils import new_message_email
signals.post_save.connect(new_message_email, sender=Message)