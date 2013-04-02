'''
Created on 2013-3-29

@author: Administrator
'''
def h():
    print 'Wen Chuan',
    m = yield 5 # Fighting!
    print m
    d = yield 12
    print 'We are together!'
if __name__ == '__main__':
    h()
    c = h()
    m = c.next() 
    d = c.send('Fighting!') 
    print 'We will never forget the date', m, '.', d