from dmx import Colour, DMXInterface, DMXLight3Slot, DMXUniverse
from time import sleep
import mido
import time # Use time.perf_counter() to get the current time.

### Set some colors for easy access during development.
Purple = Colour(128, 0, 128)
Blue = Colour(0, 0, 128)
Green = Colour(0, 128, 0)
Black = Colour(0, 0, 0)

Number_of_lights = 16
Global_max_brightness = 127
Max_attack_cycles = 128
Max_decay_cycles = 128
Max_sustain_cycles = 128
Max_release_cycles = 128

### Useful commands
### ### print(mido.get_input_names()) # Get a list of all available input ports.

############################
### Function definitions ###
############################
ONE_THIRD = 1.0/3.0
TWO_THIRD = 2.0/3.0
ONE_SIXTH = 1.0/6.0
    
def cpython_v(m1, m2, hue):
    hue = hue % 1.0
    if hue < ONE_SIXTH:
        return m1 + (m2-m1)*hue*6.0
    if hue < 0.5:
        return m2
    if hue < TWO_THIRD:
        return m1 + (m2-m1)*(TWO_THIRD-hue)*6.0
    return m1

def cpython_hls_to_rgb(h, l, s):
    if s == 0.0:
        return l, l, l
    if l <= 0.5:
        m2 = l * (1.0+s)
    else:
        m2 = l+s-(l*s)
    m1 = 2.0*l - m2
    return (cpython_v(m1, m2, h+ONE_THIRD), cpython_v(m1, m2, h), cpython_v(m1, m2, h-ONE_THIRD))

def hls_to_dmx_rgb(hue, brightness, saturation):
    Tmp = cpython_hls_to_rgb(hue, brightness, saturation)
    return(Colour(round(Tmp[0]*Global_max_brightness), round(Tmp[1]*Global_max_brightness), round(Tmp[2]*Global_max_brightness)))

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

def hsv_to_dmx_rgb(hue, saturation, value):
    Tmp = cpython_hsv_to_rgb(hue, saturation, value)
    return(Colour(round(Tmp[0]*Global_max_brightness), round(Tmp[1]*Global_max_brightness), round(Tmp[2]*Global_max_brightness)))

def CC_to_ratio(CC_input):
    return(CC_input/127)

############################################
### Necessary preparations/setup for DMX ###
############################################

