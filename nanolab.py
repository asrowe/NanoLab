

class Sample:
    def __init__(self, id, parents, unit_op, concentration= None, conc_unit=None, solvent=None):
        self.id = id
        self.unit_op = unit_op
        self.concentration = concentration
        self.conc_unit = conc_unit
        self.solvent = solvent
        self.parents = parents
    
    
    def __str__(self):

        if self.concentration is None:
            out = str(self.id)
        else:
            out = f"{str(self.id)} at {self.concentration}{self.conc_unit} in {self.solvent}"

        return out
    
    def __repr__(self):
        return self.__str__()
    
    def cloneAs(self, id, parents: list, unit_op: str):
        out = Sample(id, parents, unit_op, self.concentration, self.conc_unit, self.solvent)
        return out

    def _treewalker(self, acc, depth=0) -> list:
        node = (depth, self)

        acc.append(node)        
        if self.parents is not None:
            for parent in self.parents:
                parent._treewalker(acc,depth+1)

        return acc

    def printHistory(self) -> None:
        out = self._treewalker([])
        out = [ f"{'  ' * depth}Sample:{str(sample)} <-Unit Op({sample.unit_op})" for depth, sample in out]
        for i in out:
            print(i)

    

    
class Labware:

    def __init__(self, contents : Sample, quantity, unit):
        
        self.contents = contents
        self.quantity = quantity
        self.unit = unit


    def __str__(self) -> str:
        out = ""
        if self.quantity is None:
            out = str(self.contents)
        else:
            out = f"{self.quantity} {self.unit}: {str(self.contents)}"
        return out
    
    def canAilquot(self, quantity, unit) -> bool:
        return self.quantity is not None and unit == self.unit and quantity < self.quantity
    
    def aliquot(self, quantity, unit, Force) -> None:
        if self.canAilquot(quantity,unit):
            self.quantity = self.quantity - quantity
        elif Force:
            self.quantity = None
        else:
            raise ValueError("Insufficient quantitiy of sample or incompatable units, Try forcing it")
    
    def __repr__(self) -> str:
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
    
    def __call__(self, sample_id, quantity, unit, concentration=None, conc_unit=None,solvent=None):
        
        contents = Sample(sample_id, None , "Dispenser", concentration, conc_unit, solvent )
        out = Labware(contents, quantity, unit)
        return out

    def __str__(self):
        out = "Creating a new labware with a user defined contents"
        return out
    
#
# Register operation to model giving a sample of merit a new name
#
class Register(UnitOp):
    def __init__(self,sample_name: str, prepend=False) -> None:
        self.sample_name = sample_name
        self.prepend = prepend
    
    def __call__(self, current: Labware)-> Labware:
        
        
        if self.prepend:
            updated_id = self.sample_name + current.contents.id
        else:
            updated_id = self.sample_name

        registered_sample = current.contents.cloneAs(updated_id, [current.contents], "Register" )        

        current.contents = registered_sample
        return current

    
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
        
        serialised_sample = current.contents.cloneAs(new_id, [current.contents], "Serialiser" )        

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
       
        incubated_sample = current.contents.cloneAs(current.contents.id, [current.contents], "Incubated" )
        current.contents = incubated_sample
        return current

    def __str__(self):
        out = f"Incubate for {self.time}{self.time_unit} at {self.temp}{self.temp_unit}"
        return out


#
# Aliquoting operation to create subsamples from the current sample
#
class Aliquoter(UnitOp):
    def __init__(self, quantity, unit, force=False) -> None:
        self.quantity = quantity
        self.unit = unit
        self.force = force
    
    def __call__(self, current :Labware)-> Labware:
        
        current.aliquot(self.quantity, self.unit, self.force)
        aliquot_sample = current.contents.cloneAs(current.contents.id, [current.contents], "Ailiquot" )
        out = Labware(aliquot_sample, quantity=self.quantity, unit=self.unit)
        
        return out

    def __str__(self) -> str:
        out = f"Aliquoting {self.quantity} {self.unit} of sample"
        return out

#
# Mixes the contents of two labwares. 
#
class Mixer(UnitOp):
    def __init__(self):
        pass
    
    def __call__(self, current :Labware, other:Labware) -> Labware:
        mix_sample = Sample("Mixture",[current.contents, other.contents],"Mixer" )
        current.contents = mix_sample

        #aftermixing - other is empty
        other.contents = Sample("Empty", None,None)
        other.quantity = None
        other.unit = None
        
        #current is added to if the units match
        if current.quantity is not None and current.unit == other.unit:
            current.quantity = current.quantity + other.quantity # type: ignore
        else:
            current.quantity = None
            current.unit = None
        
        return current

    def __str__(self):
        out = "Mixing two labware contents together"
        return out
    

