# circuit-reactive-simulation

Simulate digital circuit using reactive programming in Python

## Usage

Design and simulate combinational and sequential circuits in Python  
The value of a wire is determined by functions defined for primary inputs or other wires  
Design these functions in Python and simulate the circuit by assigning values to primary inputs  
The program has registers with asynchronous reset and load value

## How it works

Wires in the circuit act as both observers and observables in reactive programming, allowing for the composition of multi-level circuits  
When the values of observables update, the wire recalculates and updates its new value, notifying its subscribers of the changes  
The software also prevents accidental direct value assignment to wires  
ReactiveX for Python (RxPY) library is employed for reactive programming  

## Examples

Design and simulate counter and full adder circuit

Design and simulate in Python:

```python
def test_counter():
    clk = CreateClock()
    seq = CreateSeq(clk, reset_value=10)
    Q = seq.get_Q()
    seq.set_f(lambda Q: Q+1, Q)
    print('Q <= Q+1')
    print(Q.value)
    for _ in range(3):
        clk.tick()
        print(int(Q.value))
    print()

def module_half_adder(i_a, i_b):
    o_s = CreateWire(lambda i_a, i_b: i_a != i_b, i_a, i_b) # Sum
    o_c = CreateWire(lambda i_a, i_b: i_a and i_b, i_a, i_b) # Carry
    return o_c, o_s
def module_full_adder(i_a, i_b, i_c):
    o_c0, o_s0 = module_half_adder(i_a, i_b)
    o_c1, o_s1 = module_half_adder(o_s0, i_c)
    o_s = CreateWire(lambda o_s1: o_s1, o_s1)
    o_c = CreateWire(lambda o_c0, o_c1: o_c0 or o_c1, o_c0, o_c1)
    return o_c, o_s
def test_module_full_adder():
    # Full adder testing
    i_a = CreatePrimaryInput(0)
    i_b = CreatePrimaryInput(0)
    i_c = CreatePrimaryInput(0)
    o_c, o_s = module_full_adder(i_a, i_b, i_c)
    print('Full adder')
    print('a b i , o s')
    for _ in range(2**3):
        i_a.value = _ & 1
        _ >>= 1
        i_b.value = _ & 1
        _ >>= 1
        i_c.value = _ & 1
        print(int(i_a.value), int(i_b.value), int(i_c.value), ',', int(o_c.value), int(o_s.value))
    print()
test_module_full_adder()
```

Simulation result:

```
$ ./circuit-reactive-simulation.py
Q <= Q+1
10
11
12
13

Q <= !Q
0
1
0
1

Half adder
a b , c s
0 0 , 0 0
1 0 , 0 1
0 1 , 0 1
1 1 , 1 0

Full adder
a b i , o s
0 0 0 , 0 0
1 0 0 , 0 1
0 1 0 , 0 1
1 1 0 , 1 0
0 0 1 , 0 1
1 0 1 , 1 0
0 1 1 , 1 0
1 1 1 , 1 1
```
