# manual computation of mean return:

# NOTE: manual computation
# for date in prices:
    # todays_price = services.parse_price_from_date(prices, date, asset_type)

    # if i != 0:
        # logger.verbose(f'{date}: (todays_price, tomorrows_price) = ({todays_price}, {tomorrows_price})')
        # daily_return = numpy.log(float(tomorrows_price)/float(todays_price))/trading_period
        # mean_return = mean_return + daily_return/sample
        # logger.verbose(f'{date}: (daily_return, mean_return) = ({round(daily_return, 2)}, {round(mean_return, 2)})')

    # else:
        # logger.verbose('Skipping first date.')
        # i += 1  

    # tomorrows_price = services.parse_price_from_date(prices, date, asset_type)
        