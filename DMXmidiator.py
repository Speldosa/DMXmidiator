#######################
### Import packages ###
#######################
from dmx import Colour, DMXInterface, DMXLight3Slot, DMXUniverse
import mido
import math
import colorsys
### Used for debugging.
# import time # Then sse time.perf_counter() to get the current time.

########################
### Global variables ###
########################
Number_of_lights = 32
Clock_ticks_per_cycle = 2

Max_brightness = 128 #In DMX value. So the minumum is 0 and the maximum is 255.
Max_Attack_cycles = 128
Max_Decay_cycles = 128
Max_Sustain_cycles = 128
Max_Release_cycles = 128
Max_LFO_cycles = 128

Main_program_0_note = 60
Main_program_1_note = 62
Main_program_2_note = 64
Main_program_3_note = 65
Main_program_4_note = 67
Main_program_5_note = 69
Main_program_6_note = 71
Main_program_7_note = 72
Main_program_notes = [Main_program_0_note, Main_program_1_note, Main_program_2_note, Main_program_3_note, Main_program_4_note, Main_program_5_note, Main_program_6_note, Main_program_7_note]

Sub_program_0_note = 61
Sub_program_1_note = 63
Sub_program_2_note = 66
Sub_program_3_note = 68
Sub_program_4_note = 70
Sub_program_notes = [Sub_program_0_note, Sub_program_1_note, Sub_program_2_note, Sub_program_3_note, Sub_program_4_note]

Parameter_0_cc = 70
Parameter_1_cc = 71
Parameter_2_cc = 72
Parameter_3_cc = 73
Parameter_4_cc = 74
Parameter_5_cc = 75
Parameter_6_cc = 76
Parameter_7_cc = 77
Parameters_cc = [Parameter_0_cc, Parameter_1_cc, Parameter_2_cc, Parameter_3_cc, Parameter_4_cc, Parameter_5_cc, Parameter_6_cc, Parameter_7_cc] 

############################
### Function definitions ###
############################
def hsv_to_dmx_rgb(Hue, Saturation, Value, Max_brightness):
    Tmp = colorsys.hsv_to_rgb(Hue, Saturation, Value)
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
    def __init__(Self, After_attack_amplitude, After_decay_amplitude, Attack, Decay, Sustain, Release, Ignore_go_to_release_phase = False):
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
        Self.Program = [[Main_program, Sub_program], "Same"] # Main_program can take on values between 1-8. This could be extended, but with 8 different programs, they can all be accessed via the white keys on piano keyboard within the same octave (well, one octave and the very begining of the next). Sub_program can take on values between 1-5. This could be extended, but with 5 different sub programs, they can all be accessed via the black keys on piano keyboard within the same octave.
        Self.Parameters = [[Parameter1, "Same"], [Parameter2, "Same"], [Parameter3, "Same"], [Parameter4, "Same"], [Parameter5, "Same"], [Parameter6, "Same"], [Parameter7, "Same"], [Parameter8, "Same"]]

#######################
### Useful commands ###
#######################
# print(mido.get_input_names()) # Get a list of all available input ports.

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
        Program = [[None, None], [None, None]] # First row represents current program. Second row represents previous program.
        Parameters = [[64, None], [64, None], [64, None], [64, None], [64, None], [64, None], [64, None], [64, None]]
    )
         
    with mido.open_input('Roland Digital Piano:Roland Digital Piano MIDI 1 36:0') as inport:
    # with mido.open_input('Elektron Syntakt:Elektron Syntakt MIDI 1 32:0') as inport:

        Buffer = []

        while True:
            Waiting_clock_messages = []

            for msg in Buffer:
                if(msg.type == 'clock'): # If the message is a clock event...
                    Waiting_clock_messages.append(msg) # Append it to the array of waiting clock messages.
                
                elif(msg.type == 'control_change'): # If the message is a cc message...
                     if(msg.control in Parameters_cc): # If the cc message is part of the parameters cc...
                        Layer2.Parameters[Parameters_cc.index(msg.control)][1] = Layer2.Parameters[Parameters_cc.index(msg.control)][0] # Move the current cc value for that parameter to the previous cc value for that parameter.
                        Layer2.Parameters[Parameters_cc.index(msg.control)][0] = msg.value # Set the current cc value to the current cc value for that parameter.
                
                elif hasattr(msg, 'note'): # If the message is a note event...
                    if(msg.type == 'note_on' and msg.velocity > 0): # If the note is a note on event...
                        if(msg.note in Main_program_notes): # If the note is part of the main program notes...
                            Layer2.Program[1] = Layer2.Program[0] # Copy current program to previous program.
                            Layer2.Program[0][0] = Main_program_notes.index(msg.note) # Set main program part of current program.
                        elif(msg.note in Sub_program_notes): # Else, if the note is part of the sub program notes...
                            Layer2.Program[1] = Layer2.Program[0] # Copy current program to previous program.
                            Layer2.Program[0][1] = Sub_program_notes.index(msg.note) # Set sub program part of current program.
                    else: # If the note is a note off event...
                        if(msg.note in Main_program_notes): # If the note is part of the main program notes...
                            if(Layer2.Program[0][0] == Main_program_notes.index(msg.note)): # If the note is a note off command for a main program that's already in the current program...
                                Layer2.Program[1] = Layer2.Program[0] # Move current program to previous program.
                                Layer2.Program[0][0] = None # Set main program part of the current program to none.
                        elif(msg.note in Sub_program_notes): # Else, if the note is part of the sub program notes...
                            if(Layer2.Program[0][1] == Sub_program_notes.index(msg.note)): # If the note is a note off command for a sub program that's already in the current program...
                                Layer2.Program[1] = Layer2.Program[0] # Move current program to previous program.
                                Layer2.Program[0][1] = None # Set sub program part of the current program to none.












                     




            ### Make an initial sort of all messages in the buffer into different categories.      
            for msg in Buffer:
                if(msg.type == 'clock'):
                    Waiting_clock_messages.append(msg)
                if(msg.type == 'control_change'):
                    Waiting_cc_messages.append(msg)
                elif hasattr(msg, 'note'):
                    if(msg.note == 60 or msg.note == 62 or msg.note == 64 or msg.note == 65 or msg.note == 67 or msg.note == 69 or msg.note == 71):
                        if(msg.type == 'note_on' and msg.velocity > 0):
                            Waiting_white_note_on_messages.append(msg)
                        else:
                            Waiting_white_note_off_messages.append(msg)
                    elif(msg.note == 61 or msg.note == 63 or msg.note == 66 or msg.note == 68 or msg.note == 70):
                        if(msg.type == 'note_on' and msg.velocity > 0):
                            Waiting_black_note_on_messages.append(msg)
                        else:
                            Waiting_black_note_off_messages.append(msg)

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

            ### Handle all waiting black note on messages.
            for msg in Waiting_black_note_on_messages:
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
            
            ### Handle all waiting white note off messages.
