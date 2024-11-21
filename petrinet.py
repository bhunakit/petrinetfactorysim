from dataclasses import dataclass, field
from typing import List
import graphviz

@dataclass
class Place:
    name: str
    tokens: int

@dataclass
class Arc:
    place: Place
    cost: int

@dataclass
class Transition:
    name: str
    input_arcs: List[Arc]
    output_arcs: List[Arc]

    def is_enabled(self):
        for arc in self.input_arcs:
            if arc.place.tokens < arc.cost:
                return False
        return True

    def fire(self):
        if self.is_enabled():
            for arc in self.input_arcs:
                arc.place.tokens -= arc.cost
            for arc in self.output_arcs:
                arc.place.tokens += arc.cost
            return True
        return False

@dataclass
class PetriNet:
    name: str
    places: List[Place]
    arcs: List[Arc]
    transitions: List[Transition]

    def run(self, firing_sequence):
        for transition_name in firing_sequence:
            transition = self.find_transition(transition_name)
            if transition.fire():
                print(f"{transition.name} fired!")
            else:
                print(f"{transition.name} did not fire.")

    def find_transition(self, name):
        for transition in self.transitions:
            if transition.name == name:
                return transition
        raise ValueError(f"Transition '{name}' not found.")
    
    def find_place(self, name):
        for place in self.places:
            if place.name == name:
                return place
        raise ValueError(f"Place '{name}' not found")

    def visualize(self):
        """
        Create a graphviz visualization of the Petri net.
        """
        g = graphviz.Digraph(format='png')

        for place in self.places:
            g.node(place.name, shape='circle', style='filled', fillcolor='yellow', label=f"{place.name}\n{place.tokens}", fixedsize='true',  width='1.5', height='1.5')  
        
        for transition in self.transitions:
            g.node(transition.name, shape='rectangle')
            for arc in transition.input_arcs:
                g.edge(arc.place.name, transition.name, label=str(arc.cost))
            for arc in transition.output_arcs:
                g.edge(transition.name, arc.place.name, label=str(arc.cost))

        g.render(self.name, directory="graphs")
        print(f"Petri net visualization saved as '{self.name}.png'.")

if __name__ == "__main__":
    p1 = Place("p1", 1)
    p2 = Place("p2", 2)
    p3 = Place("p3", 3)
    p4 = Place("p4", 2)

    t1 = Transition("t1", [Arc(p1, 1), Arc(p2, 1)], [Arc(p2, 1), Arc(p3, 1)])
    t2 = Transition("t2", [Arc(p2, 1), Arc(p3, 1)], [Arc(p4, 1), Arc(p1, 1)])

    petri_net = PetriNet(
        name="Petri Net",
        places=[p1, p2, p3, p4],
        arcs=[
            Arc(p1, 1),
            Arc(p2, 1),
            Arc(p2, 1),
            Arc(p3, 1),
            Arc(p2, 1),
            Arc(p3, 1),
            Arc(p4, 1),
            Arc(p1, 1)
        ],
        transitions=[t1, t2]
    )

    petri_net.run(["t1", "t1", "t2", "t1"])
    petri_net.visualize()