from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import GameRoom, GamePlayer, Transaction, User
from .serializers import GameRoomSerializer, GamePlayerSerializer, TransactionSerializer

class GameRoomViewSet(viewsets.ModelViewSet):
    """API for Game Room Management"""
    queryset = GameRoom.objects.all()
    serializer_class = GameRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter based on status"""
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            return self.queryset.filter(status=status_filter)
        return self.queryset

    @action(detail=False, methods=['post'])
    def create_room(self, request):
        """Create a new game room"""
        bet_amount = Decimal(request.data.get('bet_amount', 0))
        
        # Validate bet amount
        if bet_amount <= 0:
            return Response(
                {'error': 'Bet amount must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check user balance
        if request.user.wallet_balance < bet_amount:
            return Response(
                {'error': 'Insufficient balance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create game room
        game_room = GameRoom.objects.create(
            bet_amount=bet_amount,
            commission_percentage=Decimal('2.00'),  # 2% commission
            current_players=1
        )
        
        # Add creator as first player
        GamePlayer.objects.create(
            game_room=game_room,
            user=request.user,
            color='red',
            position=1,
            bet_paid=True
        )
        
        # Deduct bet from user wallet
        request.user.wallet_balance -= bet_amount
        request.user.save()
        
        # Create transaction record
        Transaction.objects.create(
            user=request.user,
            game_room=game_room,
            transaction_type='bet_placed',
            amount=bet_amount,
            status='completed',
            description=f'Bet placed for room {game_room.room_id}'
        )
        
        game_room.calculate_pool()
        
        serializer = self.get_serializer(game_room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def join_room(self, request, pk=None):
        """Join an existing game room"""
        game_room = self.get_object()
        
        # Validate room status
        if game_room.status != 'waiting':
            return Response(
                {'error': 'Room is not accepting players'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if room is full
        if game_room.current_players >= game_room.max_players:
            return Response(
                {'error': 'Room is full'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already joined
        if game_room.players.filter(user=request.user).exists():
            return Response(
                {'error': 'You have already joined this room'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check user balance
        if request.user.wallet_balance < game_room.bet_amount:
            return Response(
                {'error': 'Insufficient balance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Assign color and position
        colors = ['red', 'blue', 'green', 'yellow']
        used_colors = game_room.players.values_list('color', flat=True)
        available_color = [c for c in colors if c not in used_colors][0]
        
        with transaction.atomic():
            # Add player to room
            GamePlayer.objects.create(
                game_room=game_room,
                user=request.user,
                color=available_color,
                position=game_room.current_players + 1,
                bet_paid=True
            )
            
            # Update room
            game_room.current_players += 1
            game_room.calculate_pool()
            
            # Deduct bet from user wallet
            request.user.wallet_balance -= game_room.bet_amount
            request.user.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                game_room=game_room,
                transaction_type='bet_placed',
                amount=game_room.bet_amount,
                status='completed',
                description=f'Joined room {game_room.room_id}'
            )
            
            # Start game if room is full
            if game_room.current_players == game_room.max_players:
                game_room.status = 'in_progress'
                game_room.started_at = timezone.now()
                game_room.save()
        
        serializer = self.get_serializer(game_room)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def declare_winner(self, request, pk=None):
        """Declare winner and distribute winnings"""
        game_room = self.get_object()
        winner_user_id = request.data.get('winner_user_id')
        
        if game_room.status != 'in_progress':
            return Response(
                {'error': 'Game is not in progress'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            winner_player = game_room.players.get(user_id=winner_user_id)
        except GamePlayer.DoesNotExist:
            return Response(
                {'error': 'Winner not found in this game'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Mark winner
            winner_player.is_winner = True
            winner_player.save()
            
            # Update game room
            game_room.winner = winner_player.user
            game_room.status = 'completed'
            game_room.completed_at = timezone.now()
            game_room.save()
            
            # Credit winner
            winner_player.user.wallet_balance += game_room.winner_amount
            winner_player.user.total_games_won += 1
            winner_player.user.save()
            
            # Create win transaction
            Transaction.objects.create(
                user=winner_player.user,
                game_room=game_room,
                transaction_type='win',
                amount=game_room.winner_amount,
                status='completed',
                description=f'Won game {game_room.room_id}'
            )
            
            # Create commission transaction (platform earning)
            Transaction.objects.create(
                user=winner_player.user,  # Can be admin user or null
                game_room=game_room,
                transaction_type='commission',
                amount=game_room.commission_amount,
                status='completed',
                description=f'Platform commission from game {game_room.room_id}'
            )
            
            # Update stats for all players
            for player in game_room.players.all():
                player.user.total_games_played += 1
                player.user.save()
        
        serializer = self.get_serializer(game_room)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available_rooms(self, request):
        """Get all rooms waiting for players"""
        rooms = GameRoom.objects.filter(
            status='waiting',
            current_players__lt=4
        ).order_by('-created_at')
        
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_games(self, request):
        """Get user's game history"""
        user_games = GamePlayer.objects.filter(
            user=request.user
        ).select_related('game_room').order_by('-joined_at')
        
        games_data = []
        for game_player in user_games:
            room = game_player.game_room
            games_data.append({
                'room_id': str(room.room_id),
                'bet_amount': room.bet_amount,
                'total_pool': room.total_pool,
                'status': room.status,
                'my_color': game_player.color,
                'position': game_player.position,
                'is_winner': game_player.is_winner,
                'winner_username': room.winner.username if room.winner else None,
                'created_at': room.created_at,
                'completed_at': room.completed_at
            })
        
        return Response(games_data)


