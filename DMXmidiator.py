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
Global_Max_brightness = 128 #In DMX value.
Max_Attack_cycles = 128
Max_Decay_cycles = 128
Max_Sustain_cycles = 128
Max_Release_cycles = 128
Max_LFO_cycles = 256
Clock_ticks_per_cycle = 3

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

def CC_to_ratio_with_binary_top_condition(CC_input): # Worthless name, but I can't think of anything better right now.
    if(CC_input == 127):
        return 2.0
    else:
        return(CC_input/126)

def CC_to_boolean(CC_input):
    if(CC_input < 64):
        return False
    else:
        return True

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
                    Hue = Signal(ADSR(After_attack_amplitude=0, After_decay_amplitude=0, Attack=0, Decay=0, Sustain=0, Release=0, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                    Saturation = Signal(ADSR(After_attack_amplitude=0, After_decay_amplitude=0, Attack=0, Decay=0, Sustain=0, Release=0, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                    Brightness = Signal(ADSR(After_attack_amplitude=0, After_decay_amplitude=0, Attack=0, Decay=0, Sustain=0, Release=0, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
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
    def __init__(Self, After_attack_amplitude, After_decay_amplitude, Attack, Decay, Sustain, Release, Ignore_go_to_release_phase):
        Self.After_attack_amplitude = After_attack_amplitude
        Self.After_decay_amplitude = After_decay_amplitude
        Self.Attack = Attack
        Self.Decay = Decay
        Self.Sustain = Sustain
        Self.Release = Release
        Self.Progress = 0.0
        Self.Current_value = 0.0
        Self.Go_to_release_phase = False # A boolean stating whether the release phase is forced or not (usually because of note off commands).
        Self.Ignore_go_to_release_phase = Ignore_go_to_release_phase #
        Self.Transition_to_release_value = 2.0 # Standard behavior (which is set by default). If Self.Transition_to_release_value is set to, for example, 0.50, the value will start at 0.50 whenever the release phase starts, no matter what the current value is.
        Self.Go_to_next_phase = False

    def Update(Self):
        if(Self.Go_to_release_phase and (Self.Progress < 0.75)):
            if(not Self.Ignore_go_to_release_phase):
                Self.Progress = 0.75
            
        Self.Go_to_next_phase = True

        if(round(Self.Progress, 2) < 0.25 and Self.Go_to_next_phase): #Attack phase
            Self.Go_to_next_phase = False
            # TODO This whole blcok (the three next lines) where Attack_cycles is calculated can later be moved up to the __init__ function so that it only has to be computed once. This goes for the other phases (decay, sustain, and release) as well.
            Attack_cycles = round(Max_Attack_cycles * Self.Attack)
            if Attack_cycles == 0:
                Self.Progress = 0.25
                Self.Go_to_next_phase = True
            else:
                Self.Progress = Self.Progress + (0.25 / Attack_cycles)
                Self.Current_value = round((Self.Progress * 4) * Self.After_attack_amplitude, 3)

        if(round(Self.Progress, 2) < 0.50 and Self.Go_to_next_phase): #Decay phase. Can go higher than the the end of the attack phase.
            Self.Go_to_next_phase = False
            if(Self.Progress < 0.25):
                Self.Progress = 0.25
            Decay_cycles = round(Max_Decay_cycles * Self.Decay)
            if Decay_cycles == 0:
                Self.Progress = 0.50
                Self.Go_to_next_phase = True
            else:
                Self.Progress = Self.Progress + (0.25 / Decay_cycles)
                Self.Current_value = round(Self.After_attack_amplitude - ((Self.After_attack_amplitude - Self.After_decay_amplitude) * ((Self.Progress - 0.25) * 4)), 3)

        if(round(Self.Progress, 2) < 0.75 and Self.Go_to_next_phase): #Sustain phase
            Self.Go_to_next_phase = False
            if(Self.Progress < 0.50):
                Self.Progress = 0.50
            if(Self.Sustain > 1.0): # If sustain is set to above 1.0...
                if(not Self.Ignore_go_to_release_phase):
                    Self.Current_value = Self.After_decay_amplitude # ...hold the sustain phase.
                else: # However, if Ignore_go_to_release_phase mode is activated, skip the sustain phase all together and move on to the release phase.
                    Self.Go_to_next_phase = True
                    Self.Progress = 0.75
            else:
                Sustain_cycles = round(Max_Sustain_cycles * Self.Sustain)
                if Sustain_cycles == 0:
                    Self.Progress = 0.75
                    Self.Go_to_next_phase = True
                else:
                    Self.Progress = Self.Progress + (0.25 / Sustain_cycles)
                    Self.Current_value = Self.After_decay_amplitude

        if(round(Self.Progress, 2) < 1.0 and Self.Go_to_next_phase): #Release phase. It will always use the aloted time set for release time.
            Self.Go_to_next_phase = False
            if(Self.Progress < 0.75):
                Self.Progress = 0.75
            if(Self.Release > 1.0): # Hold the release phase if Release is set to more than 1.0.
                Self.Current_value = Self.After_decay_amplitude
            else:
                if(Self.Transition_to_release_value == 2.0):
                    Self.Transition_to_release_value = Self.Current_value
                Release_cycles = round(Max_Release_cycles * Self.Release)
                if Release_cycles == 0:
                    Self.Progress = 1.00
                    Self.Go_to_next_phase = True
                else:
                    Self.Progress = Self.Progress + (0.25 / Release_cycles)
                    Self.Current_value = Self.Transition_to_release_value - (Self.Transition_to_release_value * ((Self.Progress - 0.75) * 4))

        if(round(Self.Progress, 2) >= 1.0 and Self.Go_to_next_phase):
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
        Self.Main_program = Main_program # Can take on values between 1-8. This could be extended, but with 8 different programs, they can all be accessed via the white keys on piano keyboard within the same octave (well, one octave and the very begining of the next).
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
        
    a = 0
    start_time = time.perf_counter()
    # with mido.open_input('Roland Digital Piano:Roland Digital Piano MIDI 1 36:0') as inport:
    with mido.open_input('Elektron Syntakt:Elektron Syntakt MIDI 1 32:0') as inport:

        Buffer = []

        while True:
            Waiting_cc_messages = []
            Waiting_white_note_messages = []
            Waiting_black_note_messages = []
            Waiting_clock_messages = []
                      
            ### Make an initial sort of all messages in the buffer into different categories.      
            for msg in Buffer:
                if(msg.type == 'clock'):
                    Waiting_clock_messages.append(msg)
                if(msg.type == 'control_change'):
                    Waiting_cc_messages.append(msg)
                elif hasattr(msg, 'note'):
                    if(msg.note == 60 or msg.note == 62 or msg.note == 64 or msg.note == 65 or msg.note == 67 or msg.note == 69 or msg.note == 71):
                        Waiting_white_note_messages.append(msg)
                    elif(msg.note == 61 or msg.note == 63 or msg.note == 66 or msg.note == 68 or msg.note == 70):
                        Waiting_black_note_messages.append(msg)

            ### Handle all waiting cc messages.
            for msg in Waiting_cc_messages:
                if(msg.control == 70):
                    CC1 = msg.value
                elif(msg.control == 71):
                    CC2 = msg.value
                elif(msg.control == 72):
                    CC3 = msg.value
                elif(msg.control == 73):
                    CC4 = msg.value
                elif(msg.control == 74):
                    CC5 = msg.value
                elif(msg.control == 75):
                    CC6 = msg.value
                elif(msg.control == 76):
                    CC7 = msg.value
                elif(msg.control == 77):
                    CC8 = msg.value

            ### Handle all waiting black note messages.
            for msg in Waiting_black_note_messages:
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

            ### Handle all waiting white note messages.
            for msg in Waiting_white_note_messages:
                ### Program (white keys).
                
                ### ### Program 1: Whole field with ADSR, Sustain level, and HSV settings from CC.
                ### ### ### CC1: Hue
                ### ### ### CC2: Saturation
                ### ### ### CC3: After attack brightness
                ### ### ### CC4: After decay brightness
                ### ### ### CC5: Attack time
                ### ### ### CC6: Decay time
                ### ### ### CC7: Release time
                ### ### ### CC8: Ignore note off messages (Less than 63 means "No"; more than 63 means "Yes"). Just run a full ADR cycle no matter if there are note off messages.
                if(msg.note == 60): # Only respond to C4.
                    if(msg.type == 'note_on' and msg.velocity > 0):
                        for Count in range(Number_of_lights):
                            if(Layer2.Main_program == 1):
                                
                                if(Layer2.Sub_program == 1):
                                    for Count in range(len(Layer1.Array_of_Layer1_objects)):
                                        Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                                        )
                                        
                                elif(Layer2.Sub_program == 2):
                                    for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                        Layer1.Array_of_Layer1_objects[int(Count + len(Layer1.Array_of_Layer1_objects)/2)] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                                        )
                                        
                                elif(Layer2.Sub_program == 3):
                                    for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                        Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                                        )
                                
                                elif(Layer2.Sub_program == 4):
                                    for Count in range(int(len(Layer1.Array_of_Layer1_objects)/4)):
                                        Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                                        )
                                        Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*3] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                                        )
                                
                                elif(Layer2.Sub_program == 5):
                                    for Count in range(int(len(Layer1.Array_of_Layer1_objects)/4)):
                                        Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*1] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                                        )
                                        Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*2] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2, Ignore_go_to_release_phase=False), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0)),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO(Waveform="Sine", Amplitude=0, Repeat=True, Rate=0, Phase=0))
                                        )
                    
                                
                    if(msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)): # On Syntakt, note off is sent by sending note on with a velocity of 0.
                        if(Layer2.Main_program == 1):
                            
                            if(Layer2.Sub_program == 1):
                                for Count in range(len(Layer1.Array_of_Layer1_objects)):
                                    Layer1.Array_of_Layer1_objects[Count].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Brightness.ADSR.Go_to_release_phase = True
                                    
                            if(Layer2.Sub_program == 2):
                                for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                    Layer1.Array_of_Layer1_objects[int(Count + len(Layer1.Array_of_Layer1_objects)/2)].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[int(Count + len(Layer1.Array_of_Layer1_objects)/2)].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[int(Count + len(Layer1.Array_of_Layer1_objects)/2)].Brightness.ADSR.Go_to_release_phase = True
                                    
                            if(Layer2.Sub_program == 3):
                                for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                    Layer1.Array_of_Layer1_objects[Count].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Brightness.ADSR.Go_to_release_phase = True
                              
                            if(Layer2.Sub_program == 4):
                                for Count in range(int(len(Layer1.Array_of_Layer1_objects)/4)):
                                    Layer1.Array_of_Layer1_objects[Count].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Brightness.ADSR.Go_to_release_phase = True         
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*3].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*3].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*3].Brightness.ADSR.Go_to_release_phase = True

                                
                            if(Layer2.Sub_program == 5):
                                for Count in range(int(len(Layer1.Array_of_Layer1_objects)/4)):
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*1].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*1].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*1].Brightness.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*2].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*2].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*2].Brightness.ADSR.Go_to_release_phase = True
                                        
                ### ### Program 2: Random start of random lights.
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
                                Layer1.Array_of_Layer1_objects[Count].Hue.ADSR.Go_to_release_phase = True
                                Layer1.Array_of_Layer1_objects[Count].Saturation.ADSR.Go_to_release_phase = True
                                Layer1.Array_of_Layer1_objects[Count].Brightness.ADSR.Go_to_release_phase = True
            
            ### Clear the buffer
            Buffer = []
                
            ### Stay in this loop until the total amount of clock messages have passed the thresshold for moving on.
            while True:
                for msg in inport.iter_pending():
                    if(msg.type == 'clock'):
                        Waiting_clock_messages.append(msg)
                    else:
                        Buffer.append(msg)
                if(len(Waiting_clock_messages) >= Clock_ticks_per_cycle):
                    print(len(Waiting_clock_messages))
                    break
                    
            # Basis for what eventually will be turned into a mediator between Layer1 and Layer0.
            Layer1.Update()
            for Light_number in range(len(Layer0.Array_of_lights)):
                Layer0.Set_color(Light_number, Hue=(Layer1.Array_of_Layer1_objects[Light_number].Hue.Current_value % 1), Saturation=Layer1.Array_of_Layer1_objects[Light_number].Saturation.Current_value, Brightness=Layer1.Array_of_Layer1_objects[Light_number].Brightness.Current_value)
            Layer0.Let_there_be_light()
