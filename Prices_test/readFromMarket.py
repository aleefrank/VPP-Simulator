import numpy as np
import pandas

df = pandas.read_csv('meanprofile_prices.csv')

###### Buy
buy = df['nanmean_AcquistoMWh']
buyKWh = [buy[i]/1000 for i in range(len(buy))]
buyFinal = []
for i in range(24):
    buyFinal.append(buyKWh[i])
    buyFinal.append(buyKWh[i])
    buyFinal.append(buyKWh[i])
    buyFinal.append(buyKWh[i])

buyFinal = np.asarray(buyFinal)
np.save("buyTest.npy", buyFinal)
print(buyKWh)

###### Sell
sell = df['nanmean_VenditaMWh']
sellKWh = [sell[i]/1000 for i in range(len(sell))]
sellFinal = []
for i in range(24):
    sellFinal.append(sellKWh[i])
    sellFinal.append(sellKWh[i])
    sellFinal.append(sellKWh[i])
    sellFinal.append(sellKWh[i])

sellFinal = np.asarray(sellFinal)
np.save("sellTest.npy", sellFinal)
print(sellKWh)

###### Prod
prod = df['nanmean_ProduzioneMWh']
prodKWh = [prod[i]/1000 for i in range(len(prod))]
prodFinal = []
for i in range(24):
    prodFinal.append(prodKWh[i])
    prodFinal.append(prodKWh[i])
    prodFinal.append(prodKWh[i])
    prodFinal.append(prodKWh[i])

prodFinal = np.asarray(prodFinal)
np.save("prodTest.npy", prodFinal)

print(prodKWh)
