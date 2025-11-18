# 🎲 Zugu Ludo USDT - Backend

Real-money Ludo betting game with USDT cryptocurrency integration.

## 🚀 Features

### ✅ Implemented (MVP)
- ✨ User authentication (JWT)
- 💰 Virtual wallet system
- 🎮 Game room management (4 players)
- 💵 Betting system with commission
- 🏆 Tournament system
- 📊 Leaderboard
- 📱 RESTful APIs
- 🔌 WebSocket for real-time updates
- 👨‍💼 Admin panel
- 📝 API documentation

### 🔄 Coming Soon
- 🪙 Real USDT integration (blockchain)
- 📱 iOS & Android apps
- 🎯 Advanced game logic
- 🔒 KYC verification
- 📧 Email notifications
- 📈 Analytics dashboard

## 💻 Tech Stack

- **Backend**: Django 5.0, Django REST Framework
- **Database**: PostgreSQL (or SQLite for development)
- **Cache/Queue**: Redis, Celery
- **WebSocket**: Django Channels
- **Authentication**: JWT (Simple JWT)
- **API Docs**: drf-yasg (Swagger)
- **Blockchain**: Web3.py (for USDT)

## 📦 Installation

```bash
# Clone repository
git clone <your-repo>
cd zugu_ludo_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

**Detailed setup:** See [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 📚 API Documentation

Access Swagger UI: `http://localhost:8000/swagger/`

### Quick API Overview

**Authentication**
```
POST /api/v1/users/register/
POST /api/v1/users/login/
GET  /api/v1/users/profile/
```

**Game**
```
POST /api/v1/game/rooms/create_room/
POST /api/v1/game/rooms/{id}/join_room/
GET  /api/v1/game/rooms/available_rooms/
```

**Wallet**
```
GET  /api/v1/game/wallet/balance/
POST /api/v1/game/wallet/deposit/
POST /api/v1/game/wallet/withdraw/
```

## 🎮 Game Flow

1. **User registers** → Gets virtual wallet
2. **Create/Join room** → Bet amount is deducted
3. **4 players join** → Game starts automatically
4. **Play game** → Real-time updates via WebSocket
5. **Declare winner** → Winner gets pool minus commission
6. **Platform commission** → 1-2% from total pool

### Example: $20 Pool
- 4 players × $5 each = $20
- Commission (2%) = $0.40
- Winner gets = $19.60

## 🏗️ Project Structure

```
zugu_ludo_backend/
├── manage.py
├── requirements.txt
├── zugu_ludo/          # Main project
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py
├── users/              # User management
│   ├── models.py
│   ├── views.py
│   └── serializers.py
└── game/               # Game logic
    ├── models.py
    ├── views.py
    ├── consumers.py    # WebSocket
    └── routing.py
```

## 🔐 Security Features

- JWT authentication
- Password hashing (bcrypt)
- CORS protection
- SQL injection prevention (ORM)
- XSS protection
- CSRF protection
- Rate limiting (coming soon)

## 📊 Database Models

### User
- Authentication + Profile
- Wallet balance
- Game statistics
- Transaction history

### GameRoom
- Room management
- Betting pool
- Commission calculation
- Winner tracking

### Transaction
- Deposits/Withdrawals
- Bets placed
- Winnings
- Platform commission

### Tournament
- Tournament management
- Participants
- Prize distribution

## 🌐 WebSocket Events

### Game Room
```javascript
// Connect
ws://localhost:8000/ws/game/{room_id}/

// Events
- dice_rolled
- piece_moved
- player_joined
- game_started
- game_ended
```

### Lobby
```javascript
// Connect
ws://localhost:8000/ws/lobby/

// Events
- room_created
- room_updated
```

## 🧪 Testing

```bash
# Run tests
python manage.py test

# With coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deployment

### Development
```bash
python manage.py runserver
```

### Production
```bash
# Using Gunicorn
gunicorn zugu_ludo.wsgi:application

# Using Daphne (WebSocket)
daphne -b 0.0.0.0 -p 8000 zugu_ludo.asgi:application
```

### Docker (Coming Soon)
```bash
docker-compose up
```

## 📈 Roadmap

### Phase 1: MVP (Current) ✅
- [x] User authentication
- [x] Game room management
- [x] Virtual wallet
- [x] Basic betting system
- [x] Admin panel

### Phase 2: Blockchain Integration
- [ ] USDT wallet integration
- [ ] Smart contract deployment
- [ ] Automated payouts
- [ ] Transaction verification

### Phase 3: Mobile Apps
- [ ] React Native app
- [ ] iOS app
- [ ] Android app
- [ ] Push notifications

### Phase 4: Advanced Features
- [ ] Live tournaments
- [ ] Chat system
- [ ] Video calls
- [ ] Social features

## ⚠️ Important Notes

### Legal Compliance
- **Required**: Gambling license for real-money betting
- **KYC/AML**: User verification mandatory
- **Age verification**: 18+ only
- **Jurisdiction**: Check local laws

### Budget & Timeline
- **MVP Budget**: $300-400 (Basic prototype only)
- **Production**: $15,000-50,000+ (Full system)
- **Timeline**: 3-6 months (Production-ready)

### Current Limitations
- Virtual currency only (no real USDT yet)
- No mobile apps (API ready)
- Basic game logic (needs refinement)
- No payment gateway integration

## 🤝 Contributing

This is a private project. Contact owner for access.

## 📄 License

Proprietary - All rights reserved

## 👨‍💻 Developer

**Contact**: support@zuguludo.com

## 🆘 Support

For setup issues, check:
1. [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. [GitHub Issues](issues)
3. Email: support@zuguludo.com

## ⚡ Quick Start Commands

```bash
# Development
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Admin
python manage.py createsuperuser

# Shell
python manage.py shell

# Tests
python manage.py test
```

---

**Note**: Yeh ek MVP (Minimum Viable Product) hai. Production deployment ke liye additional security, testing, aur legal compliance required hai.
