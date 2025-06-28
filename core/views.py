from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Book
from .forms import ExchangeRequestForm
from .forms import BookForm
from .models import ExchangeRequest
from .models import ChatMessage
from django.http import Http404
from django.db.models import Count, Q
from .models import Rating


from .models import Rating, ExchangeRequest
from django.contrib import messages

@login_required
def submit_rating(request, request_id):
    exchange = get_object_or_404(ExchangeRequest, id=request_id, to_user=request.user)

    if request.method == 'POST':
        stars = int(request.POST.get('stars'))
        comment = request.POST.get('comment', '').strip()
        if 1 <= stars <= 5:
            Rating.objects.create(
                exchange_request=exchange,
                rated_user=exchange.from_user,
                rated_by=request.user,
                stars=stars,
                comment=comment
            )
            messages.success(request, "Rating submitted successfully.")
        else:
            messages.error(request, "Invalid rating value.")
    return redirect('my_received_requests')


@login_required
def chat_view(request, request_id):
    exchange = get_object_or_404(ExchangeRequest, id=request_id)

    if request.user != exchange.from_user and request.user != exchange.to_user:
        raise Http404("You are not authorized to view this chat.")

    if exchange.status != 'accepted':
        raise Http404("Chat only available for accepted exchanges.")

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ChatMessage.objects.create(
                exchange_request=exchange,
                sender=request.user,
                message=message_text
            )

    # Mark all unread messages from the other user as read
    ChatMessage.objects.filter(
    exchange_request=exchange,
    is_read=False
    ).filter(~Q(sender=request.user)).update(is_read=True)

    chat_messages = exchange.messages.all()
    return render(request, 'core/chat.html', {
        'exchange': exchange,
        'chat_messages': chat_messages
    })




from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ExchangeRequest, ChatMessage

@login_required
def handle_request(request, request_id):
    req = get_object_or_404(ExchangeRequest, id=request_id, to_user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            req.status = 'accepted'
            req.save()

            # Mark the owner's book as not available
            req.to_book.status = 'not_available'
            req.to_book.save()

        elif action == 'reject':
            req.status = 'rejected'
            req.save()

    return redirect('my_received_requests')


@login_required
def my_sent_requests(request):
    my_requests = ExchangeRequest.objects.filter(from_user=request.user).annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
        )
    ).select_related('to_user__profile', 'from_book', 'to_book')

    for req in my_requests:
        existing_rating = Rating.objects.filter(
            rated_by=request.user,
            rated_user=req.from_user,
            exchange_request=req
        ).first()
        req.existing_rating = existing_rating

    

    return render(request, 'core/my_sent_requests.html', {
        'requests': my_requests
    })


@login_required
def my_received_requests(request):
    requests = ExchangeRequest.objects.filter(to_user=request.user).annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
        )
    ).select_related('from_user__profile', 'from_book', 'to_book').order_by('-requested_at')

    for req in requests:
        existing_rating = Rating.objects.filter(
            rated_by=request.user,
            rated_user=req.from_user,
            exchange_request=req
        ).first()
        req.existing_rating = existing_rating

    return render(request, 'core/my_received_requests.html', {
        'requests': requests
    })



@login_required
def request_exchange(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    user_books = Book.objects.filter(owner=request.user, status='available').exclude(id=book.id)

    if request.method == 'POST':
        form = ExchangeRequestForm(request.POST, user=request.user)
        if form.is_valid():
            exchange = form.save(commit=False)
            exchange.from_user = request.user
            exchange.to_user = book.owner
            exchange.to_book = book
            exchange.save()
            return redirect('book_detail', book_id=book.id)
    else:
        form = ExchangeRequestForm(user=request.user)

    return render(request, 'core/request_exchange.html', {'form': form, 'book': book})

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'core/book_detail.html', {'book': book})

@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, owner=request.user)
    if request.method == 'POST':
        book.delete()
        return redirect('my_books')
    return render(request, 'core/confirm_delete.html', {'book': book})

@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, owner=request.user)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('my_books')
    else:
        form = BookForm(instance=book)

    return render(request, 'core/add_book.html', {'form': form, 'edit_mode': True})

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user  # <-- corrected here
            book.save()
            return redirect('book_list')
    else:
        form = BookForm()

    return render(request, 'core/add_book.html', {'form': form})

@login_required
def my_books(request):
    books = Book.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'core/my_books.html', {'books': books})

@login_required
def book_list(request):
    books = Book.objects.filter(status='available').exclude(owner=request.user).order_by('-created_at')
    return render(request, 'core/book_list.html', {'books': books})

@login_required
def profile(request):
    return render(request, 'core/profile.html')


@login_required
def home(request):
    query = request.GET.get('q')

    books = Book.objects.filter(status='available').exclude(owner=request.user)

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(genre__icontains=query) |
            Q(location__icontains=query)
        )

    books = books.order_by('-created_at')[:4]  # still showing only latest 4

    return render(request, 'core/home.html', {'books': books, 'query': query})


def register(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        phone = request.POST['phone']
        location = request.POST['location']
        bio = request.POST['bio']

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        # Create User
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = full_name
        user.save()

        # Update Profile
        profile = user.profile
        profile.phone = phone
        profile.location = location
        profile.bio = bio
        profile.save()

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'core/register.html')



from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Get user with this email
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
            user = authenticate(request, username=username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'core/login.html')



from django.contrib.auth import update_session_auth_hash
@login_required
def password_change_view(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if not request.user.check_password(current_password):
            messages.error(request, "Your current password is incorrect.")
            return redirect('password_change')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('password_change')

        request.user.set_password(new_password)
        request.user.save()

        update_session_auth_hash(request, request.user)  # Keeps user logged in
        messages.success(request, "Your password has been updated successfully.")
        return redirect('home')

    return render(request, 'core/password_change.html')



def logout_view(request):
    logout(request)
    return redirect('login')
