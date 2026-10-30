#import "/lib/style.typ": *
#import "/lib/figures.typ": *
#import "/lib/tables.typ": *

= Results

== Data
#graph("Pot2", caption: [A graph showing how the voltage changed over time for each discharge of Iteration 2.]) <Pot2>

#graph("C2-D1", caption: [A graph showing current versus time and the integral of current for the first discharge of Iteration 2.]) <C2-D1>

#graph("C2-D2", caption: [A graph showing current versus time and the integral of current for the second discharge of Iteration 2.]) <C2-D2>

#graph("C2-D3", caption: [A graph showing current versus time and the integral of current for the third discharge of Iteration 2.]) <C2-D3>

#graph("Ch2", caption: [A graph of the emfs measured during each charge of Iteration 2.]) <Ch2>

#graph("C2-C", caption: [A graph of the currents measured during each charge of Iteration 2.]) <C2-C>

#graph("Pot3", caption: [A graph showing how the voltage changed over time for each discharge of Iteration 3.]) <Pot3>

#graph("C3-D1", caption: [A graph showing current versus time and the integral of current for the first discharge of Iteration 3.]) <C3-D1>

#graph("C3-D2", caption: [A graph showing current versus time and the integral of current for the second discharge of Iteration 3.]) <C3-D2>

#graph("C3-D3", caption: [A graph showing current versus time and the integral of current for the third discharge of Iteration 3.]) <C3-D3>

#graph("Pot3b", caption: [A graph showing how the voltage changed over time for the discharge of the modified Iteration 3.]) <Pot3b>

#graph("C3b", caption: [A graph showing how current varied over time and the integral of current for the modified Iteration 3.]) <C3b>

#graph("Ch3", caption: [A graph of the emfs measured during each charge of Iteration 3.]) <Ch3>

#graph("C3-C", caption: [A graph of the currents measured during each charge of Iteration 2.]) <C3-C>

#graph("Pot4", caption: [A graph showing how the voltage changed over time for each discharge of Iteration 4.]) <Pot4>

#graph("C4-D1", caption: [A graph showing current versus time and the integral of current for the first discharge of Iteration 4.]) <C4-D1>

#graph("C4-D2", caption: [A graph showing current versus time and the integral of current for the second discharge of Iteration 4.]) <C4-D2>

#graph("C4-D3", caption: [A graph showing current versus time and the integral of current for the third discharge of Iteration 4.]) <C4-D3>

#graph("Ch4", caption: [A graph of the emfs measured during each charge of Iteration 4.]) <Ch4>

#graph("C4-C", caption: [A graph of the currents measured during each charge of Iteration 2.]) <C4-C>

#graph("Pot5", caption: [A graph showing how the voltage changed over time for each discharge of Iteration 5.]) <Pot5>

#graph("C5-D1", caption: [A graph showing current versus time and the integral of current for the first discharge of Iteration 5.]) <C5-D1>

#graph("C5-D2", caption: [A graph showing current versus time and the integral of current for the second discharge of Iteration 5.]) <C5-D2>

#graph("PotS", caption: [A graph showing how the voltage changed over time for the discharge of the NiMH battery.]) <PotS>

#graph("CS", caption: [A graph showing current versus time and the integral of current for the discharge of the NiMH battery.]) <CS>

== Data Analysis

The power from the battery at any given instant can be calculated using the voltage and the current using the following equation:

$ P=I V $ <power>

Using @power, the graph of power v. time can be plotted for all of the charges and discharges, as shown in the following figures. Using these graphs of power v. time, the total energy released by the battery over that time period can be calculated using the integral of power in the following equation:

$ E = integral_0^t_f P(t) dif t $ <energy>

The $t_f$ in @energy represents the final time of the definite integral. However, while an integral requires a continuous function, there are only a finite number of data points. Thus, a trapezoidal Riemann sum was used to approximate each integral in the form shown in @energy-sum.

$ E approx (Delta t)/2 sum_(n=0)^(t_f-1) (I(n) dot V(n) + I(n+1) dot V(i+1)) $ <energy-sum>

#graph("P2", caption: [A graph showing the power versus time and its integral for Iteration 2.]) <P2>

#graph("P3", caption: [A graph showing the power versus time and its integral for Iteration 3.]) <P3>

#graph("P4", caption: [A graph showing the power versus time and its integral for Iteration 4.]) <P4>

#graph("P5", caption: [A graph showing the power versus time and its integral for Iteration 5.]) <P5>

The effective charge capacity is a metric of how much charge can the battery transfer within a certain voltage range. Similarly, the effective energy of a battery is determined by how much energy is released within a useful voltage range. A AA battery, like the NiMH battery used for comparison, is only useful when the voltage is greater than 0.9 V on average @energizer_2010_energizer. Thus, finding the area beneath each curve of current v. time and power v. time while the voltage is greater than 0.9 V would give the effective charge capacity and effective energy, respectively. Thus, @cap2 shows the effective capacity and effective energy for iteration 2. The values are given in the derived units from the graph and in standard SI units.

#effective-table(2, caption: [The effective capacity and effective energy of each discharge for Iteration 2.]) <cap2>

#effective-table(3, caption: [The effective capacity and effective energy of each discharge for Iteration 3.]) <cap3>

#effective-table(4, caption: [The effective capacity and effective energy of each discharge for Iteration 4.]) <cap4>

#effective-table(5, caption: [The effective capacity and effective energy of each discharge for Iteration 5.]) <cap5>

To allow for effective comparison between the different batteries, each of which was made with different chemistries and showed different charge/discharge graphs, each charge and discharge was normalized by dividing every value in a charge or discharge by the first value. An example of the normalization formula is shown in @norm. Due to being defined as a quantity at some time divided by the initial value of that quantity, normalized versions of a quantity do not have any units. Since the normalized values can be easily compared though the actual values may differ substantially, all of the normalized graphs contain the best curve fit approximations of each graph. 

$ V_"norm" = V/V_0 $ <norm>

#graph("Vnorm", caption: [A graph of all of the normalized voltages versus time for the first discharge of each iteration.]) <Vnorm>

#graph("Cnorm", caption: [A graph showing the current v. time for all of the discharges done at 10 ohms.]) <Cnorm>

The internal resistance of a battery was calculated from the following equation:

$ V = epsilon - I r $ <Vterm>

In this equation, $V$ represents the terminal voltage, $epsilon$ is the emf, $I$ is the current, and $r$ is the internal resistance. Rearranging this equation for $r$ gives @int-res. While the emf of the battery cannot be found during a discharge, the emf at the beginning and end of each discharge were known from the open-circuit voltage that is measured at the beginning of each discharge (as the data collection was started just before the circuit was wired), or from the charging tests, which involved directly measuring the emf. Using those emf values, along with the first or last voltage and current values measured for a discharge, the internal resistance can be determined at the beginning and end of each discharge, using the formula listed in @int-res.

$ r = (epsilon - V)/I $ <int-res>

#resistance-table("start_ohm", caption: [A table of the internal resistances at the beginning of each discharge.]) <start-r>

#resistance-table("end_ohm", caption: [A table of the internal resistances at the end of each discharge.]) <end-r>
