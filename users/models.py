from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal

class User(AbstractUser):
    """Custom User Model with wallet functionality"""
    
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    
    # Wallet
    wallet_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="User's wallet balance in USDT"
    )
    usdt_address = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="User's USDT wallet address"
    )
    
    # Game Statistics
    total_games_played = models.IntegerField(default=0)
    total_games_won = models.IntegerField(default=0)
    total_amount_won = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount_lost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Profile
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    country = models.CharField(max_length=50, blank=True)
    
    # Account Status
    is_verified = models.BooleanField(default=False)
    kyc_verified = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
        ]
    
    def __str__(self):
        return self.username
    
    @property
    def win_rate(self):
        """Calculate win rate percentage"""
        if self.total_games_played == 0:
            return 0
        return round((self.total_games_won / self.total_games_played) * 100, 2)
    
    @property
    def profit_loss(self):
        """Calculate total profit/loss"""
        return self.total_amount_won - self.total_amount_lost
    
    def can_place_bet(self, amount):
        """Check if user has sufficient balance"""
        return self.wallet_balance >= amount
    
    def add_balance(self, amount):
        """Add money to wallet"""
        self.wallet_balance += Decimal(str(amount))
        self.save()
    
    def deduct_balance(self, amount):
        """Deduct money from wallet"""
        if self.can_place_bet(amount):
            self.wallet_balance -= Decimal(str(amount))
            self.save()
            return True
        return False


class UserActivity(models.Model):
    """Track user activity logs"""
    ACTIVITY_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('bet_placed', 'Bet Placed'),
        ('game_won', 'Game Won'),
        ('game_lost', 'Game Lost'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('profile_update', 'Profile Update'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "User Activities"
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.created_at}"
