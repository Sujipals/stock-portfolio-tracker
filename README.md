# 📈 Stock Portfolio Tracker

A modern, user-friendly web application to track and analyze your stock investments in real-time. Built with Flask (Python) backend and vanilla JavaScript frontend, deployed on Vercel.

## ✨ Features

### 📊 Core Features
- **Add Stocks** - Add multiple stocks with quantities to your portfolio
- **Calculate Portfolio Value** - Get real-time stock prices from Yahoo Finance API
- **View Holdings** - See all stocks in your portfolio with details
- **Remove Stocks** - Delete stocks from your portfolio easily
- **Live Price Charts** - View TradingView charts for each stock

### 💾 Data Management
- **Auto-Save** - Portfolio is automatically saved to browser storage
- **Save Named Portfolios** - Create named backups of your portfolios (e.g., "Tech Stocks", "Retirement")
- **Load Portfolios** - Load any previously saved portfolio with one click
- **Delete Portfolios** - Remove old portfolios you no longer need
- **Persistent Storage** - Data persists even after closing the browser

### 🎨 User Interface
- **Modern Design** - Beautiful gradient background and card-based layout
- **Responsive** - Works perfectly on desktop, tablet, and mobile
- **Dark/Light Mode Ready** - Smooth, professional styling
- **Real-time Feedback** - Success/error messages for all actions
- **Smooth Animations** - Fade-in and slide effects for a polished feel

### 🔐 Security & Reliability
- **Error Handling** - Graceful error handling with user-friendly messages
- **CORS Enabled** - Secure cross-origin requests
- **Input Validation** - Validates all user inputs before processing
- **Fallback Prices** - Uses alternative price sources if primary is unavailable
- **Health Check** - Server status monitoring endpoint

## 🚀 Getting Started

### Online (Recommended)
Visit: [Stock Portfolio Tracker](https://stock-portfolio-tracker-virid-tau.vercel.app)

### Local Development

#### Prerequisites
- Python 3.8+
- pip (Python package manager)

#### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Sujipals/stock-portfolio-tracker.git
cd stock-portfolio-tracker
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the app**
```bash
python backend_api.py
```

5. **Open in browser**
```
http://localhost:5000
```

## 📖 How to Use

### Adding Stocks
1. Enter stock symbol (e.g., AAPL, GOOGL, MSFT)
2. Enter quantity
3. Click "➕ Add Stock"
4. Stock appears in your portfolio list

### Calculating Portfolio Value
1. Add at least one stock
2. Click "💰 Calculate Portfolio Value"
3. See breakdown of each stock's value
4. View total portfolio value
5. See live price chart for added stocks

### Saving Portfolios
1. Click "Calculate Portfolio Value"
2. Click "💾 Save This Portfolio"
3. Enter a name (e.g., "My Tech Stocks")
4. Click "Save"

### Loading Saved Portfolios
1. Click "📂 Load Portfolio" at the top
2. Select portfolio from list
3. Click "📂 Load"
4. Your portfolio is restored

### Clearing Portfolio
1. Click "🗑️ Clear All" to clear current portfolio
2. Confirm when prompted
3. (Saved portfolios remain unaffected)

## 🏗️ Project Structure

```
stock-portfolio-tracker/
├── backend_api.py          # Flask backend server
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel deployment config
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── templates/
    └── index.html         # Frontend UI (HTML/CSS/JS)
```

## 🔧 Technical Details

### Backend (Flask)
- **Framework**: Flask 2.3.3
- **API**: Stock data from yfinance library
- **Features**: 
  - `/` - Serves HTML frontend
  - `/calculate` - Processes portfolio calculations
  - `/health` - Server health check
  - CORS-enabled for cross-origin requests

### Frontend (Vanilla JavaScript)
- **Storage**: Browser localStorage (no database needed)
- **API Calls**: Fetch API for async communication
- **Charts**: TradingView embedded widgets
- **Styling**: Custom CSS with animations

### Dependencies
```
Flask==2.3.3          # Web framework
yfinance==0.2.32      # Stock data API
Werkzeug==2.3.7       # WSGI utilities
flask-cors==4.0.0     # CORS support
```

## 🐛 Troubleshooting

### "Error connecting to server"
1. Check internet connection
2. Verify Vercel deployment is active
3. Open browser console (F12) to see detailed errors
4. Try refreshing the page

### Stock prices showing $0
- Stock symbol may be invalid
- Yahoo Finance API might be rate-limited
- Try again in a few moments

### Portfolio not saving
- Check if localStorage is enabled in browser
- Some private/incognito modes disable localStorage
- Clear browser cache and try again

### Invalid stock symbol error
- Ensure symbol is correct (e.g., AAPL not "Apple")
- Use valid NASDAQ/NYSE stock symbols
- Try with major stocks first (AAPL, GOOGL, MSFT)

## 📊 Example Portfolios

### Tech Stocks
- AAPL: 10 shares
- GOOGL: 5 shares
- MSFT: 15 shares

### Dividend Portfolio
- JNJ: 20 shares
- KO: 25 shares
- PG: 30 shares

### Crypto-Adjacent
- COIN: 5 shares
- MARA: 10 shares
- RIOT: 15 shares

## 🌐 Deployment

### Deploy to Vercel (Free)

1. **Connect GitHub**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub
   - Authorize Vercel

2. **Import Project**
   - Click "New Project"
   - Select this repository
   - Click "Import"

3. **Auto-Deploy**
   - Vercel automatically deploys on every push
   - Check deployment status in dashboard
   - Your app is live!

## 📝 API Reference

### POST /calculate
Calculate portfolio value

**Request:**
```json
[
  {"symbol": "AAPL", "quantity": 10},
  {"symbol": "GOOGL", "quantity": 5}
]
```

**Response:**
```json
{
  "stocks": [
    {
      "symbol": "AAPL",
      "price": 150.25,
      "quantity": 10,
      "value": 1502.50
    }
  ],
  "total": 1502.50,
  "errors": []
}
```

### GET /health
Server health check

**Response:**
```json
{
  "status": "ok",
  "message": "Server is running"
}
```

## 🎯 Future Enhancements

- [ ] User authentication & cloud storage
- [ ] Multiple portfolios management
- [ ] Portfolio performance analytics
- [ ] Gain/loss tracking with purchase price
- [ ] Dividend yield calculator
- [ ] Historical price trends
- [ ] Stock news feed integration
- [ ] Export to PDF/CSV
- [ ] Mobile app version
- [ ] Dark mode toggle

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an issue on GitHub
3. Check existing issues for solutions

## 🙏 Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) - Stock data API
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [TradingView](https://www.tradingview.com/) - Chart widgets
- [Vercel](https://vercel.com) - Deployment platform

---

**Made with ❤️ by [Sujipals](https://github.com/Sujipals)**

Last updated: 2026-06-16
