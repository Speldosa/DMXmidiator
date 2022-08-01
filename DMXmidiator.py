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
Number_of_lights = 32
Global_Max_brightness = 64 #In DMX value.
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
        Self.universe = DMXUniverse()

        ### Define a light.
        Self.Array_of_lights = []
        for Count in range(Number_of_lights):
            Light = DMXLight3Slot(address=1+(3*Count))
            Self.Array_of_lights.append(Light)
            Self.universe.add_light(Light)

        ### Update the interface's frame to be the universe's current state
        interface.set_frame(Self.universe.serialise())

        ### Send an update to the DMX network
        interface.send_update()

    def Set_color(Self, Light_number, Hue, Saturation, Brightness):
        Self.Array_of_lights[Light_number].set_colour(hsv_to_dmx_rgb(Hue, Saturation, Brightness))
    
    def Let_there_be_light(Self):
        interface.set_frame(Self.universe.serialise())
        interface.send_update()

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
        for Layer1_object in Self.Array_of_Layer1_objects:
            Layer1_object.Update()

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

        else:
            Self.Current_value = 0
        

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
    def __init__(Self, Number_of_lights, Main_program, Sub_program, Parameter1, Parameter2, Parameter3, Parameter4, Parameter5, Parameter6, Parameter7, Parameter8):
        Self.Number_of_lights = Number_of_lights
        Self.Main_program = Main_program # Can take on values between 1-8. This could be extended, but with 8 different programs, they can all be accessed via the white keys on piano keyboard within the same octave.
        Self.Sub_program = Sub_program # Can take on values between 1-5. This could be extended, but with 5 different sub programs, they can all be accessed via the black keys on piano keyboard within the same octave.
        Self.Parameter1 = Parameter1 # Can take on values between 0-127.
        Self.Parameter2 = Parameter2 # Can take on values between 0-127.
        Self.Parameter3 = Parameter3 # Can take on values between 0-127.
        Self.Parameter4 = Parameter4 # Can take on values between 0-127.
        Self.Parameter5 = Parameter5 # Can take on values between 0-127.
        Self.Parameter6 = Parameter6 # Can take on values between 0-127.
        Self.Parameter7 = Parameter7 # Can take on values between 0-127.
        Self.Parameter8 = Parameter8 # Can take on values between 0-127.


#######################
### Useful commands ###
#######################
print(mido.get_input_names()) # Get a list of all available input ports.


