#######################
### Import packages ###
#######################
from dmx import Colour, DMXInterface, DMXLight3Slot, DMXUniverse
from math import sin, pi
from colorsys import hsv_to_rgb
import mido

# import time # Used for debugging. Use function time.perf_counter() to get the current time.

#################################################
### Global variables that can be manually set ###
#################################################
Number_of_lights = 32 # How many individually controllable lights you want to control. Right now, you should also change the number of channels in the dmx/constants.py file. Failure to do so can slow down the program since uncesscary commands then are being sent out.
Midi_device = 'Elektron Syntakt:Elektron Syntakt MIDI 1' # Change this variable to whatever device you want to control the program. In order to get a list of all available devices, you can run: print(mido.get_input_names()). Also, notice that you don't have to include the "x:y" part at the end of the device name. In fact, it's probably better to leave this part out since it can (and probably will) change between reboots of the computer.
Respond_to_midi_channels = [15] # List which midi channels should be listened to for midi messages. Notice that counting starts at zero, meaning that what most devices call midi channel 1 will be represented by 0 in this array.
Clock_ticks_per_cycle = 2 # How many ticks (one quarter note consists of 24 ticks) one cycle of the program should consist off. Lower values means lower latency, but if the value is set to low, cycles might become uneven in length.

Max_brightness = 128 # In DMX value. So the minumum is 0 and the maximum is 255.
Max_Attack_cycles = 128 # If multiplied with Clock_ticks_per_cycle above, this results in the maximum number of ticks the attack phase can be.
Max_Decay_cycles = 128 # If multiplied with Clock_ticks_per_cycle above, this results in the maximum number of ticks the decay phase can be.
Max_Sustain_cycles = 128 # If multiplied with Clock_ticks_per_cycle above, this results in the maximum number of ticks the sustain phase can be.
Max_Release_cycles = 128 # If multiplied with Clock_ticks_per_cycle above, this results in the maximum number of ticks the release phase can be.
Max_LFO_cycles = 128 # If multiplied with Clock_ticks_per_cycle above, this results in the maximum number of ticks a complete LFO phase can be.

Main_program_0_note = 60
Main_program_1_note = 62
Main_program_2_note = 64
Main_program_3_note = 65
Main_program_4_note = 67
Main_program_5_note = 69
Main_program_6_note = 71
Main_program_7_note = 72

Sub_program_0_note = 61
Sub_program_1_note = 63
Sub_program_2_note = 66
Sub_program_3_note = 68
Sub_program_4_note = 70

Parameter_0_cc = 70
Parameter_1_cc = 71
Parameter_2_cc = 72
Parameter_3_cc = 73
Parameter_4_cc = 74
Parameter_5_cc = 75
Parameter_6_cc = 76
Parameter_7_cc = 77

##################################################################################################################################
### Global variables that are automatically computed based on the manually set global variables above (that is, do not touch!) ###
##################################################################################################################################

Main_program_notes = [Main_program_0_note, Main_program_1_note, Main_program_2_note, Main_program_3_note, Main_program_4_note, Main_program_5_note, Main_program_6_note, Main_program_7_note]
Sub_program_notes = [Sub_program_0_note, Sub_program_1_note, Sub_program_2_note, Sub_program_3_note, Sub_program_4_note]
Parameters_cc = [Parameter_0_cc, Parameter_1_cc, Parameter_2_cc, Parameter_3_cc, Parameter_4_cc, Parameter_5_cc, Parameter_6_cc, Parameter_7_cc] 

