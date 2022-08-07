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
                                    

                    

