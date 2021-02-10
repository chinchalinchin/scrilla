from django.db import models


# Have to separate equity and crypto tickers since GLD exists in both
# crypto and equity symbols. Real pain.
class EquityTicker(models.Model):
    ticker = models.CharField(max_length=5, primary_key=True)

    def __str__(self):
        return self.ticker

class CryptoTicker(models.Model):
    ticker = models.CharField(max_length=5, primary_key=True)

    def __str__(self):
        return self.ticker

class EquityMarket(models.Model):
    ticker = models.ForeignKey(EquityTicker, on_delete=models.CASCADE)
    date = models.DateField('Date')
    closing_price = models.DecimalField(max_digits=20, decimal_places=4)
    
    def __str__(self):
        return '{} {} : {}'.format(self.ticker, self.date, self.closing_price)

class CryptoMarket(models.Model):
    ticker = models.ForeignKey(CryptoTicker, on_delete=models.CASCADE)
    date = models.DateField('Date')
    closing_price = models.DecimalField(max_digits=20, decimal_places=10)
    
    def __str__(self):
        return '{} {} : {}'.format(self.ticker, self.date, self.closing_price)

class Economy(models.Model):
    statistic = models.CharField(max_length=10, primary_key=True)
    date = models.DateField('Date')
    value = models.DecimalField(max_digits=20, decimal_places=10)
    
    def __str__(self):
        return '{} {} : {}'.format(self.statistic, self.date, self.value)