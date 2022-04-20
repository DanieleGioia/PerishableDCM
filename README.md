# PerishableDCM

This library simulates the inventory control problem of perishable products by means of Discrete Choice Methods (DCM).

Specifically, **PerishableDCM** is a simulation environment for the management of perishbale items with lead times and a fixed shelf life. It deals with a multiple items, where orders for fresh produce are issued each day. The product characteristics are:

1. the price at which items are purchased (C)
2. the price at which items are sold (P)
3. the salvage value (if any), when the items are scrapped (MD)

Demand is uncertain and subject to daily seasonality. The objective is to maximize the long-run average daily profit, but the software provides insights in the generated waste as well.

## Dynamics of the simulation

The dynamics of the simulation of one day is hereafter represented.
![plot](./etc/DCM_dynamics.png)

## Available features

Two dictionaries drive the parameters of the simulation: *conf_Products* and *conf_Store*, setting the features of the available products and of the store that sells them.

For example:

```
{
"A":{
    "LT":3,
    "SL":4,
    "P":[6,6,6,6],
    "C":3,
    "MD":0,
    "Q":[22.5,23,23.5,24]
},
"B":{
    "LT":2,
    "SL":2,
    "P":[3.3,4],
    "C":2,
    "MD":0,
    "Q":[18,20]
}
}
```

defines two products A and B, where B has:

1. A lead time of 2 days
2. A shelf life of 2 days
3. A price that decrease w.r.t. to the age (4 if new, 3.3 after one day)
4. A cost of 2
5. No salvage value
6. A quality (Needed for the linear DCM) that decrease w.r.t. the age (20 if new, 18 after one day)

Whereas, the *conf_Store*

```

{
"Seasonals":[90,100,100,100,130,200,200],
"ev_Daily":300,
"std_Daily":20,
"Distr":"Poisson",
"DCM":{
    "Type":"LinearBeta",
    "alpha":2,
    "beta":3
}
}
```

defines:

1. The seasonality that will be normalized by the software s.t. it will sum to 7
2. The expected value of the number of clients per day
3. The std of the number of clients per day
4. The distribution employed to sample the number of clients (Currently Poisson and Normal are available)
5. The DCM and its peculiar requiriments (currently only the linear DCM is available)

## Example

A *main_example* file implements a constant policy 
through the gym OpenAI syntax. 

The debug flag 

```
flagPrint = True
```

provides insight on each step of the simulation. E.g.,

```
 day 409 
 inventory:
Product A : Stored
         101.0 items with  1 Residual shelf life
         89.0 items with  2 Residual shelf life
         75.0 items with  3 Residual shelf life
Product B : Stored
         0.0 items with  1 Residual shelf life
 onOrder:
Product A :Waiting for
         160.0  items A have just arrived.
         160.0  items, expected in 1 days
         160.0  items, expected in 2 days
         160.0  items, expected in 3 days
Product B :Waiting for
         100.0  items A have just arrived.
         100.0  items, expected in 1 days
         100.0  items, expected in 2 days
Total demand (partially lost):  257.0
Product  A  Ordered:  160  Sold:   [  0.   0.   0. 112.]  Scrapped:  101.0
Product  B  Ordered:  100  Sold:   [  0. 100.]  Scrapped:  0.0
 No purchase:  45 Unmet Demand:  0
Total unmet so far 6655
Total ordered so far  106340.0
Total scrapped so far 13560.0
Total sold so far [51188. 40700.]
Profit of the day  392.0
State observation:  {'A': array([160., 160., 160.,  48.,  75.,  89.]), 'B': array([100., 100.,   0.]), 'Day': 4}
Press Enter to continue

```

## Requirements

| Name | | Version employed | Description        | Website |
|:-----|:-:|:-----------:|:---------------------:|:-----------:|
| gym | >= | 0.23.1 | Toolkit for developing and comparing reinforcement learning algorithms| <https://gym.openai.com/>

# Citing Us

If you use PerishableDCM, please cite the following paper: 

```
@article{GioiaFelizBrandi2022,
  title={Inventory management of vertically differentiated perishable products with stock-out based substitution},
  author={Gioia, Daniele Giovanni and Felizardo, Leonardo Kanashiro and Brandimarte, Paolo},
  journal={},
  year={2022}
}
``` 