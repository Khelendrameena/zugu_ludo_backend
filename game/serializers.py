from rest_framework import serializers
from .models import (
    GameRoom, GamePlayer, GameMove, Transaction,
    Tournament, TournamentParticipant, PlatformSettings
)
from users.serializers import UserProfileSerializer

class GamePlayerSerializer(serializers.ModelSerializer):
    """Serializer for Game Player"""
    user = UserProfileSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = GamePlayer
        fields = [
            'id', 'user', 'username', 'color', 'position',
            'bet_paid', 'is_winner', 'joined_at'
        ]


class GameRoomSerializer(serializers.ModelSerializer):
    """Serializer for Game Room"""
    players = GamePlayerSerializer(many=True, read_only=True)
    winner_username = serializers.CharField(source='winner.username', read_only=True)
    
    class Meta:
        model = GameRoom
        fields = [
            'id', 'room_id', 'bet_amount', 'commission_percentage',
            'total_pool', 'commission_amount', 'winner_amount',
            'status', 'max_players', 'current_players',
            'players', 'winner', 'winner_username',
            'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'room_id', 'total_pool', 'commission_amount',
            'winner_amount', 'current_players', 'winner',
            'created_at', 'started_at', 'completed_at'
        ]


class GameMoveSerializer(serializers.ModelSerializer):
    """Serializer for Game Move"""
    player_username = serializers.CharField(source='player.user.username', read_only=True)
    player_color = serializers.CharField(source='player.color', read_only=True)
    
    class Meta:
        model = GameMove
        fields = [
            'id', 'player', 'player_username', 'player_color',
            'dice_value', 'piece_moved', 'from_position',
            'to_position', 'move_number', 'timestamp'
        ]


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    room_id = serializers.CharField(source='game_room.room_id', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'user_username', 'room_id',
            'transaction_type', 'amount', 'status', 'usdt_tx_hash',
            'description', 'created_at'
        ]
        read_only_fields = ['transaction_id', 'created_at']


class TournamentSerializer(serializers.ModelSerializer):
    """Serializer for Tournament"""
    participants_count = serializers.IntegerField(source='current_participants', read_only=True)
    winner_username = serializers.CharField(source='winner.username', read_only=True)
    
    class Meta:
        model = Tournament
        fields = [
            'id', 'tournament_id', 'name', 'description',
            'entry_fee', 'prize_pool', 'max_participants',
            'participants_count', 'status', 'start_date',
            'end_date', 'winner', 'winner_username', 'created_at'
        ]
        read_only_fields = ['tournament_id', 'prize_pool', 'created_at']


class TournamentParticipantSerializer(serializers.ModelSerializer):
    """Serializer for Tournament Participant"""
    user = UserProfileSerializer(read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    
    class Meta:
        model = TournamentParticipant
        fields = [
            'id', 'tournament', 'tournament_name', 'user',
            'games_played', 'games_won', 'total_points',
            'rank', 'joined_at'
        ]


class PlatformSettingsSerializer(serializers.ModelSerializer):
    """Serializer for Platform Settings"""
    
    class Meta:
        model = PlatformSettings
        fields = [
            'id', 'commission_percentage', 'min_bet_amount',
            'max_bet_amount', 'usdt_contract_address',
            'maintenance_mode', 'updated_at'
        ]
