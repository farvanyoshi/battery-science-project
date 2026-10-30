#import "/lib/style.typ": *
#import "/lib/figures.typ": *

== Theory and Principles

A battery is composed of three essential parts: an anode, a cathode, and an electrolyte. The anode is the negative terminal of a battery, while the cathode is the positive terminal. Thus, the current of a battery goes from the cathode to the anode during discharge. In reality, charge is carried by electrons, which flow in the opposite direction of the current because of their negative charge. Batteries are built so that those electrons cannot travel within the battery and thus must travel through an external circuit in order to reach the cathode. To complete the circuit, the ions within the battery must transfer charge from the anode to the cathode as well. Thus, a battery does not store any charge, but instead forces the movement of charge (in the form of electrons) through a wire to create a current, making a battery a "charge pump". Following this analogy, the potential difference produced by the battery is essentially the "pressure" applied by the "charge pump" on the electrons and ions. After factoring the movement of charge of ions inside the battery, the battery has neither stored nor released any charge, but instead moved the charges from one end of the battery to the other while doing useful work. Often, batteries contain a separator, a material preventing direct contact between the anode and cathode (that would cause a short circuit) while allowing dissolved ions to pass, as shown in @model.

#photo("intro/li-ion-discharge.png", caption: [A model of the discharge of a lithium-ion battery. Electrons travel to the cathode following the blue arrows, while ions within the battery follow the red arrows through the black separator.]) <model>

Almost all zinc-ion batteries involve the use of zinc metal for the anode. The anode reaction is represented by the following equation.

$ "Zn"(s) -> "Zn"^(2+)(a q) + 2e^- $ <zinc-ox>

The electrochemical potential of various reactions are defined using the standard reduction potential. Since a reduction cannot happen without an oxidation, the standard hydrogen reaction is assigned a reduction potential of #qty(0, "V"), and all other standard reduction potentials are based on that @cowie_2014_eetimes. The standard reduction potential is measured at a temperature of #qty(298.15, "K") (#qty(25, "deg C")) and #qty(1, "M") concentration solutions. The above reaction is the oxidation of zinc, which is simply the reverse of the zinc reduction reaction.

$ "Zn"^(2+)(a q) + 2e^- -> "Zn"(s) $ <zinc-red>

The standard oxidation potential is the negative of the standard reduction potential. As @zinc-red is $E_"reduction" degree = #qty(-0.76, "V")$, the reaction of @zinc-ox creates an electrochemical potential of #qty(0.76, "V"). 

As zinc is converted into zinc ions, it dissolves into the electrolyte. This electrolyte consists of a zinc compound dissolved in water, such as zinc sulfate or zinc chloride. A higher electrolyte concentration increases the solution conductivity, which is equivalent to decreasing the internal resistance of the battery. Decreasing the internal resistance allows for a higher maximum current from the battery. However, once the concentration is too high, the increase in viscosity due to the solute impedes the movement of ions in the solution, increasing the internal resistance. Thus, finding the best electrolyte concentration to minimize the internal resistance of the battery is an important part of battery design. Different electrolytes also have different solubilities and conductivities, so varying the electrolyte can also help to minimize the internal resistance.

The cathode was constructed using a solid piece of graphite, graphite powder, and activated carbon powder, each of which serve different functions. The solid piece of graphite functions as a current collector, to which wires can be attached and through which a circuit can be completed. While graphite and activated carbon are both carbon allotropes, they serve different purposes here.

The purpose of graphite powder was to intercalate zinc ions. Intercalation is the insertion of a molecule or ion (the guest species) between the sheets of a layered compound (the host). Layered compounds are best described as a series of stacked sheets, with strong intermolecular bonding within the layer, but weaker bonding between layers. Graphite is the most well-known example of this phenomenon. As shown in @intercalation, a guest species can expand the layers of a layered structure so that the species can be stored between those layers @inaba_2009_secondary. The energy needed to expand these layers is normally derived from a redox reaction, such as the oxidation of zinc in this case. If the guest species is ionic, the host-guest combination will have a net charge. Intercalation is used in most "-ion" batteries, such as lithium-ion and zinc-ion batteries. For intercalation to happen in a zinc-ion battery, the host material should be the cathode, and ions in solution will intercalate into the layer structure while discharging.

#photo("intro/intercalation.jpg", caption: [The main transitions during the intercalation of a guest species into a graphite host.]) <intercalation>

While intercalation and other possible cathode reactions are well-studied in lithium-ion batteries, there is less known about what occurs in zinc-ion batteries with a graphite cathode. Nevertheless, the cathode reaction between zinc and the layers of graphite, as shown in @interc-eq, contributes to the potential difference of the battery.