####################
### Main program ###
####################
### Open an interface
# with DMXInterface("FT232R") as interface:
with DMXInterface("FT232R") as interface:

    ### Initialize a Layer0.
    Layer0 = Layer0(Number_of_lights = Number_of_lights)

    ### Initialize a Layer1.
    Layer1 = Layer1(Number_of_lights = Number_of_lights)

    ### Initialize a Layer2.
    Layer2 = Layer2(
        Number_of_lights = Number_of_lights,
        Main_program = 1, 
        Sub_program = 1, 
        Parameter1 = 0, 
        Parameter2 = 0,
        Parameter3 = 0,
        Parameter4 = 0,
        Parameter5 = 0,
        Parameter6 = 0,
        Parameter7 = 0,
        Parameter8 = 0
    )   
        
    CC1 = 64
    CC2 = 64
    CC3 = 64
    CC4 = 64
    CC5 = 64
    CC6 = 64
    CC7 = 64
    CC8 = 64    
        
    with mido.open_input('Roland Digital Piano:Roland Digital Piano MIDI 1 36:0') as inport:

        while True:
            waiting_cc_messages = []
            waiting_white_note_messages = []
            waiting_black_note_messages = []
            for msg in inport.iter_pending():
                if(msg.type == 'control_change'):
                    print(msg)
                    waiting_cc_messages.append(msg)
                elif hasattr(msg, 'note'):
                    if(msg.note == 60 or msg.note == 62 or msg.note == 64 or msg.note == 65 or msg.note == 67 or msg.note == 69 or msg.note == 71):
                        waiting_white_note_messages.append(msg)
                    elif(msg.note == 61 or msg.note == 63 or msg.note == 66 or msg.note == 68 or msg.note == 70):
                        waiting_black_note_messages.append(msg)

            for msg in waiting_cc_messages:
                if(msg.control == 1):
                    CC1 = msg.value
                elif(msg.control == 2):
                    CC2 = msg.value
                elif(msg.control == 3):
                    CC3 = msg.value
                elif(msg.control == 4):
                    CC4 = msg.value
                elif(msg.control == 5):
                    CC5 = msg.value
                elif(msg.control == 6):
                    CC6 = msg.value
                elif(msg.control == 7):
                    CC7 = msg.value
                elif(msg.control == 8):
                    CC8 = msg.value

            for msg in waiting_black_note_messages:
                # Sub program (black keys).
                if(msg.note == 61):
                    Layer2.Sub_program = 1
                elif(msg.note == 63):
                    Layer2.Sub_program = 2
                elif(msg.note == 66):
                    Layer2.Sub_program = 3
                elif(msg.note == 68):
                    Layer2.Sub_program = 4
                elif(msg.note == 70):
                    Layer2.Sub_program = 5

            for msg in waiting_white_note_messages:
            
                ### Program (white keys).
                
                ### ### Program 1: Whole field with ADSR, Sustain level, and HSV settings from CC.
                if(msg.note == 60): # Only respond to C4.
                    if(msg.type == 'note_on' and msg.velocity > 0):
                        for Count in range(Number_of_lights):
                            if(Layer2.Main_program == 1):
                                if(Layer2.Sub_program == 1):
                                    for Count in range(len(Layer1.Array_of_Layer1_objects)):
                                        Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Saturation = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Brightness = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                                        )
                                elif(Layer2.Sub_program == 2):
                                    for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                        Layer1.Array_of_Layer1_objects[int(Count + len(Layer1.Array_of_Layer1_objects)/2)] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Saturation = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Brightness = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                                        )
                                elif(Layer2.Sub_program == 3):
                                    for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                        Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Saturation = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Brightness = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                                        )
                                
                    if(msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)): # On Syntakt, note off is sent by sending note on with a velocity of 0.
                        if(Layer2.Main_program == 1):
                            for Count in range(len(Layer1.Array_of_Layer1_objects)):
                                Layer1.Array_of_Layer1_objects[Count].Hue.ADSR.Progress = 0.75
                                Layer1.Array_of_Layer1_objects[Count].Saturation.ADSR.Progress = 0.75
                                Layer1.Array_of_Layer1_objects[Count].Brightness.ADSR.Progress = 0.75
                                
                ### ### Program 2: Crazy fun. Random start of random lights.
                if(msg.note == 62): # Only respond to D4.
                    if(msg.type == 'note_on' and msg.velocity > 0):
                        for Count in range(Number_of_lights):
                            if(Layer2.Main_program == 1):
                                if(Layer2.Sub_program == 1):
                                    for Count in range(len(Layer1.Array_of_Layer1_objects)):
                                        Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Saturation = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=2, Release=0), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Brightness = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=0.50, Release=1), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                                        )
                                
                    if(msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)): # On Syntakt, note off is sent by sending note on with a velocity of 0.
                        if(Layer2.Main_program == 1):
                            for Count in range(len(Layer1.Array_of_Layer1_objects)):
                                Layer1.Array_of_Layer1_objects[Count].Hue.ADSR.Progress = 1.0
                                Layer1.Array_of_Layer1_objects[Count].Saturation.ADSR.Progress = 1.0
                                Layer1.Array_of_Layer1_objects[Count].Brightness.ADSR.Progress = 1.0
                                    
            # Basis for what eventually will be turned into a mediator between Layer1 and Layer0.
            Layer1.Update()
            for Light_number in range(len(Layer0.Array_of_lights)):
                Layer0.Set_color(Light_number, Hue=(Layer1.Array_of_Layer1_objects[Light_number].Hue.Current_value % 1), Saturation=Layer1.Array_of_Layer1_objects[Light_number].Saturation.Current_value, Brightness=Layer1.Array_of_Layer1_objects[Light_number].Brightness.Current_value)
            Layer0.Let_there_be_light()