class WalletViewSet(viewsets.ViewSet):
    """Wallet Management APIs"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get user wallet balance"""
        return Response({
            'balance': request.user.wallet_balance,
            'usdt_address': request.user.usdt_address
        })

    @action(detail=False, methods=['post'])
    def deposit(self, request):
        """Deposit funds (for MVP, just add virtual currency)"""
        amount = Decimal(request.data.get('amount', 0))
        
        if amount <= 0:
            return Response(
                {'error': 'Amount must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            request.user.wallet_balance += amount
            request.user.save()
            
            Transaction.objects.create(
                user=request.user,
                transaction_type='deposit',
                amount=amount,
                status='completed',
                description='Virtual currency deposit'
            )
        
        return Response({
            'message': 'Deposit successful',
            'new_balance': request.user.wallet_balance
        })

    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        """Withdraw funds"""
        amount = Decimal(request.data.get('amount', 0))
        usdt_address = request.data.get('usdt_address')
        
        if amount <= 0:
            return Response(
                {'error': 'Amount must be greater than 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.user.wallet_balance < amount:
            return Response(
                {'error': 'Insufficient balance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            request.user.wallet_balance -= amount
            request.user.save()
            
            Transaction.objects.create(
                user=request.user,
                transaction_type='withdraw',
                amount=amount,
                status='pending',
                description=f'Withdrawal to {usdt_address}'
            )
        
        return Response({
            'message': 'Withdrawal request submitted',
            'new_balance': request.user.wallet_balance
        })

    @action(detail=False, methods=['get'])
    def transactions(self, request):
        """Get user transaction history"""
        transactions = Transaction.objects.filter(
            user=request.user
        ).order_by('-created_at')
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class TournamentViewSet(viewsets.ModelViewSet):
    """Tournament Management APIs"""
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a tournament"""
        tournament = self.get_object()
        
        if tournament.status != 'upcoming':
            return Response(
                {'error': 'Tournament is not open for registration'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if tournament.current_participants >= tournament.max_participants:
            return Response(
                {'error': 'Tournament is full'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if TournamentParticipant.objects.filter(tournament=tournament, user=request.user).exists():
            return Response(
                {'error': 'Already registered for this tournament'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.user.wallet_balance < tournament.entry_fee:
            return Response(
                {'error': 'Insufficient balance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Deduct entry fee
            request.user.wallet_balance -= tournament.entry_fee
            request.user.save()
            
            # Add to tournament
            TournamentParticipant.objects.create(
                tournament=tournament,
                user=request.user
            )
            
            # Update tournament
            tournament.current_participants += 1
            tournament.prize_pool += tournament.entry_fee
            tournament.save()
            
            # Create transaction
            Transaction.objects.create(
                user=request.user,
                transaction_type='bet_placed',
                amount=tournament.entry_fee,
                status='completed',
                description=f'Tournament entry: {tournament.name}'
            )
        
        return Response({
            'message': 'Successfully joined tournament',
            'tournament': TournamentSerializer(tournament).data
        })


class LeaderboardViewSet(viewsets.ViewSet):
    """Leaderboard APIs"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def top_players(self, request):
        """Get top players by wins"""
        from users.models import User
        top_players = User.objects.filter(
            total_games_played__gt=0
        ).order_by('-total_games_won')[:50]
        
        from users.serializers import UserProfileSerializer
        serializer = UserProfileSerializer(top_players, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_earners(self, request):
        """Get top players by earnings"""
        from users.models import User
        from django.db.models import F
        
        top_earners = User.objects.filter(
            total_games_played__gt=0
        ).annotate(
            profit=F('total_amount_won') - F('total_amount_lost')
        ).order_by('-profit')[:50]
        
        from users.serializers import UserProfileSerializer
        serializer = UserProfileSerializer(top_earners, many=True)
        return Response(serializer.data)


class GameStatsView(APIView):
    """Platform statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Sum, Count
        from users.models import User
        
        stats = {
            'total_users': User.objects.count(),
            'total_games': GameRoom.objects.filter(status='completed').count(),
            'total_bets': Transaction.objects.filter(
                transaction_type='bet_placed'
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'total_winnings': Transaction.objects.filter(
                transaction_type='win'
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'platform_earnings': Transaction.objects.filter(
                transaction_type='commission'
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'active_rooms': GameRoom.objects.filter(status='waiting').count(),
            'ongoing_games': GameRoom.objects.filter(status='in_progress').count(),
        }
        
        return Response(stats)
