from django.urls import path
from . import views

urlpatterns = [
    path("", views.market, name="market"),
    path("trade/", views.trade_view, name="trade"),
    path("trade/<str:symbol>/", views.trade_view, name="trade_asset"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("api/execute/", views.execute_trade, name="execute_trade"),
    path("api/prices/", views.price_feed, name="price_feed"),
    path("api/positions/", views.positions_feed, name="positions_feed"),
]