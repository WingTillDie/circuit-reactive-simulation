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
        self._value = new_value
        self._subject.on_next(new_value)
    # Assignment to value is forbidden, value is dependent on observables
    @property
    def value(self):
        return self._value

# Similar to CreateWire
class CreateRegister:
    def __init__(self, clk, reset_value):
        # D is pseudo primary output, PPO
        self.D = self.CreateD(reset_value)
        # Q is pseudo primary input, PPI
        # clk is primary input
        self.Q = self.CreateQ(self, clk, reset_value)
    def get_Q_D(self):
        return self.Q, self.D
    class CreateD:
        def __init__(self, reset_value):
            # Temporary, for initial value
            self._subject = CreatePrimaryInput(reset_value)

        # Note: self.D is a CreateWire() ?
        def set(self, subject):
            self._subject = subject
        @property
        def value(self):
            return self._subject.value
    class CreateQ:
        def __init__(self, parent, clk, reset_value):
            self.parent = parent
    
            # For reference for comparison operator in first call of observer
            self._value = reset_value
            
            self._subject = Subject()
    
            clk._subject.subscribe(
                self.observer
            )
            
        def observer(self, values):
            new_value = self.parent.D.value
            if new_value != self._value:
                self._value = new_value
                self._subject.on_next(new_value)
        # Assignment to value is forbidden, value is dependent on observables
        @property
        def value(self):
            return self._value

class CreateRegisterResetAsync(CreateRegister):
    def __init__(self, clk, reset, reset_value):
        self.D = self.CreateD(reset_value)
        self.Q = self.CreateQ(self, clk, reset, reset_value)
    class CreateQ:
        def __init__(self, parent, clk, reset, reset_value):
            self.parent = parent
    
            # For reference for comparison operator in first call of observer
            self._value = reset_value
            
            self._subject = Subject()

            self._reset_value = reset_value

            clk._subject.subscribe(
                self.observer_clk
            )
            reset._subject.subscribe(
                self.observer_reset
            )
        def observer_clk(self, values):
            new_value = self.parent.D.value
            if new_value != self._value:
                self._value = new_value
                self._subject.on_next(new_value)
        def observer_reset(self, values):
            new_value = self._reset_value
            if new_value != self._value:
                self._value = new_value
                self._subject.on_next(new_value)
        # Assignment to value is forbidden, value is dependent on observables
        @property
        def value(self):
            return self._value

class CreateRegisterLoadAsync(CreateRegister):
    def __init__(self, clk, load):
        self.D = self.CreateD(load)
        self.Q = self.CreateQ(self, clk, load)
    class CreateQ:
        def __init__(self, parent, clk, load):
            self.parent = parent
    
            # For reference for comparison operator in first call of observer
            self._value = load
            
            self._subject = Subject()

            clk._subject.subscribe(
                self.observer_clk
            )
            load._subject.subscribe(
                self.observer_load
            )
        def observer_clk(self, values):
            new_value = self.parent.D.value
            if new_value != self._value:
                self._value = new_value
                self._subject.on_next(new_value)
        def observer_load(self, value):
            new_value = value
            if new_value != self._value:
                self._value = new_value
                self._subject.on_next(new_value)
        # Assignment to value is forbidden, value is dependent on observables
        @property
        def value(self):
            return self._value

# Similar to CreatePrimaryInput
class CreateClock:
    def tick(self):
        # Doesn't actually update the value of clock, but notify subscribers that clock has ticked
        self._subject.on_next(1)
    def __init__(self):
        #self = CreatePrimaryInput(1)
        # 1 means posedge or clock enabled
        self._subject = BehaviorSubject(1)
    # @property
    # def value(self):
    #     return self._subject.value
    # @value.setter
    # def value(self, new_value):
    #     if new_value != self.value:
    #         self._subject.on_next(new_value)

def module_seq_Q_bar(clk, reset_value):
    Q, D = CreateRegister(clk, reset_value).get_Q_D()
    Q_next = CreateWire(lambda Q: not Q, Q)
    D.set(Q_next)
    return Q

# Create sequential circuit
# For <= assignments
class CreateSeq:
    def __init__(self, clk, reset_value):
        self.Q, self.D = CreateRegister(clk, reset_value).get_Q_D()
    def get_Q(self):
        return self.Q
    def set_f(self, *f_and_reactive_or_dependent_variables):
        # Q_next is a PPO
        Q_next = CreateWire(*f_and_reactive_or_dependent_variables)
        self.D.set(Q_next)

class CreateSeqResetAsync:
    def __init__(self, clk, reset, reset_value):
        self.Q, self.D = CreateRegisterResetAsync(clk, reset, reset_value).get_Q_D()
    def get_Q(self):
        return self.Q
    def set_f(self, *f_and_reactive_or_dependent_variables):
        Q_next = CreateWire(*f_and_reactive_or_dependent_variables)
        self.D.set(Q_next)

class CreateSeqLoadAsync:
    def __init__(self, clk, load):
        self.Q, self.D = CreateRegisterLoadAsync(clk, load).get_Q_D()
    def get_Q(self):
        return self.Q
    def set_f(self, *f_and_reactive_or_dependent_variables):
        Q_next = CreateWire(*f_and_reactive_or_dependent_variables)
        self.D.set(Q_next)

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
#test_counter()

def test_counter_reset_async():
    clk = CreateClock()
    reset = CreateClock()
    seq = CreateSeqResetAsync(clk, reset, reset_value=10)
    Q = seq.get_Q()
    seq.set_f(lambda Q: Q+1, Q)
    print('Q <= Q+1')

    print(Q.value)

    clk.tick()
    print(int(Q.value))

    clk.tick()
    print(int(Q.value))

    clk.tick()
    reset.tick()
    print(int(Q.value))

    clk.tick()
    print(int(Q.value))

    print()
test_counter_reset_async()

def test_counter_load_async():
    clk = CreateClock()
    load = CreatePrimaryInput(10)
    seq = CreateSeqLoadAsync(clk, load)
    Q = seq.get_Q()
    seq.set_f(lambda Q: Q+1, Q)
    print('Q <= Q+1')

    print(Q.value)

    clk.tick()
    print(int(Q.value))

    clk.tick()
    print(int(Q.value))

    clk.tick()
    load.value = 19
    print(int(Q.value))

    clk.tick()
    print(int(Q.value))

    print()
#test_counter_load_async()

def test_module_seq_Q_bar():
    # Sequential circuit testing
    clk = CreateClock()

    Q = module_seq_Q_bar(clk, reset_value=0)

    print('Q <= !Q')
    print(Q.value)
    for _ in range(3):
        clk.tick()
        print(int(Q.value))
    print()
test_module_seq_Q_bar()

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

def test_module_half_adder():
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
    print()
test_module_half_adder()

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