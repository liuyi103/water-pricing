__author__ = 'liu'

import numpy as np
import random
import pulp as pp

n_seller = 10
n_buyer = 10
n_edge = 20

class Candidate:
    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return 'price '+ str(self.price)+'; quantity '+str(self.quantity)


sellers = [Candidate(random.random(), np.random.random_integers(10, 100)) for i in range(n_seller)]
buyers = [Candidate(random.random() * 1.5, np.random.random_integers(10, 100)) for i in range(n_buyer)]
edges = [(random.randint(0, n_seller - 1), random.randint(0, n_buyer - 1)) for i in range(n_edge)]
edges = [(a,b) for a,b in edges if sellers[a].price < buyers[b].price]
edges = list(set(edges))

prob = pp.LpProblem('max social welfare', pp.LpMaximize)
f = pp.LpVariable.dict('f', range(len(edges)), 0)
prob += pp.lpSum([(buyers[b].price - sellers[a].price) * f[k] for k,(a,b) in enumerate(edges)])
for i, seller in enumerate(sellers):
    attached = []
    for k, edge in enumerate(edges):
        if edge[0] == i:
            attached.append(k)
    if len(attached) == 0:
        continue
    prob += pp.lpSum([f[k]for k in attached]) <= sellers[i].quantity

for i, buyerer in enumerate(buyers):
    attached = []
    for k, edge in enumerate(edges):
        if edge[1] == i:
            attached.append(k)
    if len(attached) == 0:
        continue
    prob += pp.lpSum([f[k]for k in attached]) <= buyers[i].quantity
prob.solve()
fs = []
for i, edge in enumerate(edges):
    print edge, pp.value(f[i])
    fs.append(pp.value(f[i]))

prob = pp.LpProblem('get prices')
s = pp.LpVariable.dict('s', range(n_seller), 0)
b = pp.LpVariable.dict('b', range(n_buyer), 0)
for i, (x, y) in enumerate(edges):
    if fs[i] == 0:
        prob += s[x] + b[y] >= buyers[y].price - sellers[x].price
    elif fs[i] >= min(buyers[y].quantity, sellers[x].quantity)-0.1:
        prob += s[x] + b[y] <= buyers[y].price - sellers[x].price
    else:
        prob += s[x] + b[y] == buyers[y].price - sellers[x].price
prob.solve()
for i, seller in enumerate(sellers):
    s[i] = pp.value(s[i])
for i, buyer in enumerate(buyers):
    b[i] = pp.value(b[i])
for k, (x,y) in enumerate(edges):
    print x,y
    print 'delta_price', buyers[y].price - sellers[x].price, s[x]+b[y], fs[k]
    assert((fs[k] < 1e-3) or (buyers[y].price - sellers[x].price >= s[x]+b[y] - 1e-4))
    assert((fs[k] > 1e-3) or (buyers[y].price - sellers[x].price <= s[x]+b[y] + 1e-4))