#             for msg in Waiting_white_note_off_messages:
#                 if(msg.note == 60):
#                     Layer2.Quit_main_program.append(1)
#                 elif(msg.note == 62):
#                     Layer2.Quit_main_program.append(2)
#                 elif(msg.note == 64):
#                     Layer2.Quit_main_program.append(3)
#                 elif(msg.note == 65):
#                     Layer2.Quit_main_program.append(4)
#                 elif(msg.note == 67):
#                     Layer2.Quit_main_program.append(5)
#                 elif(msg.note == 69):
#                     Layer2.Quit_main_program.append(6)
#                 elif(msg.note == 71):
#                     Layer2.Quit_main_program.append(7)
#                 elif(msg.note == 72):
#                     Layer2.Quit_main_program.append(8)

            ### Handle all waiting white note on messages.
            for msg in Waiting_white_note_on_messages:
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
                    for Count in range(Number_of_lights):                            
                        if(Layer2.Sub_program == 1):
                            for Count in range(len(Layer1.Array_of_Layer1_objects)):
                                Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                    Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO())
                                )
                                
                        elif(Layer2.Sub_program == 2):
                            for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                Layer1.Array_of_Layer1_objects[int(Count + len(Layer1.Array_of_Layer1_objects)/2)] = Layer1_light_object(
                                    Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO())
                                )
                                
                        elif(Layer2.Sub_program == 3):
                            for Count in range(int(len(Layer1.Array_of_Layer1_objects)/2)):
                                Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                    Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO())
                                )
                        
                        elif(Layer2.Sub_program == 4):
                            for Count in range(int(len(Layer1.Array_of_Layer1_objects)/4)):
                                Layer1.Array_of_Layer1_objects[Count] = Layer1_light_object(
                                    Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO())
                                )
                                Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*3] = Layer1_light_object(
                                    Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO())
                                )
                        
                        elif(Layer2.Sub_program == 5):
                            for Count in range(int(len(Layer1.Array_of_Layer1_objects)/4)):
                                Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*1] = Layer1_light_object(
                                    Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO())
                                )
                                Layer1.Array_of_Layer1_objects[Count+int(len(Layer1.Array_of_Layer1_objects)/4)*2] = Layer1_light_object(
                                    Hue = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC1), After_decay_amplitude=CC_to_ratio(CC1), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Saturation = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC2), After_decay_amplitude=CC_to_ratio(CC2), Attack=0, Decay=0, Sustain=2, Release=2), LFO()),
                                    Brightness = Signal(ADSR(After_attack_amplitude=CC_to_ratio(CC3), After_decay_amplitude=CC_to_ratio(CC4), Attack=CC_to_ratio(CC5), Decay=CC_to_ratio(CC6), Sustain=2.0, Release=CC_to_ratio(CC7), Ignore_go_to_release_phase=CC_to_boolean(CC8)), LFO())
                                )
                    
                ### ### Program 2: Sweep.
                if(msg.note == 62):
                    pass

                                
            ### Handle all waiting white note off messages.
            for msg in Waiting_white_note_off_messages:                           
                  if(msg.note == 60): # Only respond to C4. 
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
                                    

            ### Clear the buffer
            Buffer = []

            # Basis for what eventually will be turned into a mediator between Layer1 and Layer0.
            Layer1.Update()
            for Light_number in range(len(Layer0.Array_of_lights)):
                Layer0.Set_color(Light_number, Hue=(Layer1.Array_of_Layer1_objects[Light_number].Hue.Current_value % 1), Saturation=Layer1.Array_of_Layer1_objects[Light_number].Saturation.Current_value, Brightness=Layer1.Array_of_Layer1_objects[Light_number].Brightness.Current_value)
            Layer0.Let_there_be_light()

            ### Stay in this loop until the total amount of clock messages have passed the thresshold for moving on.
            while True:
                for msg in inport.iter_pending():
                    if(msg.type == 'clock'):
                        Waiting_clock_messages.append(msg)
                    else:
                        Buffer.append(msg)
                if(len(Waiting_clock_messages) >= Clock_ticks_per_cycle):
                    break
                    