### Open an interface
with DMXInterface("FT232R") as interface:
    
    ### Create a universe
    universe = DMXUniverse()

    ### Define a light
    Lights = []
    for i in range(Number_of_lights):
        Light = DMXLight3Slot(address=1+(3*i))
        Lights.append(Light)
        universe.add_light(Light)

    ### Update the interface's frame to be the universe's current state
    interface.set_frame(universe.serialise())

    ### Send an update to the DMX network
    interface.send_update()

    Layer0 = []
    for Count in range(Number_of_lights):
        Layer0.append(hls_to_dmx_rgb(0,0,0))
        
    class Layer1_object:
        def __init__(self, variant, hue, saturation, local_max_brightness, attack, decay, sustain, release):
            self.variant = variant
            self.hue = hue
            self.saturation = saturation
            self.local_max_brightness = local_max_brightness
            self.attack = attack
            self.decay = decay
            self.sustain = sustain
            self.release = release
            self.progress = 0
            self.transition_brightness = 1
            self.current_brightness = 0
    Layer1 = []
    for Count in range(Number_of_lights):
        Layer1.append(Layer1_object("ADSR", 0, 0, 0, 127, 127, 127, 127))

    with mido.open_input('Elektron Syntakt:Elektron Syntakt MIDI 1 40:0') as inport:
        
        CC1 = 0
        CC2 = 0
        CC3 = 127
        CC4 = 0
        CC5 = 16
        CC6 = 64
        CC7 = 32
        CC8 = 127
        
        # Counting = 0 # For debugging.
        
        while True:
            # Counting = Counting + 1 # For debugging.
            
            waiting_cc_messages = []
            waiting_note_messages = []
            for msg in inport.iter_pending():
                if(msg.type == 'control_change'):
                    print(msg)
                    waiting_cc_messages.append(msg)
                elif hasattr(msg, 'note'):
                    print(msg)
                    waiting_note_messages.append(msg)
            
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
                
            for msg in waiting_note_messages:
                if(msg.note == 60): # Only respond to C4.
                    if(msg.type == 'note_on' and msg.velocity > 0):
                        for Count in range(Number_of_lights):
                            Layer1[Count] = Layer1_object("ADSR", CC_to_ratio(CC1), CC_to_ratio(CC2), CC_to_ratio(CC3), CC_to_ratio(CC5), CC_to_ratio(CC6), CC_to_ratio(CC7), CC_to_ratio(CC8))
                    if(msg.type == 'note_on' and msg.velocity == 0):
                        for Count in range(Number_of_lights):
                            if(Layer1[Count].progress < 0.75):
                                Layer1[Count].progress = 0.75 # Go to the release phase.
                
            for Count in range(Number_of_lights):
                
                if(Layer1[Count].progress < 0.25): # Meaning we're in the attack phase.
                    # Local_max_brightness = round(Layer1[Count].local_max_brightness * Global_max_brightness) # Compute the local max brightness value in a DMX value.
                    Attack_cycles = round(Max_attack_cycles * Layer1[Count].attack)
                    if(Attack_cycles == 0):
                        Attack_cycles = 1
                    Layer1[Count].progress = Layer1[Count].progress + (0.25 / Attack_cycles)
                    Layer1[Count].current_brightness = (Layer1[Count].progress / 0.25) * Layer1[Count].local_max_brightness
                    Layer0[Count] = hsv_to_dmx_rgb(Layer1[Count].hue, Layer1[Count].saturation, Layer1[Count].current_brightness)
                    if(Layer1[Count].progress >= 0.25):
                        Layer1[Count].progress = 0.25
                    
                elif(Layer1[Count].progress < 0.50): # Meaning we're in the decay phase.
                    # Local_max_brightness = round(Layer1[Count].local_max_brightness * Global_max_brightness) # Compute the local max brightness value in a DMX value.
                    if(Layer1[Count].progress == 0.25):
                        Layer1[Count].transition_brightness = Layer1[Count].current_brightness # This should be equal to the local max brightness.
                    Decay_cycles = round(Max_decay_cycles * Layer1[Count].decay)
                    if(Decay_cycles == 0):
                        Decay_cycles = 1
                    Layer1[Count].progress = Layer1[Count].progress + (0.25 / Decay_cycles)
                    Layer1[Count].current_brightness = Layer1[Count].transition_brightness - (((Layer1[Count].progress - 0.25) / 0.25) * (Layer1[Count].local_max_brightness - (Layer1[Count].transition_brightness * Layer1[Count].sustain)))
                    if(Layer1[Count].current_brightness <= 0):
                        Layer1[Count].current_brightness = 0
                    Layer0[Count] = hsv_to_dmx_rgb(Layer1[Count].hue, Layer1[Count].saturation, Layer1[Count].current_brightness)
                    if(Layer1[Count].progress >= 0.50):
                        Layer1[Count].progress = 0.50
                        
                elif(Layer1[Count].progress < 0.75): # Meaning we're in the sustain phase.
                    pass
    
                elif(Layer1[Count].progress <= 1.0): # Meaning we're in the release phase.
                    # Local_max_brightness = round(Layer1[Count].local_max_brightness * Global_max_brightness) # Compute the local max brightness value in a DMX value.
                    if(Layer1[Count].progress == 0.75):
                        Layer1[Count].transition_brightness = Layer1[Count].current_brightness
                    Release_cycles = round(Max_release_cycles * Layer1[Count].release)
                    if(Release_cycles == 0):
                        Release_cycles = 1 
                    Layer1[Count].progress = Layer1[Count].progress + (0.25 / Release_cycles)
                    Layer1[Count].current_brightness = Layer1[Count].transition_brightness - (((Layer1[Count].progress - 0.75) / 0.25) * Layer1[Count].local_max_brightness)
                    if(Layer1[Count].current_brightness <= 0):
                        Layer1[Count].current_brightness = 0
                    Layer0[Count] = hsv_to_dmx_rgb(Layer1[Count].hue, Layer1[Count].saturation, Layer1[Count].current_brightness)
                    if(Layer1[Count].progress >= 1.00):
                        Layer1[Count].progress = 1.00
        
            for Count in range(Number_of_lights):
                Lights[Count].set_colour(Layer0[Count])
            interface.set_frame(universe.serialise())
            interface.send_update()
        


