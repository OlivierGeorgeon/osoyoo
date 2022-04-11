from Osoyoo import *
mem = MemoryV1()
hexMem = HexaMemory(50,50)
synthe = Synthesizer(mem,hexMem)
view = EgoMemoryWindowNew()
hexaview = HexaView()
controller = ControllerNew(Agent6(mem,hexMem),mem,synthesizer = synthe, hexa_memory = hexMem,
                    view = view, hexaview = hexaview, automatic = False)
print("Debut loop")
controller.main()