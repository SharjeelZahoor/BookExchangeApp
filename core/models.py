from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver



class Rating(models.Model):
    exchange_request = models.ForeignKey('ExchangeRequest', on_delete=models.CASCADE, related_name='ratings', null=True)
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    stars = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rated_user.username} rated {self.stars} by {self.rated_by.username}"




class ChatMessage(models.Model):
    exchange_request = models.ForeignKey('ExchangeRequest', on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']


GENRE_CHOICES = [
    ('fiction', 'Fiction'),
    ('non-fiction', 'Non-fiction'),
    ('romance', 'Romance'),
    ('mystery', 'Mystery'),
    ('fantasy', 'Fantasy'),
    ('biography', 'Biography'),
    ('sci-fi', 'Sci-Fi'),
    ('history', 'History'),
    ('children', 'Children'),
    ('self-help', 'Self Help'),
    ('islamic', 'Islamic'),
    ('drama', 'Drama'),
    ('thriller', 'Thriller'),
    ('adventure', 'Adventure'),
    ('classic', 'Classic'),
    ('education', 'Education'),
    ('poetry', 'Poetry'),
    ('comics', 'Comics'),
    ('art', 'Art'),
    ('travel', 'Travel'),
]

CONDITION_CHOICES = [
    ('new', 'New'),
    ('like-new', 'Like New'),
    ('good', 'Good'),
    ('used', 'Used'),
    ('poor', 'Poor'),
]

STATUS_CHOICES = [
    ('available', 'Available'),
    ('reserved', 'Reserved'),
    ('exchanged', 'Exchanged'),
]


class Book(models.Model):


    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    photo = models.ImageField(upload_to='book_photos/', blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"
    
class ExchangeRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    from_book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='offered_exchanges')
    to_book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='received_exchanges')
    status = models.CharField(max_length=20, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    def average_rating(self):
        ratings = self.user.ratings_received.all()
        if ratings.exists():
            return round(sum(r.stars for r in ratings) / ratings.count(), 1)
        return None

    

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        



class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.user.username}"
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book, Wishlist, Notification

@receiver(post_save, sender=Book)
def match_book_with_wishlist(sender, instance, created, **kwargs):
    if created:
        matching_wishes = Wishlist.objects.filter(
            title__iexact=instance.title,
            notification_sent=False
        )
        for wish in matching_wishes:
            Notification.objects.create(
                user=wish.user,
                message=f"A book you wished for ('{wish.title}') has been listed!"
            )
            wish.notification_sent = True
            wish.save()
