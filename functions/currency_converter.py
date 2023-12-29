from currency_converter import CurrencyConverter


async def todollar(value):
    c = CurrencyConverter()
    return "${:.2f}".format(c.convert(float(value), 'USD'))


async def toeur(value):
    c = CurrencyConverter()
    return "€{:.2f}".format(float(value))


async def topound(value):
    c = CurrencyConverter()
    return "£{:.2f}".format(float(value))

