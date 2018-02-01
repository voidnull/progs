#!/usr/bin/env python

import datetime
import requests
import BeautifulSoup
import types
import argparse

def getRateOn(d):
    url='http://www.x-rates.com/historical/?from=USD&amount=1&date=' + str(d.date())
    #print 'fetching ', url
    page = requests.get(url)
    soup = BeautifulSoup.BeautifulSoup(page.text)
    a = soup.find('a',{'href':"/graph/?from=USD&to=INR"})
    return float(a.text)

'''
date : yyyy-mm-dd
'''
def getFriendlyRate(date=5):
    if type(date) == types.StringType:
        if date.isdigit():
            date = int(date)
        else:
            date = datetime.datetime.strptime(date,'%Y-%m-%d')

    if type(date) == types.IntType:
        date = datetime.datetime.today() - datetime.timedelta(days=date)

    dayrates = []
    for day in range(-5,6):
        d = date + datetime.timedelta(days=day)
        dayrates.append((d,getRateOn(d)))

    rates = [d[1] for d in dayrates]
    rates.sort()
    avg = sum(rates[1:-1])/(len(rates)-2)

    print '10 day rates around {} from http://www.x-rates.com'.format(date.strftime('%b %d'))
    print '-' * 30
    for d in dayrates:
        print '{} : {}'.format(d[0].strftime('%b %d'),d[1])
    print '-' * 30
    print 'Rate: {:5.2f}    min:{:5.2f}  max:{:5.2f}'.format(avg, rates[0],rates[-1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='get the freindly rate from x-rates.com')
    parser.add_argument('date', nargs='?', default='10')
    args = parser.parse_args()
    getFriendlyRate(args.date)
