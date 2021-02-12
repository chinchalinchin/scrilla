from django.db import models

import app.settings as app_settings
import util.helper as helper


# Have to separate equity and crypto tickers since GLD exists in both
# crypto and equity symbols. Real pain.
class EquityTicker(models.Model):
    ticker = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return self.ticker

class CryptoTicker(models.Model):
    ticker = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return self.ticker

class EquityMarket(models.Model):
    ticker = models.ForeignKey(EquityTicker, on_delete=models.CASCADE)
    date = models.DateField('Date')
    open_price = models.DecimalField(max_digits=20, decimal_places=4)
    close_price = models.DecimalField(max_digits=20, decimal_places=4)
    
    
    def __str__(self):
        return '{} {} : {}'.format(self.ticker, self.date, self.closing_price)
    
    def to_list(self):
        date_string = helper.date_to_string(self.date)
        formatted_self = {}
        formatted_self[date_string][app_settings.AV_RES_EQUITY_OPEN_PRICE] = self.open_price
        formatted_self[date_string][app_settings.AV_RES_EQUITY_CLOSE_PRICE] = self.close_price 
        return formatted_self
    
    def to_date(self):
        return helper.date_to_string(self.date)

class CryptoMarket(models.Model):
    ticker = models.ForeignKey(CryptoTicker, on_delete=models.CASCADE)
    date = models.DateField('Date')
    open_price = models.DecimalField(max_digits=20, decimal_places=10)
    close_price = models.DecimalField(max_digits=20, decimal_places=10)
    
    def __str__(self):
        return '{} {} : {}'.format(self.ticker, self.date, self.closing_price)
    
    def to_list(self):
        formatted_self = {}
        formatted_self[app_settings.AV_RES_CRYPTO_OPEN_PRICE] = self.open_price
        formatted_self[app_settings.AV_RES_CRYPTO_CLOSE_PRICE] = self.close_price 
        return formatted_self

    def to_date(self):
        return helper.date_to_string(self.date)

class Economy(models.Model):
    statistic = models.CharField(max_length=10, primary_key=True)
    date = models.DateField('Date')
    value = models.DecimalField(max_digits=20, decimal_places=10)
    
    def __str__(self):
        return '{} {} : {}'.format(self.statistic, self.date, self.value)