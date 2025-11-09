from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from users.models import User, UserActivity
from .models import (
    GameRoom, GamePlayer, GameMove, Transaction,
    Tournament, TournamentParticipant, PlatformSettings
)

# User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'wallet_balance_display', 'total_games_played', 
                    'total_games_won', 'win_rate', 'is_verified', 'is_banned']
    list_filter = ['is_verified', 'kyc_verified', 'is_banned', 'created_at']
    search_fields = ['username', 'email', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Wallet Info', {'fields': ('wallet_balance', 'usdt_address')}),
        ('Game Stats', {'fields': ('total_games_played', 'total_games_won', 
                                    'total_amount_won', 'total_amount_lost')}),
        ('Profile', {'fields': ('avatar', 'bio', 'country', 'phone_number')}),
        ('Verification', {'fields': ('is_verified', 'kyc_verified', 'is_banned', 'ban_reason')}),
    )
    
    def wallet_balance_display(self, obj):
        return format_html('<b>${}</b>', obj.wallet_balance)
    wallet_balance_display.short_description = 'Wallet Balance'


# User Activity Admin
@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'ip_address', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['user', 'activity_type', 'description', 'ip_address', 
                       'user_agent', 'metadata', 'created_at']
    
    def has_add_permission(self, request):
        return False


# Game Room Admin
@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ['room_id', 'bet_amount', 'status', 'current_players', 
                    'total_pool', 'winner', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['room_id', 'winner__username']
    readonly_fields = ['room_id', 'total_pool', 'commission_amount', 
                       'winner_amount', 'created_at']
    
    fieldsets = (
        ('Room Info', {
            'fields': ('room_id', 'bet_amount', 'commission_percentage', 
                      'status', 'max_players', 'current_players')
        }),
        ('Financial', {
            'fields': ('total_pool', 'commission_amount', 'winner_amount')
        }),
        ('Game Details', {
            'fields': ('winner', 'created_at', 'started_at', 'completed_at')
        }),
    )


# Game Player Admin
@admin.register(GamePlayer)
class GamePlayerAdmin(admin.ModelAdmin):
    list_display = ['user', 'game_room', 'color', 'position', 'bet_paid', 'is_winner']
    list_filter = ['color', 'is_winner', 'bet_paid']
    search_fields = ['user__username', 'game_room__room_id']


# Game Move Admin
@admin.register(GameMove)
class GameMoveAdmin(admin.ModelAdmin):
    list_display = ['game_room', 'player', 'dice_value', 'move_number', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['game_room__room_id', 'player__user__username']
    readonly_fields = ['timestamp']


# Transaction Admin
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'user', 'transaction_type', 'amount_display', 
                    'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['transaction_id', 'user__username', 'usdt_tx_hash']
    readonly_fields = ['transaction_id', 'created_at']
    
    def amount_display(self, obj):
        color = 'green' if obj.transaction_type in ['deposit', 'win'] else 'red'
        return format_html('<span style="color: {};">${}</span>', color, obj.amount)
    amount_display.short_description = 'Amount'


# Tournament Admin
@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'entry_fee', 'prize_pool', 
                    'current_participants', 'start_date', 'winner']
    list_filter = ['status', 'start_date']
    search_fields = ['name', 'tournament_id']
    readonly_fields = ['tournament_id', 'prize_pool', 'created_at']


# Tournament Participant Admin
@admin.register(TournamentParticipant)
class TournamentParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'tournament', 'games_played', 'games_won', 
                    'total_points', 'rank']
    list_filter = ['tournament']
    search_fields = ['user__username', 'tournament__name']


# Platform Settings Admin
@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ['commission_percentage', 'min_bet_amount', 'max_bet_amount', 
                    'maintenance_mode', 'updated_at']
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not PlatformSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
