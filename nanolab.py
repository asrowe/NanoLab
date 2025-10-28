

class Sample:
    def __init__(self, id, concentration=None, conc_unit=None, solvent=None, _parents=(), _unit_op = "" ):
        self.id = id
        self.concentration = concentration
        self.conc_unit = conc_unit
        self.solvent = solvent
        self._parents = _parents
        self._unit_op = _unit_op
    
    def __str__(self):
        out = ""
        if self.concentration is None:
            out = str(self.id)
        else:
            out = f"{str(self.id)} at {self.concentration}{self.conc_unit} in {self.solvent}"

        return out
    
    def __repr__(self):
        return self.__str__()
    
    def cloneAs(self, id, parents: tuple, unit_op):
        out = Sample(id, self.concentration, self.conc_unit, self.solvent, parents, unit_op)
        return out
    
    def geneology(self):
        if len(self._parents) == 0:
            return (self._unit_op, self.id)
        else:
            return [p.geneology() for p in self._parents]
    
    def printGeneology(self, indent=""):
        print(indent + f"{self._unit_op}: {self.id}")
        if len(self._parents) == 0:
            pass
        else:
            indent += "  "
            for p in self._parents:
                p.printGeneology(indent=indent+"  ") 

class Labware:

    def __init__(self, contents : Sample, quantity, unit, _parents=()):
        
        self.contents = contents
        self.quantity = quantity
        self.unit = unit

        self._prev = _parents

    def __str__(self):
        out = ""
        if self.quantity is None:
            out = str(self.contents)
        else:
            out = f"{self.quantity} {self.unit}: {str(self.contents)}"
        return out
    
    def __repr__(self):
        return self.__str__()
    
#
#    Base Class for the unit operations in the Microlab engine.
#
class UnitOp:
    pass

#
# Dispenser operation to model adding some phsical sample into labware (i.e. a testtube)
#
class Dispenser(UnitOp):

    def __init__(self):
        pass
    
    def __call__(self, sample, quantity, unit, concentration=None, conc_unit=None,solvent=None):
        
        contents = Sample(sample, concentration, conc_unit, solvent,  _unit_op = "Dispensed as")
        
        out = Labware(contents, quantity, unit)
        return out

    def __str__(self):
        out = "Creating a new labware with a user defined contents"
        return out
    
#
# Register operation to model giving a sample of merit a new name
#
class Register(UnitOp):
    def __init__(self,sample_name, prepend=False):
        self.sample_name = sample_name
        self.prepend = prepend
    
    def __call__(self, current):
        
        new_id = self.sample_name
        if self.prepend:
            new_id = self.sample_name + current.contents.id

        registered_sample = current.contents.cloneAs(new_id, (current.contents,), "Registered as" )        

        current.contents = registered_sample
        return current

    def __rrshift__(self, other):
        self.__call__(other)

    def __str__(self):
        out = f"Registrying labware contents with name: {self.sample_name}"
        return out
    
#
# Seralise operation to model creating different serial numbers for samples
#     
class Serialiser(UnitOp):
    def __init__(self, counter=0):
        self.counter = counter
    
    def __call__(self, current):

        new_id = f"{current.contents.id}_{self.counter}"
        self.counter += 1
        
        serialised_sample = current.contents.cloneAs(new_id, (current.contents,), "Serialised as" )        

        current.contents = serialised_sample
        return current

    def __str__(self):
        out = f"Current Serial Numer: {self.counter}"
        return out


#
# Incubate operatation to model holding something at a fixed temp for period of time
#
class Incubator(UnitOp):
    def __init__(self, time, time_unit, temp, temp_unit):
        self.time = time
        self.time_unit = time_unit
        self.temp = temp
        self.temp_unit = temp_unit
    
    def __call__(self, current):
        incubated = Sample(current.contents.id, _parents=(current.contents,), _unit_op = "Incubated as" )

        current.contents = incubated
        return current

    def __str__(self):
        out = f"Incubate for {self.time}{self.time_unit} at {self.temp}{self.temp_unit}"
        return out


#
# Aliquoting operation to create subsamples from the current sample
#
class Aliquoter(UnitOp):
    def __init__(self, quantity, unit):
        self.quantity = quantity
        self.unit = unit
    
    def __call__(self, current):
        
        aliquot = Sample(current.contents.id, current.contents.concentration,current.contents.conc_unit, current.contents.solvent, _parents=(current.contents,), _unit_op="Aliquoted as")
        out = Labware(aliquot, quantity=self.quantity, unit=self.unit)
        current.contents = aliquot

        return out

    def __str__(self):
        out = f"Aliquoting {self.quantity} {self.unit} of sample"
        return out

#
# Mixes the contents of two labwares. 
#
class Mixer(UnitOp):
    def __init__(self):
        pass
    
    def __call__(self, current, other):
        mix = Sample("Mixture", _parents=(current.contents, other.contents), _unit_op = "Mixer")
        current.contents = mix
        current.quantity = None
        current.unit = None
        return current

    def __str__(self):
        out = "Mixing two labware contents together"
        return out