############################
### Function definitions ###
############################
def hsv_to_dmx_rgb(Hue, Saturation, Value, Max_brightness):
    Tmp = hsv_to_rgb(Hue, Saturation, Value)
    return(Colour(round(Tmp[0]*Max_brightness), round(Tmp[1]*Max_brightness), round(Tmp[2]*Max_brightness)))

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
        Self.Array_of_lights[Light_number].set_colour(hsv_to_dmx_rgb(Hue, Saturation, Brightness, Max_brightness))
    
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
    def __init__(Self, After_attack_amplitude = 1, After_decay_amplitude = 1, Attack = 0, Decay = 0, Sustain = 2.0, Release = 0, Ignore_go_to_release_phase = False):
        Self.After_attack_amplitude = After_attack_amplitude
        Self.After_decay_amplitude = After_decay_amplitude
        Self.Attack = Attack
        Self.Decay = Decay
        Self.Sustain = Sustain
        Self.Release = Release
        Self.Progress = 0.0
        Self.Current_value = 0.0
        Self.Go_to_release_phase = False # A boolean stating whether the release phase is forced or not (usually because of note off commands). Will mainly be maniupulated later (that is, not during the initialization of the class).
        Self.Ignore_go_to_release_phase = Ignore_go_to_release_phase # If true, a setting of Self.Go_to_release_phase to True will be ignored. 
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
    def __init__(Self, Waveform = "Sine", Amplitude = 0, Repeat = True, Rate = 0, Phase = 0):
        Self.Waveform = Waveform
        Self.Amplitude = Amplitude
        Self.Repeat = Repeat
        Self.Rate = Rate
        Self.Phase = Phase
        Self.Progress = 0.0
        Self.Current_value = 1.0 # Can range between 0 and 2.

    def Update(Self):
        if(round(Self.Progress, 2) >= 1):
            if(Self.Repeat):
                Self.Progress = 0
        if(not Self.Repeat and (round(Self.Progress, 2) >= 1)):
            Self.Current_value = sin(pi * 2 * ((0 + (1 * Self.Phase)) % 1)) * Self.Amplitude + 1
        else:
            Self.Current_value = sin(pi * 2 * ((Self.Progress + (1 * Self.Phase)) % 1)) * Self.Amplitude + 1
            if(Max_LFO_cycles < 4): # Fastest possible number of cycles for the LFO is 4.
                Max_LFO_cycles_updated = 4
            else:
                Max_LFO_cycles_updated = Max_LFO_cycles
            LFO_cycles = 4 + round((Max_LFO_cycles_updated - 4) * (1 - Self.Rate))
            Self.Progress = Self.Progress + 1/LFO_cycles

class Layer2:
    def __init__(Self, Number_of_lights, Main_program, Sub_program, Parameter0, Parameter1, Parameter2, Parameter3, Parameter4, Parameter5, Parameter6, Parameter7):
        Self.Number_of_lights = Number_of_lights
        Self.Program = [[Main_program, Sub_program], [None, None], [None, None]] # First row represents the program that should be implemented. Second row represents the program that it currently running. Third row represents the program that should be closed down. Main_program can take on values between 1-8. This could be extended, but with 8 different programs, they can all be accessed via the white keys on piano keyboard within the same octave (well, one octave and the very begining of the next). Sub_program can take on values between 1-5. This could be extended, but with 5 different sub programs, they can all be accessed via the black keys on piano keyboard within the same octave.
        Self.Parameters = [[Parameter0, None], [Parameter1, None], [Parameter2, None], [Parameter3, None], [Parameter4, None], [Parameter5, None], [Parameter6, None], [Parameter7, None]] # First row represents the new parameter value. If the second row has a value, that means that that previos value might still be implemented on a lower level (and in that case should be replaced).