$ ce("C")_x + "Zn"^(2+) + 2e^- -> ce("ZnC")_x $ <interc-eq>

All graphite intercalation compounds have the formula $"XC"_n$, where $n>=6$ @iupac_1994_international. However, the properties of zinc ions cause those ions to intercalate non-stoichiometrically, and can vary heavily depending on the method and the compound used for intercalation. Zinc ions are divalent, which allows for more complex bonding and interactions between the graphite and zinc. The distance between successive layers of graphite is about #qty(3.50, "angstrom") on average @akmak_2019_continuous. While zinc only has an ionic radius of #qty(0.74, "angstrom"), anions (chlorine ion, sulfate ion, etc.) also intercalate between the layers. The anions have much larger ionic radii, such as #qty(1.81, "angstrom") for chlorine ions and #qty(2.42, "angstrom") for sulfate ions on average @nationalinstituteofhealth_2004_sulfate. Besides those factors, electrostatic repulsion and disruption of the graphite structure due to the presence of these ions cause graphite to expand during intercalation.

The final iteration of the battery also included manganese dioxide (#ce("MnO2")) in the construction of the cathode. Manganese dioxide is another intercalating compound and has been found in some studies to be more or as effective as graphite for intercalation in zinc-ion batteries @ming_2019_zincion. Zinc and manganese dioxide are fundamental components to alkaline batteries, but a different reaction occurs in alkaline batteries which is not reversible. The reaction that occurs in zinc-ion batteries (which is reversible) is modeled by the following chemical equation:

$ "Zn"^(2+) + 2"MnO"_2 + 2e^- --> ce("ZnMn2O4") $

The final part of the cathode is activated carbon powder, which is also known as activated charcoal. Activated carbon has an extremely high surface area of over #qty(3000, "m^2/g"). This makes activated carbon useful for filtration, odor removal, and nullifying toxins, among other uses @islam_2021_a. Activated carbon does not have the layered structure necessary for intercalation, but the extremely high surface area allows for adsorption of zinc ions onto the surface of the powder. Adsorption is a process by which one material, the adsorbate, adheres to the surface of another material (the adsorbent) @lpez_2023_applications.

Activated carbon is able to adsorb zinc ions to its surface through the use of van der Waals and London dispersion forces. Van der Waals forces can be caused by a variety of factors, but the most likely one here is the Debye force, where momentary dipoles that form and disappear in the graphite attract the positively charged zinc ions. London dispersion forces arise in the interaction between momentary dipoles in both molecules. However, since these zinc ions are positively charged, an outer layer of negatively charged ions forms loosely around the inner layer of positive zinc ions. This phenomenon is known as the electric double layer (EDL), and is visible in activated carbon due to the enormous surface area. However, studies have shown that this electric double layer stores electrical energy through what is called double layer capacitance @shi_1996_activated. This capacitance is not constant and can be found by the following equation:

$ C = (dif sigma)/(dif Psi) $ <edlc>

Where $sigma$ is the charge of the surface and $Psi$ is the electrical potential at the surface of the activated carbon. As there is no simple method of measuring this surface charge and surface potential, it is better to view more general properties to which the double layer contributed, such as the battery charge capacity and the terminal voltage measured from the battery. The presence of activated-carbon would theoretically cause some capacitive effects in the battery due to the presence of the EDL. However, as in a capacitor, these processes would only be expected to dominate the current and voltage at the beginning of a discharge, as eventually intercalation reactions (which run slower and are exhausted later) would become more prevalent. As such, the initial current and voltage during a discharge could be considerably higher than the values determined for most of the discharge, but the values would eventually stabilize when intercalation effects become more dominant.

A zinc-ion/graphite battery has a theoretical standard cell potential of #qty(2.2, "V") @zhang_2020_electrochemical. Subtracting the oxidation potential of zinc at #qty(0.76, "V") gives a standard reduction potential of #qty(1.44, "V") for the intercalation of zinc in graphite. On the other hand, the reduction potential of manganese dioxide depends on the specific structure, and can vary between 1.3 and 1.4#unit("V") @ming_2019_zincion. Since the reduction potential of the zinc-graphite intercalation relation is similar to the reduction potential of the zinc-manganese dioxide intercalation reaction, it can be assumed that the theoretical cell potential, even with the manganese dioxide, is still 2.2#unit("V").

However, the values listed above for reduction potentials and the overall cell potential above do not consider variations from standard conditions, which require the Nernst equation:

$ E= E degree - (R T)/(n F) ln Q $ <nernst>

In this equation, $E$ is the cell potential in non-standard conditions (measured in V), $E degree$ is the standard cell potential (V), $R$ is the universal gas constant (#qty(8.314, "J/mol/K")), $T$ is the absolute temperature, $n$ is the number of electrons transferred in a single reaction, $F$ is Faraday's constant, the absolute value of the charge of 1 mole of electrons (#qty(96485, "C/mol")), and $Q$ is the reaction quotient for the specific reaction. For this specific type of battery, the net chemical equation can be written as:

And, as known from @zhang_2020_electrochemical, the theoretical electrochemical potential from this net reaction is #qty(2.2, "V") at the standard conditions. However, the concentration of the electrolyte can affect the cell potential through the Nernst equation. Knowing that $n=2$ for the zinc ion battery, the individual Nernst equations for the anode and cathode take the following form:

$
  E_a&=E degree_a + (R T)/(2 F) ln ["Zn"^(2+)]/["Zn"]wide wide&&("Anode") \
  E_c &= E degree_c + (R T)/(2 F) ln [ce("ZnC")_x]/["Zn"^(2+)]&&("Cathode")
$

However, the concentration of zinc and the concentration of the zinc-graphite intercalation compound is constant, as these materials are solids. Thus, they can be omitted from the calculation to give the following equations:

$
  E_a&=E degree_a + (R T)/(2 F) ln ["Zn"^(2+)] \
  E_c &= E degree_c - (R T)/(2 F) ln["Zn"^(2+)]
$

The overall cell potential is equivalent to the difference in the reduction potentials of the cathode and anode. Thus, an overall Nernst equation can be derived for the cell, as shown in @nernst-zib.


$
  E_"cell" = E_"cathode" - E_"anode" \
  E_"cell" = (E degree_c - (R T)/(2 F) ln["Zn"^(2+)]) - (E degree_a + (R T)/(2 F) ln ["Zn"^(2+)]) \
  E_"cell" = E degree_c - E degree_a - (R T)/F ln["Zn"^(2+)] \
  E_"cell" = E degree_"cell" - (R T)/F ln["Zn"^(2+)]
$ <nernst-zib>

However, since the zinc ions should be reacting at the cathode at around the same rate as the anode, the concentration of zinc ions is not changing much overall and the cell potential for a single battery should not be expected to change much. Furthermore, the quantity $(R T)/F$ is very small, so the deviation from the standard cell potential should be minimal. Thus, the Nernst equation's (@nernst) effects can be ignored and the theoretical cell potential can be assumed to be #qty(2.2, "V") for the batteries made in this experiment @zhang_2020_electrochemical.

The potential measured by placing a voltage probe across the ends of a battery while discharging would not be the cell potential however; every battery has an internal resistance, which is the opposition to the movement of charge within the battery. The cell potential is also called the emf, while the voltage while discharging is called the terminal voltage, and varies with the current through the following equation:

$ V = epsilon - I r $

In this equation, _V_ is the terminal voltage, $epsilon$ is the emf (or cell potential), _I_ is the current, and _r_ is the internal resistance of the battery. Though modeled as a resistor, the internal resistance is not caused by any resistive elements in the battery; rather, it is caused by the formation of concentration gradient that opposes the flow of current @zhang_2020_fundamentals.

A nickel-metal hydride (NiMH) battery was used as a standard for comparison to the zinc-ion battery, as its uses overlap with many of the potential uses of a zinc-ion battery. NiMH batteries are a very common type of rechargeable battery. They are able to safely discharge at higher currents, can be charged and discharged hundreds of times with minimal loss in capacity, and remain usable for a long amount of time. However, NiMH batteries also have the highest rate of energy loss when not in use of the common batteries. This phenomenon is known as self-discharge, and standard NiMH batteries can lose 15% of their stored energy per month, making these batteries ineffective for grid storage.
The reactions of the nickel-metal hydride battery can be seen below. In these equations, "#ce("M")" represents a metal alloy of some sort. NiMH cells require an alkaline electrolyte, which usually is potassium hydroxide.

$
  ce("H2O + M + e-") &ce("<=> OH- + MH") && ("Anode") \
  ce("Ni(OH)2 + OH-") &ce("<=> NiO(OH) + H2O + e-") wide && ("Cathode")
$

In order to determine the feasibility of zinc-ion batteries for usage in commercial applications, the cathode and electrolyte were varied to find which combinations would produce the best results. In every design, the zinc anode was kept the same, and the casing used was identical. To provide a basis for comparison, a nickel-metal hydride battery was discharged as well.
