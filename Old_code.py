

    ################
    ### Old code ###
    ################
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

        while True:
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
