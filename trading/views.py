import json
import random
import requests
from django.core.cache import cache
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Asset, Trade


@login_required
def market(request):
    assets = Asset.objects.filter(is_active=True)
    return render(request, "trading/market.html", {
        "assets": assets,
        "crypto": assets.filter(asset_type="crypto"),
        "stocks": assets.filter(asset_type="stock"),
    })


@login_required
def trade_view(request, symbol="BTC"):
    symbol = symbol.upper()
    asset = get_object_or_404(Asset, symbol=symbol, is_active=True)
    assets = Asset.objects.filter(is_active=True)
    open_trades = request.user.trades.filter(status="open").select_related("asset")
    closed_trades = request.user.trades.filter(status="closed").select_related("asset")[:10]
    return render(request, "trading/trade.html", {
        "asset": asset,
        "assets": assets,
        "open_trades": open_trades,
        "closed_trades": closed_trades,
        "wallet": request.user.wallet,
    })


@login_required
def portfolio(request):
    user = request.user
    open_trades = user.trades.filter(status="open").select_related("asset")
    closed_trades = user.trades.filter(status="closed").select_related("asset")
    total_open_value = sum(t.current_value for t in open_trades)
    total_unrealized = sum(t.unrealized_pnl for t in open_trades)
    realized_pnl = sum(float(t.pnl) for t in closed_trades)
    wins = sum(1 for t in closed_trades if t.pnl > 0)
    total_closed = closed_trades.count()
    win_rate = round((wins / total_closed * 100) if total_closed else 0, 1)
    return render(request, "trading/portfolio.html", {
        "open_trades": open_trades,
        "closed_trades": closed_trades[:20],
        "total_open_value": total_open_value,
        "total_unrealized": total_unrealized,
        "realized_pnl": realized_pnl,
        "win_rate": win_rate,
        "wallet": user.wallet,
        "total_trades": total_closed,
    })


@login_required
@require_POST
def execute_trade(request):
    try:
        data = json.loads(request.body)
        symbol = data.get("symbol", "").upper()
        side = data.get("side", "").lower()
        amount_str = str(data.get("amount", "0"))
        amount_usd = Decimal(amount_str)
        asset = get_object_or_404(Asset, symbol=symbol, is_active=True)
        wallet = request.user.wallet

        if side == "buy":
            if amount_usd <= 0:
                return JsonResponse({"error": "Enter a valid amount."}, status=400)
            if wallet.balance < amount_usd:
                return JsonResponse({"error": f"Insufficient balance. You have ${wallet.balance:,.2f}"}, status=400)
            quantity = amount_usd / asset.current_price
            wallet.balance -= amount_usd
            wallet.save()
            trade = Trade.objects.create(
                user=request.user, asset=asset, side="buy",
                quantity=quantity, entry_price=asset.current_price, status="open"
            )
            return JsonResponse({
                "success": True,
                "message": f"✓ Bought {float(quantity):.6f} {symbol} @ ${float(asset.current_price):,.2f}",
                "trade_id": trade.id,
                "balance": float(wallet.balance),
            })

        elif side == "sell":
            trade_id = data.get("trade_id")
            if trade_id:
                trade = get_object_or_404(Trade, id=trade_id, user=request.user, status="open")
            else:
                trade = request.user.trades.filter(asset=asset, status="open").first()
                if not trade:
                    return JsonResponse({"error": "No open position for this asset."}, status=400)
            trade.close_position()
            pnl = float(trade.pnl)
            return JsonResponse({
                "success": True,
                "message": f"✓ Closed {symbol}. P&L: {'+'if pnl>=0 else ''}${pnl:,.2f}",
                "pnl": pnl,
                "balance": float(request.user.wallet.balance),
            })

        return JsonResponse({"error": "Invalid side."}, status=400)

    except (InvalidOperation, ValueError) as e:
        return JsonResponse({"error": "Invalid amount."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


TWELVE_DATA_API_KEY = '5f9fcffd7dd44e128fb7bce7310d0e50'

COINGECKO_IDS = {
    'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
    'SOL': 'solana', 'XRP': 'ripple', 'ADA': 'cardano',
    'DOGE': 'dogecoin', 'AVAX': 'avalanche-2',
}

STOCK_SYMBOLS = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'AMZN', 'GOOG', 'META']

def price_feed(request):
    from django.core.cache import cache
    assets = Asset.objects.filter(is_active=True)
    prices = {}

    cached = cache.get('live_prices')
    if cached:
        return JsonResponse({'prices': cached})

    live = {}

    # --- CoinGecko for crypto (free, no limits) ---
    try:
        ids = ','.join(COINGECKO_IDS.values())
        r = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': ids, 'vs_currencies': 'usd'},
            timeout=5
        )
        cg_data = r.json()
        for symbol, cg_id in COINGECKO_IDS.items():
            if cg_id in cg_data:
                live[symbol] = cg_data[cg_id]['usd']
    except Exception:
        pass

    # --- Twelve Data for stocks ---
    try:
        td_symbols = ','.join(STOCK_SYMBOLS)
        r = requests.get(
            'https://api.twelvedata.com/price',
            params={'symbol': td_symbols, 'apikey': TWELVE_DATA_API_KEY},
            timeout=5
        )
        td_data = r.json()
        for symbol in STOCK_SYMBOLS:
            raw = td_data.get(symbol, {})
            if 'price' in raw:
                live[symbol] = float(raw['price'])
    except Exception:
        pass

    # --- Update DB and build response ---
    for asset in assets:
        if asset.symbol in live:
            asset.current_price = Decimal(str(live[asset.symbol]))
            asset.save(update_fields=['current_price'])

        prices[asset.symbol] = {
            'price': float(asset.current_price),
            'change_24h': asset.change_24h,
            'up': asset.current_price >= asset.base_price,
        }

    cache.set('live_prices', prices, 60)
    return JsonResponse({'prices': prices})


@login_required
def positions_feed(request):
    trades = request.user.trades.filter(status="open").select_related("asset")
    data = []
    for t in trades:
        data.append({
            "id": t.id,
            "symbol": t.asset.symbol,
            "quantity": float(t.quantity),
            "entry_price": float(t.entry_price),
            "current_price": float(t.asset.current_price),
            "cost_basis": t.cost_basis,
            "current_value": t.current_value,
            "pnl": t.unrealized_pnl,
            "pnl_pct": t.unrealized_pnl_pct,
        })
    return JsonResponse({
        "positions": data,
        "balance": float(request.user.wallet.balance),
    })
