from django.db import models

# Create your models here.

# TODO: create model for market
# TODO: fields (date, ticker, close)

class Market(models.Model):
    ticker = models.CharField(max_length=5, primary_key=True)
    date = models.DateField('Date')
    closing_price = models.DecimalField(max_digits=20, decimal_places=4)
    
    def __str__(self):
        return '{} {} : {}'.format(self.ticker, self.date, self.closing_price)

class Crypto(models.Model):
    ticker = models.CharField(max_length=5, primary_key=True)
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