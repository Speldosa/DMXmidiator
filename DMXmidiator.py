#######################
### Import packages ###
#######################
from dmx import Colour, DMXInterface, DMXLight3Slot, DMXUniverse
import mido
import math
### Used for debugging.
from time import sleep
import time # Use time.perf_counter() to get the current time.


########################
### Global variables ###
########################
Number_of_lights = 1
Global_Max_brightness = 127 #In DMX value.
Max_Attack_cycles = 128
Max_Decay_cycles = 128
Max_Sustain_cycles = 128
Max_Release_cycles = 128
Max_LFO_cycles = 256

############################
### Function definitions ###
############################
def cpython_v(m1, m2, hue):
    hue = hue % 1.0
    if hue < (1.0/6.0):
        return m1 + (m2-m1)*hue*6.0
    if hue < 0.5:
        return m2
    if hue < (2.0/3.0):
        return m1 + (m2-m1)*((2.0/3.0)-hue)*6.0
    return m1

def cpython_hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h*6.0) # XXX assume int() truncates!
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i%6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q

def hsv_to_dmx_rgb(Hue, Saturation, Value):
    Tmp = cpython_hsv_to_rgb(Hue, Saturation, Value)
    return(Colour(round(Tmp[0]*Global_Max_brightness), round(Tmp[1]*Global_Max_brightness), round(Tmp[2]*Global_Max_brightness)))

def CC_to_ratio(CC_input):
    return(CC_input/127)


#########################
### Class definitions ###
#########################
class Layer0:
    def __init__(Self, Number_of_lights):
        ### Create a universe.
        universe = DMXUniverse()

        ### Define a light.
        Self.Array_of_lights = []
        for Count in range(Number_of_lights):
            Light = DMXLight3Slot(address=1+(3*Count))
            Self.Array_of_lights.append(Light)
            universe.add_light(Light)

        ### Update the interface's frame to be the universe's current state
        interface.set_frame(universe.serialise())

        ### Send an update to the DMX network
        interface.send_update()

    def Let_there_be_light(Self, Light_number, Hue, Saturation, Brightness):
        Self.Array_of_lights[Light_number].set_colour(hsv_to_dmx_rgb(Hue, Saturation, Brightness))