####################
### Main program ###
####################
### Open an interface
with DMXInterface("FT232R") as interface:

    Layer0 = Layer0(Number_of_lights = Number_of_lights) # Initialize a Layer0.
    Layer1 = Layer1(Number_of_lights = Number_of_lights) # Initialize a Layer1.
    Layer2 = Layer2(Number_of_lights = Number_of_lights, Main_program = None, Sub_program = None, Parameter0 = 64, Parameter1 = 64, Parameter2 = 64, Parameter3 = 64, Parameter4 = 64, Parameter5 = 64, Parameter6 = 64, Parameter7 = 64) # Initialize a Layer2.
         
    with mido.open_input(Midi_device) as inport:

        Buffer = []

        while True:
            Waiting_clock_messages = [] # Effectively clear the Waiting_clock_messages memory and start over.

            ### Go through each midi message in the buffer and for everytime there is something else than a clock message, first update Layer2 and then update Layer1 based on the content of Layer2.
            for msg in Buffer:

                ### ### If the midi message is just a clock message, record it.
                if(msg.type == 'clock'): # If the message is a clock event...
                    Waiting_clock_messages.append(msg) # Append it to the array of waiting clock messages.

                ### ### However, if the midi message coming in is something more interesting (CC message or note message), update Layer2 based on this information.
                elif (((msg.type == 'control_change') or hasattr(msg, 'note')) and (msg.channel in Respond_to_midi_channels)):
                    if(msg.type == 'control_change'): # If the message is a cc message...
                        if(msg.control in Parameters_cc): # If the cc message is part of the parameters cc...
                            Layer2.Parameters[Parameters_cc.index(msg.control)][1] = Layer2.Parameters[Parameters_cc.index(msg.control)][0] # Move the current cc value for that parameter to the previous cc value for that parameter.
                            Layer2.Parameters[Parameters_cc.index(msg.control)][0] = msg.value # Set the current cc value to the current cc value for that parameter.
                    
                    elif hasattr(msg, 'note'): # If the message is a note event...
                        if(msg.type == 'note_on' and msg.velocity > 0): # If the note is a note on event...
                            if(msg.note in Main_program_notes): # If the note is part of the main program notes...
                                Layer2.Program[2] = Layer2.Program[1] # Copy program currently running to program that should be closed down.
                                Layer2.Program[0][0] = Main_program_notes.index(msg.note) # Set main program part of program that should be implemented.
                            elif(msg.note in Sub_program_notes): # Else, if the note is part of the sub program notes...
                                Layer2.Program[2] = Layer2.Program[1] # Copy program currently running to program that should be closed down.
                                Layer2.Program[0][1] = Sub_program_notes.index(msg.note) # Set sub program part of program that should be implemented.
                        else: # If the note is a note off event...
                            if(msg.note in Main_program_notes): # If the note is part of the main program notes...
                                if(Layer2.Program[0][0] == Main_program_notes.index(msg.note)): # If the note is a note off command for a main program that's already in the program to be initialized...
                                    Layer2.Program[0][0] = None #...set it to none.
                                if(Layer2.Program[1][0] == Main_program_notes.index(msg.note)): # If the note is a note off command for a main program that's already in the current program...
                                    Layer2.Program[2] = Layer2.Program[1] # Copy program currently running to program that should be closed down...
                                    Layer2.Program[1] = [None, None] # ..and set the program currently running to none.
                                    Layer2.Program[0][0] = None # Set main program part of program that should be implemented to none.
                            elif(msg.note in Sub_program_notes): # Else, if the note is part of the sub program notes...
                                if(Layer2.Program[0][1] == Sub_program_notes.index(msg.note)): # If the note is a note off command for a sub program that's already in the program to be initialized...
                                    Layer2.Program[0][1] = None #...set it to none.
                                if(Layer2.Program[1][1] == Sub_program_notes.index(msg.note)): # If the note is a note off command for a sub program that's already in the current program...
                                    Layer2.Program[2] = Layer2.Program[1] # Copy program currently running to program that should be closed down...
                                    Layer2.Program[1] = [None, None] # ...and set the program currently running to none.
                                    Layer2.Program[0][1] = None # Set sub program part of program that should be implemented to none.
                    
                    ### ### ### Then update Layer1 based on the content of Layer2. Note that only one operation will be necessary per loop. That is, if a program is to be closed down, there won't be any program to initialize and vice versa.
                    ### ### ### ### Initialize program
                    if((Layer2.Program[0][0] is not None) and (Layer2.Program[0][1] is not None)): # If there is a complete program waiting in the program to be initialized (i.e., if it contains a valid main program and a valid sub program)...
                        if(Layer2.Program[0] != Layer2.Program[1]): # ...and if the program to be implemented isn't the same as what's currently running (in that case, it has already been initialized).
                            
                            if(Layer2.Program[0][0] == 0): # Main program 0.
                                
                                if(Layer2.Program[0][1] == 0): # Sub program 0. All lights on.
                                    for Count in range(len(Layer1.Array_of_Layer1_objects)):
                                        Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[2][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[3][0]), Attack=CC_to_ratio(Layer2.Parameters[4][0]), Decay=CC_to_ratio(Layer2.Parameters[5][0]), Sustain=2.0, Release=CC_to_ratio(Layer2.Parameters[6][0]), Ignore_go_to_release_phase=CC_to_boolean(Layer2.Parameters[7][0])), LFO())
                                        )
                                    
                                elif(Layer2.Program[0][1] == 1): # Sub program 1. Left half of the lights on.
                                    for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                        Layer1.Array_of_Layer1_objects[int(Count + len(Layer1.Array_of_Layer1_objects)/2)] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[2][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[3][0]), Attack=CC_to_ratio(Layer2.Parameters[4][0]), Decay=CC_to_ratio(Layer2.Parameters[5][0]), Sustain=2.0, Release=CC_to_ratio(Layer2.Parameters[6][0]), Ignore_go_to_release_phase=CC_to_boolean(Layer2.Parameters[7][0])), LFO())
                                        )
                                
                                elif(Layer2.Program[0][1] == 2): # Sub program 2. Right half of the lights on.
                                    for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                        Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[2][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[3][0]), Attack=CC_to_ratio(Layer2.Parameters[4][0]), Decay=CC_to_ratio(Layer2.Parameters[5][0]), Sustain=2.0, Release=CC_to_ratio(Layer2.Parameters[6][0]), Ignore_go_to_release_phase=CC_to_boolean(Layer2.Parameters[7][0])), LFO())
                                        )
                                
                                elif(Layer2.Program[0][1] == 3): # Sub program 3. Left and right fourths of the lights on.
                                    for Count in range(int(len(Layer1.Array_of_Layer1_objects)/4)):
                                        Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[2][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[3][0]), Attack=CC_to_ratio(Layer2.Parameters[4][0]), Decay=CC_to_ratio(Layer2.Parameters[5][0]), Sustain=2.0, Release=CC_to_ratio(Layer2.Parameters[6][0]), Ignore_go_to_release_phase=CC_to_boolean(Layer2.Parameters[7][0])), LFO())
                                        )
                                        Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*3] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[2][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[3][0]), Attack=CC_to_ratio(Layer2.Parameters[4][0]), Decay=CC_to_ratio(Layer2.Parameters[5][0]), Sustain=2.0, Release=CC_to_ratio(Layer2.Parameters[6][0]), Ignore_go_to_release_phase=CC_to_boolean(Layer2.Parameters[7][0])), LFO())
                                        )
                                
                                elif(Layer2.Program[0][1] == 4): # Sub program 4. Middle fourths of the lights on.
                                    for Count in range(int(len(Layer1.Array_of_Layer1_objects)/4)):
                                        Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*1] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[2][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[3][0]), Attack=CC_to_ratio(Layer2.Parameters[4][0]), Decay=CC_to_ratio(Layer2.Parameters[5][0]), Sustain=2.0, Release=CC_to_ratio(Layer2.Parameters[6][0]), Ignore_go_to_release_phase=CC_to_boolean(Layer2.Parameters[7][0])), LFO())
                                        )
                                        Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*2] = Layer1_light_object(
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[1][0]), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                            Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[2][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[3][0]), Attack=CC_to_ratio(Layer2.Parameters[4][0]), Decay=CC_to_ratio(Layer2.Parameters[5][0]), Sustain=2.0, Release=CC_to_ratio(Layer2.Parameters[6][0]), Ignore_go_to_release_phase=CC_to_boolean(Layer2.Parameters[7][0])), LFO())
                                        )

                            if(Layer2.Program[0][0] == 1): # Main program 1.
                                
                                if(Layer2.Program[0][1] == 0): # Sub program 0.
                                    for Count in range(len(Layer1.Array_of_Layer1_objects)):
                                        Tmp = Count/(len(Layer1.Array_of_Layer1_objects) - 1)
                                        Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                            # Hue = Signal(ADSR(After_attack_amplitude=1, After_decay_amplitude=1, Attack=Tmp, Decay=0, Sustain=2, Release=0), LFO()),
                                            # Saturation = Signal(ADSR(After_attack_amplitude=0, After_decay_amplitude=1, Attack=Tmp, Decay=0, Sustain=1, Release=0), LFO()),
                                            # Brightness = Signal(ADSR(After_attack_amplitude=0, After_decay_amplitude=0.5, Attack=Tmp, Decay=0, Sustain=1, Release=0), LFO(Waveform = "Sine", Amplitude = 1, Repeat = True, Rate = 0, Phase = -0.25 - Tmp))
                                            Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), After_decay_amplitude=CC_to_ratio(Layer2.Parameters[0][0]), Attack=0, Decay=0, Sustain=1, Release=0), LFO()),
                                            Saturation = Signal(ADSR(After_attack_amplitude=0, After_decay_amplitude=1, Attack=0, Decay=0, Sustain=1, Release=0), LFO()),
                                            Brightness = Signal(ADSR(After_attack_amplitude=0, After_decay_amplitude=0.5, Attack=Tmp * (1-CC_to_ratio(Layer2.Parameters[3][0])), Decay=0, Sustain=1, Release=0), LFO(Waveform = "Sine", Amplitude = 1, Repeat = True, Rate = CC_to_ratio(Layer2.Parameters[3][0]), Phase = -0.25 - Tmp))
                                            # CC_to_ratio(Layer2.Parameters[3][0])
                                        )

                            Layer2.Program[1] = Layer2.Program[0] # Finally, copy the program to be implemented to program that is currently running...
                            Layer2.Program[0] = [None, None] # ...and remove the program to be implemented.
                            
                    ### ### ### ### Close down program
                    elif((Layer2.Program[2][0] is not None) and (Layer2.Program[2][1] is not None)): # If there is a complete program waiting in the program to be closed down (i.e., if it contains a valid main program and a valid sub program)...
                        
                        if(Layer2.Program[2][0] == 0): # Main program 0.

                            if(Layer2.Program[2][1] == 0): # Sub program 0. All lights on.
                                for Count in range(len(Layer1.Array_of_Layer1_objects)):
                                    Layer1.Array_of_Layer1_objects[Count].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Brightness.ADSR.Go_to_release_phase = True    
            
                            elif(Layer2.Program[2][1] == 1): # Sub program 1. Left half of the lights on.
                                for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                    Layer1.Array_of_Layer1_objects[int(Count + len(Layer1.Array_of_Layer1_objects)/2)].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[int(Count + len(Layer1.Array_of_Layer1_objects)/2)].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[int(Count + len(Layer1.Array_of_Layer1_objects)/2)].Brightness.ADSR.Go_to_release_phase = True

                            elif(Layer2.Program[2][1] == 2): # Sub program 2. Right half of the lights on.
                                for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                    Layer1.Array_of_Layer1_objects[Count].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Brightness.ADSR.Go_to_release_phase = True

                            elif(Layer2.Program[2][1] == 3): # Sub program 3. Left and right fourths of the lights on.
                                for Count in range(int(len(Layer1.Array_of_Layer1_objects)/4)):
                                    Layer1.Array_of_Layer1_objects[Count].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count].Brightness.ADSR.Go_to_release_phase = True         
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*3].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*3].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*3].Brightness.ADSR.Go_to_release_phase = True

                            elif(Layer2.Program[2][1] == 4): # Sub program 4. Middle fourths of the lights on.
                                for Count in range(int(len(Layer1.Array_of_Layer1_objects)/4)):
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*1].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*1].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*1].Brightness.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*2].Hue.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*2].Saturation.ADSR.Go_to_release_phase = True
                                    Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*2].Brightness.ADSR.Go_to_release_phase = True
                        
                        if(Layer2.Program[2][0] == 1): # Main program 1.
                            if(Layer2.Program[2][1] == 0): # Sub program 0. All lights on.
                                pass

                        Layer2.Program[2] = [None, None] # Finally, set the program to be removed to none.
                        
            ### When all messages in the buffer have been handeled... 
            ### ...update Layer1...
            Layer1.Update() 
            ####  ...update Layer0 based on the content of Layer1...
            for Light_number in range(len(Layer0.Array_of_lights)):
                Layer0.Set_color(Light_number, Hue=(Layer1.Array_of_Layer1_objects[Light_number].Hue.Current_value % 1), Saturation=max(min(Layer1.Array_of_Layer1_objects[Light_number].Saturation.Current_value,1),0), Brightness=max(min(Layer1.Array_of_Layer1_objects[Light_number].Brightness.Current_value,1),0))
            ### ...and finllay light up the lights based on the content of Layer0.
            Layer0.Let_there_be_light()

            ### Then clear the buffer...
            Buffer = []
        
            ### ...and fill up the new buffer until the total amount of clock messages have passed the thresshold for starting from the top of this whole while loop again.
            while True:
                for msg in inport.iter_pending():
                    if(msg.type == 'clock'):
                        Waiting_clock_messages.append(msg)
                    else:
                        Buffer.append(msg)
                if(len(Waiting_clock_messages) >= Clock_ticks_per_cycle):
                    # print(len(Waiting_clock_messages)) # If you want to monitor if all cycles contains the same number of ticks, uncomment this line.
                    break
