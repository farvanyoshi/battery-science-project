#import "/lib/style.typ": *
#import "/lib/figures.typ": *

= Materials and Methods

== Materials

To design a zinc-ion battery, a cathode, anode, electrolyte, casing, and separator each must be created and combined into a final structure. The experimental casing was a 3D printed hollow cylinder with a 5.08 cm diameter and a height of 10.16 cm, as shown in @casing. While larger than a standard battery, this size allowed for easier designing and testing. The casing was made from PETG (polyethylene terephthalate glycol-modified), though any plastic used in 3D printing would have been suitable.

#photo("method/battery-casing.jpg", caption: [The casing used to house the battery.]) <casing>

The cathode, or positive terminal, was constructed from graphite current collector and a carbon-electrolyte mix, with manganese dioxide added for the final version. Three different current collectors were used for different parts of the experiment. A total of 66.23 g of activated carbon, 36.22 g of graphite powder, and 6.47 g of manganese dioxide were used to build the cathodes. The specific activated carbon powder used, as shown in @carbon, was coconut-based activated carbon powder from Belle Chemical, obtained from Amazon. The graphite powder, shown in @graphite, was obtained from Flinn Scientific through Dallastown Area High School. The manganese dioxide is shown in @MnO2 and was obtained through Amazon as well.

