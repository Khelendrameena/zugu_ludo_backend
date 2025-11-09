import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GameRoom, GamePlayer, GameMove
from users.models import User

class GameConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time game updates"""
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'game_{self.room_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current game state
        game_state = await self.get_game_state()
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'data': game_state
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'roll_dice':
            await self.handle_dice_roll(data)
        elif message_type == 'move_piece':
            await self.handle_piece_move(data)
        elif message_type == 'chat_message':
            await self.handle_chat(data)
    
    async def handle_dice_roll(self, data):
        """Handle dice roll"""
        import random
        dice_value = random.randint(1, 6)
        
        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'dice_rolled',
                'user': self.scope['user'].username,
                'dice_value': dice_value
            }
        )
    
    async def handle_piece_move(self, data):
        """Handle piece movement"""
        piece_id = data.get('piece_id')
        from_position = data.get('from_position')
        to_position = data.get('to_position')
        
        # Save move to database
        await self.save_move(piece_id, from_position, to_position)
        
        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'piece_moved',
                'user': self.scope['user'].username,
                'piece_id': piece_id,
                'from_position': from_position,
                'to_position': to_position
            }
        )
    
    async def handle_chat(self, data):
        """Handle chat message"""
        message = data.get('message')
        
        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': self.scope['user'].username,
                'message': message
            }
        )
    
    # Receive message from room group
    async def dice_rolled(self, event):
        await self.send(text_data=json.dumps({
            'type': 'dice_rolled',
            'user': event['user'],
            'dice_value': event['dice_value']
        }))
    
    async def piece_moved(self, event):
        await self.send(text_data=json.dumps({
            'type': 'piece_moved',
            'user': event['user'],
            'piece_id': event['piece_id'],
            'from_position': event['from_position'],
            'to_position': event['to_position']
        }))
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'user': event['user'],
            'message': event['message']
        }))
    
    async def player_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'user': event['user'],
            'color': event['color']
        }))
    
    async def game_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'message': 'Game has started!'
        }))
    
    async def game_ended(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_ended',
            'winner': event['winner']
        }))
    
    @database_sync_to_async
    def get_game_state(self):
        """Get current game state from database"""
        try:
            game_room = GameRoom.objects.get(room_id=self.room_id)
            players = GamePlayer.objects.filter(game_room=game_room)
            
            return {
                'room_id': str(game_room.room_id),
                'status': game_room.status,
                'bet_amount': float(game_room.bet_amount),
                'current_players': game_room.current_players,
                'players': [
                    {
                        'username': p.user.username,
                        'color': p.color,
                        'position': p.position
                    } for p in players
                ]
            }
        except GameRoom.DoesNotExist:
            return None
    
    @database_sync_to_async
    def save_move(self, piece_id, from_position, to_position):
        """Save move to database"""
        # Implementation for saving move
        pass


class LobbyConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for lobby updates"""
    
    async def connect(self):
        self.room_group_name = 'lobby'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send available rooms
        rooms = await self.get_available_rooms()
        await self.send(text_data=json.dumps({
            'type': 'available_rooms',
            'rooms': rooms
        }))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle lobby messages
    
    async def room_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'room_created',
            'room': event['room']
        }))
    
    async def room_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'room_updated',
            'room': event['room']
        }))
    
    @database_sync_to_async
    def get_available_rooms(self):
        """Get available game rooms"""
        rooms = GameRoom.objects.filter(
            status='waiting',
            current_players__lt=4
        )
        return [
            {
                'room_id': str(room.room_id),
                'bet_amount': float(room.bet_amount),
                'current_players': room.current_players
            } for room in rooms
        ]
