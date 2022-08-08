The code of this projects is right now a complete mess and shouldn't be used by anyone who want to keep their sanity. A readme and desciption of the program will be published once it's in a usable state.

Modified code from PyDMX (https://github.com/JMAlego/PyDMX; Copyright (c) 2019-2022, Jacob Allen) is included in this project (see full license information in the license file).

Things to structure later:
- After choosing a main program and a sub program via midi note events, there is no memory of both of these key presses. That means that if you for example press C4 and D#4, release D#4 and press F#4 instead, nothing will happen since there is no memory left of C4 being held down. This is intentional.
- After you've initialized a program (by choosing a main program and a sub program), you cannot manipulate the parameters of that program. For example, the release time will be whatever you sat it to at the initialization even if you send new parameter instuctions afterwards.