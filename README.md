# SanchaarBot.AI 🚀

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB.svg)](https://reactjs.org/)
[![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20S3%20%7C%20DynamoDB-orange.svg)](https://aws.amazon.com/)

**SanchaarBot.AI** is an intelligent, full-stack AI-powered travel companion that revolutionizes how you plan, book, and manage your travels. Built with cutting-edge AI technology, it provides personalized travel assistance through natural language conversations, real-time alerts, document management, and multi-language support.

---

## ✨ Key Features

### 🤖 **AI-Powered Conversational Interface**
- Natural language trip planning and assistance
- AWS Bedrock integration for intelligent responses
- Context-aware conversations with memory

### ✈️ **Smart Travel Booking**
- Real-time flight search and booking (Amadeus, Skyscanner)
- Hotel recommendations and reservations (Booking.com, Expedia)
- Car rental integration with price comparisons

### 📅 **Intelligent Itinerary Planning**
- AI-generated personalized itineraries
- Manual itinerary creation and editing
- Budget tracking and expense management
- PDF export functionality

### 🚨 **Real-Time Travel Alerts**
- Flight delay and gate change notifications
- Weather alerts and advisories
- Travel news and security updates
- Document expiration reminders

### 📄 **Document Management System**
- Secure cloud storage (AWS S3)
- OCR text extraction (AWS Textract)
- Document categorization and organization
- Backup and sharing capabilities

### 🌍 **Multi-Language Translation**
- Text translation with AWS Translate
- Travel phrase suggestions
- Document translation support
- 100+ supported languages

### 📱 **Responsive Dashboard**
- Mobile-first design
- Real-time notifications
- Drag-and-drop file uploads
- Intuitive user interface

---

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │────│   Flask Backend  │────│   AWS Services  │
│                 │    │                  │    │                 │
│ • Chat UI       │    │ • REST APIs      │    │ • Bedrock (AI)  │
│ • Dashboard     │    │ • Agent Logic    │    │ • S3 (Storage)  │
│ • Components    │    │ • Data Processing│    │ • DynamoDB (DB) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │  External APIs   │
                    │                  │
                    │ • Amadeus        │
                    │ • OpenWeather    │
                    │ • NewsAPI        │
                    │ • Google Translate│
                    └──────────────────┘
```

---

## 📁 Project Structure

```
SanchaarBot.AI/
│
├── 📂 backend/
│   ├── 🐍 app.py                     # Main Flask application
│   ├── 🧠 bedrock_agent.py           # AI agent with AWS Bedrock
│   ├── 🗄️ dynamodb_client.py         # Database operations
│   ├── 📦 s3_client.py               # File storage operations
│   ├── 🔧 utils.py                   # Utility functions
│   ├── 📋 requirements.txt           # Python dependencies
│   ├── 🔐 .env.example               # Environment variables template
│   │
│   ├── 📂 lambda_functions/
│   │   ├── ✈️ bookings_handler.py     # Flight/hotel booking logic
│   │   ├── 🚨 alerts_handler.py       # Travel alerts system
│   │   ├── 🌐 translation_handler.py  # Translation services
│   │   ├── 📅 itinerary_handler.py    # Trip planning logic
│   │   └── 📄 document_manager.py     # Document operations
│   │
│   └── 📂 api_clients/
│       ├── ✈️ flights_api.py          # Amadeus/Skyscanner integration
│       ├── 🏨 hotels_api.py           # Booking.com/Expedia integration
│       ├── 🌤️ weather_api.py          # OpenWeatherMap integration
│       └── 📰 news_api.py             # NewsAPI integration
│
├── 📂 frontend/
│   ├── 📂 public/
│   │   ├── 🌐 index.html             # HTML template
│   │   └── 🖼️ favicon.ico            # App icon
│   │
│   ├── 📂 src/
│   │   ├── ⚛️ App.jsx                 # Main React component
│   │   ├── 🔗 api.js                 # API client functions
│   │   ├── 🎨 styles.css             # Global styles
│   │   ├── 🏁 index.js               # React entry point
│   │   │
│   │   └── 📂 components/
│   │       ├── 💬 ChatWindow.jsx      # AI chat interface
│   │       ├── 📅 ItineraryViewer.jsx # Trip planning UI
│   │       ├── 🚨 AlertsPanel.jsx     # Notifications dashboard
│   │       └── 📄 DocumentUploader.jsx# File management UI
│   │
│   ├── 📦 package.json               # Node dependencies
│   └── 🔒 package-lock.json          # Dependency lock file
│
├── 📖 README.md                      # Project documentation
├── 📜 LICENSE                        # MIT License
└── 🐳 docker-compose.yml            # Docker setup (optional)
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** 🐍
- **Node.js 16+** & **npm** 📦
- **Git** 🔧
- **AWS Account** (optional for full features) ☁️

### 1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/SanchaarBot.AI.git
cd SanchaarBot.AI
```

### 2. **Backend Setup**

#### Install Python Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys (optional for testing)
nano .env  # or use your preferred editor
```

#### Start the Backend Server

```bash
python app.py
```

✅ Backend running on: http://localhost:5000

### 3. **Frontend Setup**

#### Install Node Dependencies

```bash
cd ../frontend
npm install
```

#### Start the Development Server

```bash
npm start
```

✅ Frontend running on: http://localhost:3000

### 4. **Access the Application**

Open your browser and navigate to: **http://localhost:3000**

🎉 **Congratulations!** SanchaarBot.AI is now running locally.

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-super-secret-key-change-this-in-production

# AWS Configuration (Required for full functionality)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1

# Database Configuration
DYNAMODB_TABLE_PREFIX=sanchaarbot-dev
S3_BUCKET_NAME=sanchaarbot-documents-dev

# External API Keys (Optional - Mock data used if not provided)
# Travel APIs
AMADEUS_API_KEY=your-amadeus-api-key
AMADEUS_SECRET=your-amadeus-secret-key
SKYSCANNER_API_KEY=your-skyscanner-api-key
BOOKING_API_KEY=your-booking-com-api-key
EXPEDIA_API_KEY=your-expedia-api-key

# Weather & News APIs
OPENWEATHER_API_KEY=your-openweathermap-api-key
WEATHERAPI_KEY=your-weatherapi-com-key
NEWSAPI_KEY=your-newsapi-org-key
GUARDIAN_API_KEY=your-guardian-api-key

# Translation APIs
GOOGLE_TRANSLATE_API_KEY=your-google-translate-api-key
```

### API Key Setup Guide

| Service | Purpose | Free Tier | Sign Up Link |
|---------|---------|-----------|--------------|
| AWS | AI, Storage, Database | ✅ Yes | [aws.amazon.com](https://aws.amazon.com) |
| Amadeus | Flight Data | ✅ Yes | [developers.amadeus.com](https://developers.amadeus.com) |
| OpenWeatherMap | Weather Data | ✅ Yes | [openweathermap.org/api](https://openweathermap.org/api) |
| NewsAPI | Travel News | ✅ Yes | [newsapi.org](https://newsapi.org) |
| Google Translate | Translation | ✅ Yes | [cloud.google.com/translate](https://cloud.google.com/translate) |

---

## 🎯 Usage Examples

### 💬 Chat with the AI

```
You: "Plan a romantic 3-day trip to Paris for $2000"

SanchaarBot: "I'd love to help you plan a romantic Parisian getaway! 
Here's a curated 3-day itinerary:

Day 1: Arrive & Classic Romance
- Morning: Check into boutique hotel near Champs-Élysées
- Afternoon: Seine River cruise with champagne
- Evening: Dinner at Le Jules Verne (Eiffel Tower)

Day 2: Art & Culture
- Morning: Louvre Museum with skip-the-line tickets
- Afternoon: Stroll through Montmartre & Sacré-Cœur
- Evening: Opera show at Palais Garnier

Day 3: Local Experiences
- Morning: Cooking class in Le Marais district
- Afternoon: Palace of Versailles day trip
- Evening: Sunset at Trocadéro with Eiffel Tower view

Budget Breakdown:
- Accommodation: $600 (3 nights)
- Flights: $800 (estimated)
- Activities: $400
- Meals: $200
Total: ~$2000

Would you like me to search for specific flights or hotels?"
```

### ✈️ Flight Search

```
You: "Find flights from NYC to Tokyo departing December 15th"

SanchaarBot: "Searching flights from New York to Tokyo for December 15th...

Found 3 options:
1. ✈️ American Airlines AA154
   Departure: JFK 1:30 PM → NRT 5:45 PM (+1 day)
   Duration: 14h 15m (Direct)
   Price: $1,249 Economy

2. ✈️ Delta Airlines DL295
   Departure: JFK 11:25 AM → NRT 3:40 PM (+1 day) 
   Duration: 15h 15m (1 stop in Seattle)
   Price: $1,089 Economy

3. ✈️ Japan Airlines JL6
   Departure: JFK 2:45 PM → NRT 6:20 PM (+1 day)
   Duration: 14h 35m (Direct)
   Price: $1,399 Economy

Would you like to see more details or book one of these flights?"
```

### 🌍 Translation

```
You: "Translate 'Where is the nearest hospital?' to Japanese"

SanchaarBot: "Translation:
English: 'Where is the nearest hospital?'
Japanese: '一番近い病院はどこですか？'
(Romanized: Ichiban chikai byōin wa doko desu ka?)

Here are some related emergency phrases in Japanese:
- 'I need help': '助けが必要です' (Tasuke ga hitsuyō desu)
- 'Call an ambulance': '救急車を呼んでください' (Kyūkyūsha o yonde kudasai)
- 'I don't feel well': '気分が悪いです' (Kibun ga warui desu)

Would you like me to save these translations for your trip?"
```

---

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
python -m pytest tests/ -v
```

### Run Frontend Tests

```bash
cd frontend
npm test
```

### Manual Testing Checklist

- [ ] Chat interface responds to messages
- [ ] Itinerary creation and AI generation works
- [ ] Document upload and download functions
- [ ] Travel alerts display correctly
- [ ] Translation services work
- [ ] Mobile responsiveness

---

## 🚀 Deployment

### Frontend Deployment (Vercel/Netlify)

#### Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel --prod
```

#### Netlify Deployment

```bash
# Build the project
cd frontend
npm run build

# Deploy dist folder to Netlify
# (Use Netlify dashboard or CLI)
```

### Backend Deployment Options

#### AWS Lambda (Serverless)

```bash
# Install Zappa
pip install zappa

# Initialize Zappa
zappa init

# Deploy to AWS
zappa deploy production
```

#### Docker Deployment

```bash
# Build Docker image
docker build -t sanchaarbot-backend ./backend

# Run container
docker run -p 5000:5000 --env-file .env sanchaarbot-backend
```

#### Traditional VPS/Cloud Server

```bash
# Install dependencies
pip install -r requirements.txt

# Use Gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment-Specific Configuration

#### Production `.env`

```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=generate-a-strong-secret-key-for-production
AWS_ACCESS_KEY_ID=prod-access-key
AWS_SECRET_ACCESS_KEY=prod-secret-key
# ... other production configurations
```

---

## 🔧 Development

### Setting Up Development Environment

```bash
# Install development dependencies
cd backend
pip install -r requirements-dev.txt

cd frontend
npm install --include=dev
```

### Code Style and Linting

#### Backend (Python)

```bash
# Format code with Black
black .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .
```

#### Frontend (JavaScript/React)

```bash
# Lint with ESLint
npm run lint

# Format with Prettier
npm run format
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files
```

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and **add tests**
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Contribution Guidelines

- Follow the existing code style and conventions
- Add tests for new functionality
- Update documentation as needed
- Use clear, descriptive commit messages
- Reference any related issues in your PR description

### Development Workflow

1. **Issues**: Check existing issues or create a new one
2. **Discussion**: Discuss your approach before starting major work
3. **Code**: Write clean, well-documented code
4. **Tests**: Ensure all tests pass
5. **Review**: Submit PR for code review

### Areas for Contribution

- 🐛 Bug fixes and stability improvements
- ✨ New travel service integrations
- 🌐 Multi-language support
- 📱 Mobile app development
- 🔒 Security enhancements
- 📊 Analytics and reporting features
- 🎨 UI/UX improvements
- 📚 Documentation improvements

---

## 🛡️ Security

### Security Best Practices

- All API keys are stored as environment variables
- Input validation and sanitization implemented
- File uploads are scanned and validated
- CORS policies properly configured
- HTTPS recommended for production
- Regular dependency updates

### Reporting Security Issues

If you discover a security vulnerability, please email us at security@sanchaarbot.ai instead of opening a public issue.

---

## 📚 API Documentation

### REST API Endpoints

#### Chat Endpoints

```http
POST /api/chat
Content-Type: application/json

{
  "user_id": "string",
  "message": "string"
}
```

#### Booking Endpoints

```http
POST /api/booking
Content-Type: application/json

{
  "user_id": "string",
  "booking_type": "flight|hotel|car",
  "booking_details": {...}
}
```

#### Itinerary Endpoints

```http
GET /api/itinerary?user_id=string
POST /api/itinerary
PUT /api/itinerary
DELETE /api/itinerary
```

For complete API documentation, visit: `/api/docs` when running the server.

---

## 🔍 Troubleshooting

### Common Issues

#### Backend Issues

**Port Already in Use**
```bash
# Find process using port 5000
lsof -i :5000
# Kill the process
kill -9 <PID>
```

**Import Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**AWS Credentials Issues**
```bash
# Check AWS configuration
aws configure list

# Test AWS access
aws s3 ls
```

#### Frontend Issues

**Module Not Found**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**CORS Errors**
- Ensure backend is running on port 5000
- Check proxy configuration in package.json
- Verify CORS settings in Flask app

#### Performance Issues

**Slow Response Times**
- Check API key limits and quotas
- Monitor AWS service limits
- Optimize database queries
- Use caching where appropriate

---

## 📊 Monitoring and Analytics

### Logging

The application uses structured logging for monitoring:

```python
# Backend logging
import logging
logging.basicConfig(level=logging.INFO)

# Custom logger for specific modules
logger = logging.getLogger(__name__)
```

### Metrics

Key metrics to monitor:

- API response times
- Error rates
- User engagement
- Resource utilization
- External API usage

### Health Checks

```http
GET /health
```

Returns system health status and external service connectivity.

---

## 🗺️ Roadmap

### Version 2.0 (Q1 2025)

- [ ] 📱 Native mobile apps (iOS/Android)
- [ ] 🎯 Advanced AI personalization
- [ ] 💳 Payment integration
- [ ] 🗺️ Interactive maps
- [ ] 👥 Group travel planning
- [ ] 📧 Email integration

### Version 2.5 (Q2 2025)

- [ ] 🔊 Voice assistant integration
- [ ] 🤖 Telegram/WhatsApp bots
- [ ] 📈 Advanced analytics dashboard
- [ ] 🌐 Offline mode support
- [ ] 🔗 Third-party app integrations

### Long-term Vision

- [ ] 🎮 AR/VR travel experiences
- [ ] 🧠 Predictive travel recommendations
- [ ] 🌍 Carbon footprint tracking
- [ ] 🏢 Corporate travel management
- [ ] 📚 Travel community features

---

## 💡 FAQ

### General Questions

**Q: Is SanchaarBot.AI free to use?**
A: Yes! The core application is open-source and free. Some external APIs may have usage limits.

**Q: Do I need AWS to run the application?**
A: No, the app works with mock data for testing. AWS enhances functionality with AI and cloud storage.

**Q: Can I use this for commercial purposes?**
A: Yes, under the MIT license. Please review the license terms.

### Technical Questions

**Q: Which databases are supported?**
A: Currently DynamoDB (AWS) and SQLite (local development). PostgreSQL support planned.

**Q: Can I add new travel service integrations?**
A: Absolutely! The API client architecture makes it easy to add new services.

**Q: Is the AI model customizable?**
A: Yes, you can modify prompts and integrate different LLM providers.

---

## 🙏 Acknowledgments

### Built With

- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [React](https://reactjs.org/) - Frontend JavaScript library
- [AWS Bedrock](https://aws.amazon.com/bedrock/) - AI foundation models
- [AWS S3](https://aws.amazon.com/s3/) - Cloud storage
- [AWS DynamoDB](https://aws.amazon.com/dynamodb/) - NoSQL database

### External APIs

- [Amadeus](https://developers.amadeus.com/) - Travel data
- [OpenWeatherMap](https://openweathermap.org/) - Weather data
- [NewsAPI](https://newsapi.org/) - News data
- [Google Translate](https://cloud.google.com/translate) - Translation services

### Contributors

Thanks to all the amazing contributors who have helped build SanchaarBot.AI!

<!-- Contributors will be automatically generated -->

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 SanchaarBot.AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support & Contact

### Get Help

- 📖 **Documentation**: [Wiki](https://github.com/yourusername/SanchaarBot.AI/wiki)
- 🐛 **Bug Reports**: [Issues](https://github.com/yourusername/SanchaarBot.AI/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/SanchaarBot.AI/discussions)
- 📧 **Email**: support@sanchaarbot.ai

### Community

- 🐦 **Twitter**: [@SanchaarBotAI](https://twitter.com/SanchaarBotAI)
- 💼 **LinkedIn**: [SanchaarBot.AI](https://linkedin.com/company/sanchaarbot-ai)
- 📱 **Discord**: [Join our server](https://discord.gg/sanchaarbot)

---

<div align="center">

### ⭐ Star the Repository

If you found this project helpful, please give it a star! ⭐

**Made with ❤️ by the SanchaarBot.AI Team**

[🏠 Website](https://sanchaarbot.ai) • [📱 Demo](https://demo.sanchaarbot.ai) • [📚 Docs](https://docs.sanchaarbot.ai)

---

**SanchaarBot.AI - Your AI-Powered Travel Companion**

*Transforming the way you explore the world, one conversation at a time.*

</div>