class Layer1:
    def __init__(Self, Number_of_lights):
        Self.Array_of_Layer1_objects = []
        for i in range(Number_of_lights):
            Self.Array_of_Layer1_objects.append(
                Layer1_light_object(
                    Hue = Signal(ADSR(After_attack_amplitude=0, After_decay_amplitude=0, Attack=0, Decay=0, Sustain=0, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                    Saturation = Signal(ADSR(After_attack_amplitude=0, After_decay_amplitude=0, Attack=0, Decay=0, Sustain=0, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                    Brightness = Signal(ADSR(After_attack_amplitude=0, After_decay_amplitude=0, Attack=0, Decay=0, Sustain=0, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                )
            )

    def Update(Self):
        pass # Hmmmm.... Ska uppdatera Current_value.

class Layer1_light_object:
    def __init__(Self, Hue, Saturation, Brightness):
        Self.Hue = Hue
        Self.Saturation = Saturation
        Self.Brightness = Brightness

    def Update(Self):
        Self.Hue.Update()
        Self.Saturation.Update()
        Self.Brightness.Update()

class Signal:
    def __init__(Self, ADSR, LFO):
        Self.ADSR = ADSR
        Self.LFO = LFO
        Self.Current_value = 0.0

    def Update(Self):
        Self.ADSR.Update()
        Self.LFO.Update()
        Self.Current_value = Self.ADSR.Current_value * Self.LFO.Current_value

class ADSR:
    def __init__(Self, After_attack_amplitude, After_decay_amplitude, Attack, Decay, Sustain, Release):
        Self.After_attack_amplitude = After_attack_amplitude
        Self.After_decay_amplitude = After_decay_amplitude
        Self.Attack = Attack
        Self.Decay = Decay
        Self.Sustain = Sustain
        Self.Release = Release
        Self.Progress = 0.0
        Self.Current_value = 0.0
        Self.Initialize_release_phase = False
        Self.Transition_to_release_value = -1.0

    def Update(Self):
        if(Self.Initialize_release_phase and (Self.Progress < 0.75)):
            Self.Progress = 0.75

        if(round(Self.Progress, 2) < 0.25): #Attack phase
            # TODO This whole blcok (the three next lines) where Attack_cycles is calculated can later be moved up to the __init__ function so that it only has to be computed once. This goes for the other phases (decay, sustain, and release) as well.
            Attack_cycles = round(Max_Attack_cycles * Self.Attack)
            if Attack_cycles == 0:
                Attack_cycles = 1
            Self.Progress = Self.Progress + (0.25 / Attack_cycles)
            Self.Current_value = round((Self.Progress * 4) * Self.After_attack_amplitude, 3)

        elif(round(Self.Progress, 2) < 0.50): #Decay phase. Can go higher than the the end of the attack phase.
            if(Self.Progress < 0.25):
                Self.Progress = 0.25
            Decay_cycles = round(Max_Decay_cycles * Self.Decay)
            if Decay_cycles == 0:
                Decay_cycles = 1
            Self.Progress = Self.Progress + (0.25 / Decay_cycles)
            Self.Current_value = round(Self.After_attack_amplitude - ((Self.After_attack_amplitude - Self.After_decay_amplitude) * ((Self.Progress - 0.25) * 4)), 3)

        elif(round(Self.Progress, 2) < 0.75): #Sustain phase
            if(Self.Progress < 0.50):
                Self.Progress = 0.50
            if(Self.Sustain > 1.0): # Hold the sustain phase if Sustain is set to more than 1.0.
                Self.Current_value = Self.After_decay_amplitude
            else:
                Sustain_cycles = round(Max_Sustain_cycles * Self.Sustain)
                if Sustain_cycles == 0:
                    Sustain_cycles = 1
                Self.Progress = Self.Progress + (0.25 / Sustain_cycles)
                Self.Current_value = Self.After_decay_amplitude

        elif(round(Self.Progress, 2) < 1.0): #Release phase. It will always use the aloted time set for release time.
            if(Self.Progress < 0.75):
                Self.Progress = 0.75
            if(Self.Transition_to_release_value == -1):
                Self.Transition_to_release_value = Self.Current_value
            Release_cycles = round(Max_Release_cycles * Self.Release)
            if Release_cycles == 0:
                Release_cycles = 1
            Self.Progress = Self.Progress + (0.25 / Release_cycles)
            Self.Current_value = Self.Transition_to_release_value - (Self.Transition_to_release_value * ((Self.Progress - 0.75) * 4))

class LFO:
    def __init__(Self, Waveform, Amplitude, Repeat, Rate, Phase):
        Self.Waveform = Waveform
        Self.Amplitude = Amplitude
        Self.Repeat = Repeat
        Self.Rate = Rate
        Self.Phase = Phase
        Self.Progress = 0.0
        Self.Current_value = 1.0

    def Update(Self):
        if(round(Self.Progress, 2) >= 1):
            if(Self.Repeat):
                Self.Progress = 0
        if(not Self.Repeat and (round(Self.Progress, 2) >= 1)):
            Self.Current_value = math.sin(math.pi * 2 * ((0 + (1 * Self.Phase)) % 1)) * Self.Amplitude + 1
        else:
            Self.Current_value = math.sin(math.pi * 2 * ((Self.Progress + (1 * Self.Phase)) % 1)) * Self.Amplitude + 1
            if(Max_LFO_cycles < 4): # Fastest possible number of cycles for the LFO is 4.
                Max_LFO_cycles_updated = 4
            else:
                Max_LFO_cycles_updated = Max_LFO_cycles
            LFO_cycles = 4 + round((Max_LFO_cycles_updated - 4) * (1 - Self.Rate))
            Self.Progress = Self.Progress + 1/LFO_cycles

class Layer2:
    def __init__(Self, Number_of_lights, Program, Sub_program, Parameter1, Parameter2, Parameter3, Parameter4, Parameter5, Parameter6, Parameter7, Parameter8):
        Self.Number_of_lights = Number_of_lights
        Self.Program = Program
        Self.Sub_program = Sub_program
        Self.Parameter1 = Parameter1
        Self.Parameter2 = Parameter2
        Self.Parameter3 = Parameter3
        Self.Parameter4 = Parameter4
        Self.Parameter5 = Parameter5
        Self.Parameter6 = Parameter6
        Self.Parameter7 = Parameter7
        Self.Parameter8 = Parameter8


#######################
### Useful commands ###
#######################
### ### print(mido.get_input_names()) # Get a list of all available input ports.


####################
### Main program ###
####################
### Open an interface
# with DMXInterface("FT232R") as interface:
with DMXInterface("Dummy") as interface:

    ### Initialize a Layer0.
    Layer0 = Layer0(Number_of_lights = Number_of_lights)

    ### Initialize a Layer1.
    Layer1 = Layer1(Number_of_lights = Number_of_lights)

    ### Initialize a Layer2.
    Layer2 = Layer2(
        Number_of_lights = Number_of_lights,
        Program = 1, # Can take on values between 1-8. This could be extended, but with 8 different programs, they can all be accessed via the white keys on piano keyboard within the same octave.
        Sub_program = 1, # Can take on values between 1-5. This could be extended, but with 5 different sub programs, they can all be accessed via the black keys on piano keyboard within the same octave.
        Parameter1 = 0, # Is set by CC1, which can take on values between 0-127
        Parameter2 = 0, # Is set by CC2, which can take on values between 0-127
        Parameter3 = 0, # Is set by CC3, which can take on values between 0-127
        Parameter4 = 0, # Is set by CC4, which can take on values between 0-127
        Parameter5 = 0, # Is set by CC5, which can take on values between 0-127
        Parameter6 = 0, # Is set by CC6, which can take on values between 0-127
        Parameter7 = 0, # Is set by CC7, which can take on values between 0-127
        Parameter8 = 0  # Is set by CC8, which can take on values between 0-127
    )

    ### Test suite.

    ### ### I'm setting all of the Layer1 objects to a certain profile just to test this out.
    for Count in range(len(Layer1.Array_of_Layer1_objects)):
        Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
            Hue = Signal(ADSR(After_attack_amplitude=0.5, After_decay_amplitude=0.85, Attack=0.05, Decay=0.05, Sustain=0.10, Release=0.10), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=1, Phase=0)),
            Saturation = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
            Brightness = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
        )

    while True:
        Layer1.Update()
        for Light_number in range(len(Layer0.Array_of_lights)):
            Layer1.Array_of_Layer1_objects[Light_number].Update()
            print("ADSR Progress:")
            print(Layer1.Array_of_Layer1_objects[Light_number].Hue.ADSR.Progress)
            print("ADSR value:")
            print(Layer1.Array_of_Layer1_objects[Light_number].Hue.ADSR.Current_value)
            print("LFO Progress:")
            print(Layer1.Array_of_Layer1_objects[Light_number].Hue.LFO.Progress)
            print("LFO value:")
            print(Layer1.Array_of_Layer1_objects[Light_number].Hue.LFO.Current_value)
            print("Combined Value:")
            print(Layer1.Array_of_Layer1_objects[Light_number].Hue.Current_value)
            print("")
            # Layer0.Let_there_be_light(Light_number, (Hue=Layer1.Array_of_Layer1_objects[Light_number].Hue.Current_value % 1), Saturation=Layer1.Array_of_Layer1_objects[Light_number].Saturation.Current_value, Value=Layer1.Array_of_Layer1_objects[Light_number].Brightness.Current_value)