#side-by-side(
  [#photo("method/activated-carbon.jpg", width: 60%, height: 15em, caption: [The activated carbon.]) <carbon>],
  [#photo("method/graphite-powder.jpg", width: 60%, height: 15em, caption: [The graphite powder.]) <graphite>],
  [#photo("method/manganese-dioxide.jpg", width: 50%, height: 15em, caption: [The manganese dioxide.]) <MnO2>],
)

The electrolyte was also varied between designs to determine whether the anion plays a significant role in the battery. For the designs described in this paper, zinc sulfate heptahydrate and zinc chloride were used. Zinc sulfate is more stable and is often used in zinc-ion battery prototypes, but zinc chloride has a much higher solubility, allowing for higher concentrations and thus higher currents. All of the zinc sulfate and zinc chloride used in these experiments was obtained via Amazon, with the specific brands visible in @zinc-sulfate and @zinc-chloride, respectively. A total of 82.85 g of zinc sulfate heptahydrate and 136.29 g of zinc chloride were used to produce the various electrolytes used for the batteries described in this paper.

#side-by-side(
  [#photo("method/zinc-sulfate.jpg", width: 27%, caption: [The zinc sulfate heptahydrate used in this paper.]) <zinc-sulfate>],
  [#photo("method/zinc-chloride.jpg", width: 27%, caption: [The zinc chloride used in this paper.]) <zinc-chloride>],
)

The anode used in these batteries was a zinc foil, and was kept constant through every iteration. Since the purpose of the anode of a zinc-battery is to simply oxidize zinc, any other material would be less effective. The zinc foil is shown in @zinc-foil, and a new piece of foil was used in each iteration. The foil had a thickness of 0.1 mm, and a 10 mm by 8 mm piece was cut out for each iteration.

#photo("method/zinc-foil.png", caption: [A piece of zinc foil used in the designs.]) <zinc-foil>

To carry out the measurements necessary to evaluate the different batteries, a Vernier current and voltage probe, as shown in @current and @voltage, were wired into the various circuits. Since the data often needed to be collected unattended, a LabQuest 2, as shown in @labquest, was used to collect the data.

#side-by-side(
  [#photo("method/current-probe.jpg", width: 90%, caption: [A current probe.]) <current>],
  [#photo("method/voltage-probe.jpg", width: 90%, caption: [A voltage probe.]) <voltage>],
  [#photo("method/labquest.jpg", width: 90%, caption: [A Vernier LabQuest 2, used to record data unattended.]) <labquest>],
)

In order to charge the various batteries, a power supply was used with constant voltage control. The specific power supply used, as shown in @supply, was a GW Instek GPS-1850D DC power supply.

#photo("method/power-supply.jpg", width: 50%) <supply>

== Procedure

While the quantities and some materials differed between the various iterations, the fundamental methodology remained mostly unchanged. Thus, this paper has described the first iteration in detail, while only listing the most notable changes between iterations, as well as any differences in the testing done for each iteration.

The design of each battery was divided into three steps: making the electrolyte, constructing the cathode, and building the battery. The electrolyte used in the first battery consisted of 2.5 M #ce("ZnSO4") solution. 40.37 g of #ce("ZnSO4") were measured out and placed in a beaker. Regular water was added until the volume of the solution in the beaker was 100 mL to produce the 2.5 M solution. The solution was thoroughly stirred until clear. Afterward, 15.56 g of activated carbon powder and 6.33 g of graphite powder were measured out and stirred in a bowl until thoroughly mixed. Next, a pipette was used to slowly add small amounts of the zinc sulfate solution to the powder mix. The mixture was made damp, yet not wet, and had a consistency similar to peanut butter when complete. This paste is shown in @goop1.

#photo("method/carbon-paste.jpg", width: 50%, caption: [A picture of the carbon-electrolyte paste.]) <goop1>

The paste was then spread evenly around a rod of graphite to produce the cathode. However, to stop the paste from interacting with the anode and dissolving into the electrolyte, the cathode was wrapped with filter paper and sealed with hot glue. The cathode was placed in the battery housing (@casing) with the zinc foil. Lastly, the remaining amount of solution was added to the casing to act as the electrolyte. The finished version of the first battery is shown in @battery1.

#photo("method/first-battery.jpg", width: 15%, caption: [The completed first battery. The cathode can be seen sticking out of the battery,\  while the zinc foil anode lines the edge of the casing.]) <battery1>

The first iteration of the battery was a prototype and not used for any of the data shown below, as the data was neither standardized nor reliable. The second iteration of the battery was similar to the first, but involved proper standardization of data collection, and the data from the second iteration was used for analysis.

The second iteration of the battery, though similar to the first battery, was using less materials, so that a general decrease was expected across the measurements. The electrolyte was made using 21.6 g of #ce("ZnSO4"), and water was added until the solution had a volume of 50 mL, equivalent to a concentration of 1.5 M. Only 9.22 g of activated carbon and 3.74 g of graphite powder were used. The graphite rod from the first iteration was cleaned off and reused for the second iteration.

The battery was connected in series with a current probe and a resistance box (which allows for varying the resistance), while a voltage probe was connected in series. The circuit is shown in @discharge, though a schematic is also visible in @d-schem. The Vernier LabQuest 2 (shown in @labquest) was set to measure 6 samples per minute for 480 minutes, which is equivalent to 1 sample every 10 seconds for 8 hours. Later iterations were measured at 30 samples per minute (1 sample every 2 seconds).
#side-by-side(
  [#photo("method/discharge-circuit.jpg", width: 85%, caption: [An example of a discharge circuit.]) <discharge>],
  [#photo("method/discharge-schematic.png", width: 85%, caption: [A schematic of a discharge circuit. The battery shown has internal resistance.]) <d-schem>],
)
The next step was to charge the battery. Simply charging the battery while measuring the current and voltage would not show the emf, which is equivalent to the open circuit voltage. To do so, an Arduino microcontroller board was connected to a relay wired into the circuit. The arduino and its wiring when not connected to a battery circuit is shown in @arduino.

#photo("method/arduino.jpg", width: 40%, caption: [The arduino used to time the charging circuit. The purple wire connects digital pin 10 to the coil and returns to ground through the white wire. The red and green wires connect to the battery circuit.]) <arduino>

The arduino was set to wait for 4 minutes, disconnect the circuit for one minute, then reconnect the circuit, on loop. The code is shown here:
#raw(read("/assets/code/charge-timer.ino"), lang: "cpp", block: true)
This program sets the output to digital pen. The ```cpp setup()``` function runs once when the Arduino is first connected to power. It initializes the Arduino to read any input data at 115200 symbols per second (115200 baud) and sets digital pin 10 as an output. Afterword, in the ```cpp loop()``` function, the Arduino turns off the pin, waits 4 minutes, turns the pin on, waits for a minute, and then repeats. Turning the pin on activated the relay and opens the circuit. The LabQuest 2 was timed to collect the current and voltage once very 2.5 minutes, so that the current while charging could be read, then the emf could be read while the circuit was open, 2.5 minutes later. The LabQuest 2 was set to collect, then the Arduino was activated 10 seconds later, so that the two would not interfere with one another. Each charge lasted for 60 minutes, with the current supply set to a constant voltage of 1.5 V. This time and voltage was chosen to ensure that the battery would not be charged for too long (leading to battery damage and the formation hydrogen gas). A schematic of the charging circuit is shown in @c-schem, where the battery is modeled as a load (resistance) for the power supply.

#photo("method/charge-schematic.png", width: 50%, caption: [A schematic of the battery while charging.]) <c-schem>

The second iteration battery was discharged across a #qty(100, "ohm") resistor three times and charged three times.

The third iteration of the battery featured a different graphite rod and a switch to zinc chloride electrolyte. Anhydrous zinc chloride was used, as shown previously in @zinc-chloride. Equivalent amounts of activated carbon and graphite powder were used as was in the second iteration of the battery. However, the electrolyte was instead made using 20.45 g of #ce("ZnCl2") to produce 1.5 M #ce("ZnCl2") solution. This solution was used in the creation of the paste and as the electrolyte for the battery.

The circuits used to test the third battery were the same as those used to test the second iteration battery. However, the external resistance was varied for each discharge. The third battery battery was originally discharged across #qty(10, "ohm"), then at #qty(1000, "ohm"), and lastly at #qty(100, "ohm"). This battery was charged between each discharge using the process listed before at 1.5 V.

As an extra test, the cathode from the third iteration battery was combined with a new piece of zinc in zinc sulfate solution instead to examine the effect of mixing the electrolytes. Water was added to 40.91 g of zinc sulfate until the total concentration of the solution reached 100 mL. This electrolyte was then used in place of the zinc chloride previously used for the third iteration. This battery was only discharged once, however, due to the terrible performance of this battery.

The fourth iteration of the battery was designed with much more graphite. A new cathode consisting of a fresh graphite rod, 9.88 g of activated carbon and 11.19 g of graphite powder were used, while 40.89 g of zinc chloride were used instead to increase the concentration to 3 M #ce("ZnCl2"). This battery was discharged at 10#unit("ohm"), 1000#unit("ohm"), and 100#unit("ohm"), with the battery being charged between each discharge.

The fifth and final iteration of the battery involved some more drastic changes, in a last attempt to improve performance and show more "battery-like" behavior. First, distilled water was obtained and used instead of regular water. The concentration was increased up to 6 M, using 102.23 g of #ce("ZnCl2") combined with enough distilled water to create 125 mL of solution at 6 M concentration. The cathode was made using 16 g of activated carbon, 7.77 g of graphite powder, and 6.47 g of manganese dioxide through the same processes as before. By adding the manganese dioxide, it was thought that the battery may perform much better. Then, through the same processes as done before, the battery was constructed in the casing. To ensure that the final battery would show the best performance upon data collection, this battery was first charged for an hour at 2.4 V (the theoretical potential for this battery), where data was not collected. Data was then collected of the final battery being discharged across a 1000#unit("ohm") resistor for 240 minutes (4 hours) to allow the battery to "break-in" (allowing for an increase in performance after the first discharge, shown in some studies @ming_2019_zincion) and provide optimal performance on the next run. Using the Arduino-based circuit from before, this battery was recharged for 1 hour at 2.2 V. Lastly, the battery was discharged across a 10#unit("ohm") resistor for 8 hours. While a lower resistance would have allowed for more energy to be released over the same period, keeping the resistance at 10#unit("ohm") allowed for fair comparison with all of the previous tests.

Finally, a standard rechargeable AA nickel-metal hydride battery was discharged to provide a comparison. The battery was discharged across a 1000#unit("ohm") resistor for 8 hours. Due to the dangers of recharging a commercial battery across a power supply and the inability to control the workings of a commercial NiMH battery charger safely, the battery was not recharged, and this graph was only used as a standard for comparison.
