"""
Exchange Rate Service - Provides real-time currency conversion
Supports INR, USD, and EUR with 24-hour cache
"""
import logging
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import aiohttp

logger = logging.getLogger(__name__)


class ExchangeRateService:
    """
    Service for real-time currency exchange rates
    Supports INR, USD, EUR with caching
    """
    
    # Free exchange rate API (no key required)
    API_URL = "https://api.exchangerate-api.com/v4/latest/{base_currency}"
    
    # Fallback rates (updated periodically)
    FALLBACK_RATES = {
        "USD": {
            "INR": 83.12,
            "EUR": 0.92,
            "USD": 1.0
        },
        "EUR": {
            "INR": 90.35,
            "USD": 1.09,
            "EUR": 1.0
        },
        "INR": {
            "USD": 0.012,
            "EUR": 0.011,
            "INR": 1.0
        }
    }
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """
        Initialize exchange rate service
        
        Args:
            db: MongoDB database instance (optional, for caching)
        """
        self.db = db
        self.cache_collection = db.exchange_rate_cache if db else None
        self.cache_ttl_hours = 24
        
        logger.info("ExchangeRateService initialized")
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Get exchange rate from one currency to another
        
        Args:
            from_currency: Source currency (INR, USD, EUR)
            to_currency: Target currency (INR, USD, EUR)
            
        Returns:
            Exchange rate as float
        """
        # Normalize currency codes
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Same currency
        if from_currency == to_currency:
            return 1.0
        
        # Validate currencies
        supported_currencies = ["INR", "USD", "EUR"]
        if from_currency not in supported_currencies or to_currency not in supported_currencies:
            logger.warning(f"Unsupported currency pair: {from_currency} -> {to_currency}")
            return 1.0
        
        # Check cache first
        if self.cache_collection:
            cached_rate = await self._get_cached_rate(from_currency, to_currency)
            if cached_rate:
                logger.debug(f"Using cached rate: {from_currency} -> {to_currency} = {cached_rate}")
                return cached_rate
        
        # Fetch live rate
        try:
            rate = await self._fetch_live_rate(from_currency, to_currency)
            
            # Cache the rate
            if self.cache_collection and rate:
                await self._cache_rate(from_currency, to_currency, rate)
            
            logger.info(f"Fetched live rate: {from_currency} -> {to_currency} = {rate}")
            return rate
            
        except Exception as e:
            logger.error(f"Error fetching exchange rate: {e}")
            # Use fallback rates
            return self._get_fallback_rate(from_currency, to_currency)
    
    async def convert_amount(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> float:
        """
        Convert amount from one currency to another
        
        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            Converted amount
        """
        rate = await self.get_exchange_rate(from_currency, to_currency)
        converted = amount * rate
        
        logger.debug(f"Converted {amount} {from_currency} to {converted:.2f} {to_currency}")
        return converted
    
    async def _fetch_live_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Fetch live exchange rate from API
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            Exchange rate
        """
        url = self.API_URL.format(base_currency=from_currency)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    rates = data.get('rates', {})
                    
                    if to_currency in rates:
                        return float(rates[to_currency])
                    else:
                        raise ValueError(f"Rate for {to_currency} not found in API response")
                else:
                    raise ValueError(f"API returned status {response.status}")
    
    def _get_fallback_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Get fallback exchange rate from hardcoded values
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            Fallback exchange rate
        """
        if from_currency in self.FALLBACK_RATES:
            if to_currency in self.FALLBACK_RATES[from_currency]:
                rate = self.FALLBACK_RATES[from_currency][to_currency]
                logger.warning(f"Using fallback rate: {from_currency} -> {to_currency} = {rate}")
                return rate
        
        logger.error(f"No fallback rate available for {from_currency} -> {to_currency}")
        return 1.0
    
    async def _get_cached_rate(
        self,
        from_currency: str,
        to_currency: str
    ) -> Optional[float]:
        """
        Get cached exchange rate
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            Cached rate if found and not expired, None otherwise
        """
        if not self.cache_collection:
            return None
        
        try:
            cache_key = f"{from_currency}_{to_currency}"
            cached_doc = await self.cache_collection.find_one({"cache_key": cache_key})
            
            if not cached_doc:
                return None
            
            # Check expiration
            expires_at = cached_doc.get('expires_at')
            if expires_at:
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                if expires_at < datetime.now(timezone.utc):
                    # Expired, delete it
                    await self.cache_collection.delete_one({"cache_key": cache_key})
                    return None
            
            return cached_doc.get('rate')
            
        except Exception as e:
            logger.error(f"Error retrieving cached rate: {e}")
            return None
    
    async def _cache_rate(
        self,
        from_currency: str,
        to_currency: str,
        rate: float
    ) -> None:
        """
        Cache exchange rate
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            rate: Exchange rate to cache
        """
        if not self.cache_collection:
            return
        
        try:
            cache_key = f"{from_currency}_{to_currency}"
            expires_at = datetime.now(timezone.utc) + timedelta(hours=self.cache_ttl_hours)
            
            cache_doc = {
                "cache_key": cache_key,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": rate,
                "cached_at": datetime.now(timezone.utc),
                "expires_at": expires_at
            }
            
            await self.cache_collection.update_one(
                {"cache_key": cache_key},
                {"$set": cache_doc},
                upsert=True
            )
            
            logger.debug(f"Cached exchange rate: {cache_key} = {rate}")
            
        except Exception as e:
            logger.error(f"Error caching exchange rate: {e}")
    
    def get_currency_symbol(self, currency: str) -> str:
        """
        Get currency symbol
        
        Args:
            currency: Currency code (INR, USD, EUR)
            
        Returns:
            Currency symbol
        """
        symbols = {
            "INR": "₹",
            "USD": "$",
            "EUR": "€"
        }
        return symbols.get(currency.upper(), currency)
    
    def format_amount(self, amount: float, currency: str) -> str:
        """
        Format amount with currency symbol
        
        Args:
            amount: Amount to format
            currency: Currency code
            
        Returns:
            Formatted string (e.g., "$50,000.00", "₹5,00,000.00")
        """
        currency = currency.upper()
        symbol = self.get_currency_symbol(currency)
        
        # Indian numbering system for INR
        if currency == "INR":
            # Format with Indian comma placement
            amount_str = f"{amount:,.2f}"
            # Convert to Indian format (lakhs, crores)
            parts = amount_str.split('.')
            integer_part = parts[0].replace(',', '')
            decimal_part = parts[1] if len(parts) > 1 else "00"
            
            # Indian formatting
            if len(integer_part) > 3:
                last_three = integer_part[-3:]
                remaining = integer_part[:-3]
                
                # Add commas every 2 digits for remaining
                formatted_remaining = ""
                for i, digit in enumerate(reversed(remaining)):
                    if i > 0 and i % 2 == 0:
                        formatted_remaining = "," + formatted_remaining
                    formatted_remaining = digit + formatted_remaining
                
                formatted = f"{symbol}{formatted_remaining},{last_three}.{decimal_part}"
            else:
                formatted = f"{symbol}{integer_part}.{decimal_part}"
            
            return formatted
        else:
            # Western format for USD, EUR
            return f"{symbol}{amount:,.2f}"
