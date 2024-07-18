import datetime

datea = '2024-07'

# convert from yyyy-mm to mmm-yyyy
dateb = datetime.datetime.strptime(datea, '%Y-%m').strftime('%b-%Y')
print(dateb)