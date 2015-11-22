#!/usr/bin/env python
from matepay import matemat
from MDB import MDB
from decimal import Decimal
import time
import threading

def MDBpollThread(e):
    global a
    while True:
        e.wait()
        a.poll()
        time.sleep(0.2)

a = MDB.MDB("A1OUKMUG")
m = matemat.Matemat()

# Reset Sequence
a.reset()
a.poll()
a.setup()
a.expansionidentification() #IN: Optional Features: 0x0 0x0 0x0 0x7
a.expansionfeatureenable(['\x00', '\x00', '\x00', '\x07'])
a.expansiondiagnosticstatus()
a.tubestatus()
a.enableall(manual = True)

e = threading.Event()
t = threading.Thread(target=MDBpollThread, args=(e,))
t.daemon = True
t.start()

e.set()

while True:
    cost = m.getCost()
    deposited = Decimal(a.getdeposited() / 100.)
    if (cost > 0):
        print "Cost for selected priceline: " + str(cost)
        m.writeLCD("Price: " + str(cost))
    else:
        m.writeLCD("Credit: " + str(Decimal(deposited)))
    
    if (deposited > 0):
        print "Deposited money/User credit: " + str(deposited)


    if ( deposited >= cost ) and ( cost > Decimal('0') ):
        print "Serving user"
        try:
            e.clear()
            m.writeLCD("Serving your bottle...")
            m.serve()
            time.sleep(1)
            payout = int(float( deposited - cost ) * 100)
            print "Clearing user credit"
            a.cleardeposited()
            print "Payout of change (in Cents): " + str(payout)
            m.writeLCD("Tendering change...")
            a.payout(payout)
            a.poll()
            e.set()
        except matemat.ServeError:
            print "Serve error - continuing"
    time.sleep(0.02)
