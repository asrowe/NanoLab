# NanoLab
A design study on lab workflows to inform building a laboratory informatics engine

## Introduction

The concept of digitizing the work in a scientific research library needs at a core three main categories of computational building block:
* **Entities** - the tools and methods to manipulate the digital models of the materials found in the lab.
* **Workflows** - the tools and methods to digitally model and orchestrate the flow of work in a lab.
* **Results Analysis** - the tools and methods to organise, analyse and report on the data generated in the lab.

When designing software to digitizing work undertaken we need to seamlessly work accross all of these modules, depending on the task at hand, and that requires a modern informatics system that enables all of these capabilites.

In the MicroLab project we are trying to build a simple engine that enables a pedagological analysis of the building blocks and their interactions to help navigate the landscape of very neuanced technology. However, MicroLab itself does not always lend itself to a gradual learning curve. Instead we have developed NanoLab - an even tinier engine to build a basic intuition of the concepts.

This notebook first takes you through the entire engine - Then demonstrates some toy workflows to help demonstrate its use.

## NanoLab
NanoLab is based on the concept of singleton science, where you manage all of your individual samples as distict entities - so it is kind of like high scool chemisty. Even at this level it is informative to help understand the interplace between the three categories mentioned in the introduction: Entities, Workflows and Results Analysis.

Lets dive in:

### Entitites
In NanoLab we try to model two core entities that you need to maintain track of in the lab:
1. **Samples** - representing a sample of physical material that you use in your experimentation. 
2. **Labware** - representing the containers that are used to hold and mix the samples in your work

#### Samples

Lets dive in with the sample model:

```
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
```

The sample object tracks the following variables:

##### Naming:

* **ID** - The primary ID of the sample. In Nanolab this is tracked by a string you might give the sample

##### Concentration:

* **Concentration** - Tracks the concentration of a sample in a _solvent_. (A float)
* **Concentration Units** - Tracks the units of concentration. (A string)
* **Solvent** - The solvent a sample is desolved in (A string)

##### Sample Tracking:

* **Parents** - a pointer to samples that this sample was creates from
* **UnitOp** - a pointer to the Unit Operation (more on these later) that created the sample

##### Geneology:

A critical requirment for a sample it to understand its geneology. The Geneology methods generates a data structure the details all of the upstream operations that have taken place to produce this samples. This is accessed by the methods: 
* **Geneology method** - generates a data structure for further analysis
* **PrintGeneology** - dumps current geneology to a string for inspection and debugging

#### Labware

The **LabWare** object builds out a definiton of the containers (like test tubes) we use to study our samples in:

```
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
```
The Labware object tracks the following variables:

_Note: Currently we do not identify the labware, this simplification may be updaed in the future._


Contents:

* **Contents** - The sample that is contained in the labware
* **Quantity** - A measure of how much sample is contained in the labware
* **Quuantity Units** - The units of the quantity variable


Labware Tracking:

* **Parents** - if an operation creates new labware, as opposed to using the same labware. then the predecessor labware is tracked though this ponter.

### Unit Operations

Unit Operations (UnitOp) are the second category of building block in NanoLab. The represent an atomic action of work in the lab. 

NanoLab workflows are built by creating and combining unit operations into a process that executes a scientific protocol.

The library of UnitOps define the scope of how a lab can manipulate samples - new unit operations can be added to the NanoLab library to represent other capabilites. And finally as Unit operations are just code. Then higher level reusable functions can be built for common patterns of lab computation.

Unit Operations are _"Entity Aware"_ in that they operate by computing over labware and sample entities.

In the industrial engineering world, factories are modelled according to a standard called [ISA-88](https://en.wikipedia.org/wiki/ISA-88). We don't really consider this at all, other than noting that there is a ton of work in modelled industrial batch processes that were totally ignoring.

The current library of Unit Operation in NanaLab is:

* **Dispenser** - The dispenser unit op models despensing a quantity of sample into a new item of labware. It is typically the inital elements of any NanoLab flow

* **Analyser** = The analyser unit op models recording a measurement from a sample. For example the samples weight or a test result. This typically is the final element of a NanoLab flow.

* **Register** - The Register unit op models the process of giving a sample a specific name, do distinguish it from other samples. For the purposes of NanoLab is enable renaming a _sample.id_

* **Serialiser** - The Serialiser unit op is used to take a set of samples and update them with a unique serial number (appending it to the _sample.id_)

* **Incubator** - The Incubator unit op models the laboratory process of incubating or holding a sample at a specific temperature for a specific time.

* **Aliquoter** - The Aliquoter unit op models the laboratory process of measuring out a fixed amount of a sample into new labware. Tyically splitting a sample prior to taking a specific meaurement. 
* **Mixer** - The Mixer unit op models the process of Mixing two samples together.

* **Diluter** - The Diluter unit op model the process of diluting the sample by updating the _sample.concentration_ value

Using this simple library of operations we can build some common and useful laboratory workflows in order to model and understand the flow of information accross different workflows.

Exploring each one is more detail:

#### Dispenser

The Dispenser unit op is the primary mechanism in Nanolab to create new entities. The intuition of the comes from the idea of a lab store which dispenses a certain amount of material so that it can be used in experimentation.

When called, a Dispenser first creates a new sample with the required properties and then an an new Labware object for it to explore with it properties.

```
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
```

#### Register

The Register operation creates a new sample object with a differnt sample.id. Critically it remains in the same labware. 

The intutition is that we're giving this samples a specific name for reasons of distingishing it later. These might be the preparation of a specific sample for testing, or giving a mixture a currents sample:

_Note:_ due to the design of the unit ops to have a single variable so that they are easily available to the "map" construct. There is not a version of rename that injects a string at calltime. The matches the idea that in production registration would be backed by a registration engine that would assign it a name in a global register.

```
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
```

##### Notes on Register

* TODO

#### Serialiser

The serialiser operation allows a sample.id to have a serial number appended to the name of id. so that "mysample" becomes "mysample_2" where 2 is provided a runtime based on the initalisation of the Seraliser unit op. 

The intutition is that frequently samples are broken into sub samples (see the Aliquoter) and this allows them to be named uniquly. When combeined with the Register unit operation. This can provided some quite complex logic for processing samples

In this implementatation each Serialiser holds a counter. When it is called on a piece of labware it _clones_ the sample but  updating the id of new sample by appending the counter number onto the end of _sample.id_, and adding the serialise operation to the *operations graph*.

```    
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

```
##### Notes on the serialiser
* The serialiser creates a new sample. We do this because of wanting to track the unit operation that has been applied. But technically the sample is the same. This means that we have to build a more neuanced understanding of sample changes (material changes vs metadata changes) to build a correctly trackable sample lineage. 

* We have started to use map function calling over the unit operations of NanoLab. IMO this is a sign of clean class logic. It is unclear to me if for this set of operator we need labware or if we could have achived it with just a sample object.

#### Incubator

The Incubator unit operation represents the idea of holding a sample at a certain temperature for a certain time to enable a chemical change to take place.

In the Nanolab implementation.... well its currently horrible. It doesn't clone the sample and it doesn't track in the operations graph and details of the incubation operation.

```
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
```

##### Notes on Incubator

* Something to consider in comparison to the Register/Serialiser operations. The Incubator operation is used to allow a chemical change to happen. The contents of the labware change. But what do we need to track. It it actually a new sample object? Did the reaction take place ? Obviously in reality this is the role of analytical assays to check this. But until confirmed experimentally is creating a new sample object the best way to track things.

#### Aliquoter

```
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

```

#### Mixer
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

#### Diluter

TODO

#### Analyser

TODO