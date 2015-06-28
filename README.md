Financial Computing HW3 
=======================
R03246004 陳彥安

--------------------------------------------------
## Environment:
1. python 2.7.9
2. package (module) needed:
    - numpy (1.9.2) 
    - scipy (0.15.1)


## How To Run (example):
 - **Entering parameter's value in a file**

Open file `./input` and enter (modify) input values in JSON format

```json
[
    {
        "S": 100,
        "X": 95,
        "s": 35,
        "T0": "2015-04-21",
        "T1": "2015-06-19",
        "T2": "2015-05-21",
        "T3": "2015-06-19",
        "m": 2,
        "r": 10
    },
    {
        "S": 100,
        "X": 95,
        "s": 35,
        "T0": "2015-04-21",
        "T1": "2015-06-19",
        "T2": "2015-05-21",
        "T3": "2015-06-19",
        "m": 2,
        "r": 0
    }
]
```

 - **Execute the program**
Use the command: 
`python <HW3.py|HW3.pyc> <data location>`. 
For example:

```bash
> python HW3.py input
S=100, X=95, s=35%, t=0.1643835616438356, n=120, r=10 %:
- Bermuda Call :    9.42048158011
- Bermuda Put  :    2.93698986998
S=100, X=95, s=35%, t=0.1643835616438356, n=120, r=0 %:
- Bermuda Call :    8.44706749215
- Bermuda Put  :    3.44706749215
> 
```
