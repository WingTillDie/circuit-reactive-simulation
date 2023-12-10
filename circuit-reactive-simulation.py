#!/usr/bin/python3
import rx
from rx.subject import BehaviorSubject, Subject

class CreatePrimaryInput:
    def __init__(self, initial_value):
        self._subject = BehaviorSubject(initial_value)

    @property
    def value(self):
        return self._subject.value

    @value.setter
    def value(self, new_value):
        if new_value != self.value:
            self._subject.on_next(new_value)

class CreateWire:
    def __init__(self, *f_and_reactive_or_dependent_variables):
        if(f_and_reactive_or_dependent_variables):
            f, *reactive_or_dependent_variables = f_and_reactive_or_dependent_variables
            self._f = f
            subjects = (_._subject for _ in reactive_or_dependent_variables)
            values = (_.value for _ in reactive_or_dependent_variables)

            self._subject = Subject()

            self._value = self._f(*values)
            
            rx.combine_latest(*subjects).subscribe(
                self.observer
            )
        else: raise
    def observer(self, values):
        new_value = self._f(*values)
        if new_value != self._value:
            self._value = new_value
            self._subject.on_next(new_value)
    # Assignment to value is forbidden, value is dependent on observables
    @property
    def value(self):
        return self._value

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

# Half adder testing
i_a = CreatePrimaryInput(0)
i_b = CreatePrimaryInput(0)
o_c, o_s = module_half_adder(i_a, i_b)
print('Half adder')
print('a b , c s')
for _ in range(2**2):
    i_a.value = _ & 1
    _ >>= 1
    i_b.value = _ & 1
    print(int(i_a.value), int(i_b.value), ',', int(o_c.value), int(o_s.value))

# Full adder testing
i_a = CreatePrimaryInput(0)
i_b = CreatePrimaryInput(0)
i_c = CreatePrimaryInput(0)
o_c, o_s = module_full_adder(i_a, i_b, i_c)
print('\nFull adder')
print('a b i , o s')
for _ in range(2**3):
    i_a.value = _ & 1
    _ >>= 1
    i_b.value = _ & 1
    _ >>= 1
    i_c.value = _ & 1
    print(int(i_a.value), int(i_b.value), int(i_c.value), ',', int(o_c.value), int(o_s.value))