from stage_titouan import *
mem = MemoryV1()
hexMem = HexaMemory(50,200, cell_radius = 20)
synthe = SynthesizerUserInteractionV2(mem,hexMem)
view = EgocentricView()
hexaview = HexaView(hexa_memory = hexMem)
controller = ControllerUserActionV2(Agent5(),mem, ip = "192.168.8.189",synthesizer = synthe, hexa_memory = hexMem,
                    view = view, hexaview = hexaview, automatic = False)
print("Debut loop")
controller.main()