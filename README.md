# circuit-reactive-simulation
Simulate digital circuit using reactive programming in Python

## Usage
Design and simulate digital combinational circuits in Python  
The value of a wire is determined by functions defined for primary inputs or other wires  
Design these functions in Python and simulate the circuit by assigning values to primary inputs  


## How it works
Wires in the circuit act as both observers and observables in reactive programming, allowing for the composition of multi-level circuits  
When the values of observables update, the wire recalculates and updates its new value, notifying its subscribers of the changes  
The software also prevents accidental direct value assignment to wires  
ReactiveX for Python (RxPY) library is employed for reactive programming  

## Examples
Design and simulate a full adder circuit in Python using reactive programming  

Outputs:
```
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