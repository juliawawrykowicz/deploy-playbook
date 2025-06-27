# Harness Location-Specific Energy Intelligence

Pinpoint wind and solar project potential across 67,000 US sites

## Solar Cost Curve
*LCOE incl. transmission costs, capex for new technologies, and land-siting constraints*

<div class="responsive-iframe">
  <div id="loading-message" style="position: absolute; top: 0; width: 100%; font-size: 18px; font-weight: bold;">
    Interactive Map is Loading...
  </div>
  <iframe 
    src="https://juliawawrykowicz.github.io/examples/usa_PV_cost_curve.html" loading="lazy"
    onload="document.getElementById('loading-message').style.display='none';">
  </iframe>
</div>

<style>
.responsive-iframe{position:relative;padding-top:56.25%;height:0;}
.responsive-iframe iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0;}
</style>

!!! abstract "Cost Curve Maps"

    Interactive map shows potential plant capacity (marker size) and levelized cost of energy (color scale: green = low, yellow = medium, red = high). Zoom out to view nationwide opportunities.

## Wind Cost Curve
*LCOE incl. transmission costs, capex for new technologies, and land-siting constraints*
 
<div style="position: relative; width: 100%; height: 0; padding-top: 56.25%; max-height: 100vh; overflow: hidden;">
  <iframe
    src="https://juliawawrykowicz.github.io/examples/usa_wind_cost_curve.html"
    loading="lazy"
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;">
  </iframe>
</div>


## Model Components

- __Resources__: Incorporates high-fidelity wind speed and solar irradiance data

- __Technology & Cost__: Utilizes detailed assumptions for technology design and project finance

- __Siting Constraints__: Accounts for physical, regulatory, and environmental restrictions

- __Grid Connection Cost__: Models costs associated with grid interconnection

``` mermaid
graph LR
  A[Wind Resource] --> E[Hourly Generation];
  D[Turbine Specs] --> E;
  E --> F[Site LCOE];
  H[Power Grid] --> I[Supply Curve];
  F --> I;
  G[Land Use] --> I;

```


### Technology and Costs

The following technical and financial parameters serve as the baseline for the supply curve calculations. The model assumes a 30-year capital recovery period with capital expenditure estimates benchmarked for the year 2030.

=== "Solar PV Characteristics"
| Parameter                | Value                      |
| :----------------------- | :------------------------- |
| PV Array Nameplate | 1 MW                       |
| PV Array Type | 1-axis tracking            |
| Tilt | 0 degrees                  |
| System Losses | 10.4%                      |
| Inverter Loading Ratio| 1.34                       |
| Capacity Density | 43 MWdc/km²                |
| Capital Expenditures | 1,042 (2021$/kWac)         |
| Fixed O&M | 18.4 (2021$/kWac/yr)       |
| Fixed Charge Rate | 0.06778                    |

=== "Wind Technology Characteristics"
| Parameter                | Value                      |
| :----------------------- | :------------------------- |
| Turbine Nameplate | 6 MW                       |
| Rotor Diameter | 170 m                      |
| Hub Height | 115 m                      |
| System Losses | Calculated                 |
| Capacity Density | Calculated                 |
| Capital Expenditures | 1,150 (2021$/kW)           |
| Fixed O&M | 27 (2021$/kW/yr)           |
| Fixed Charge Rate | 0.080373                   |

### Siting Constraints

While clear obstructions like highways and urban areas are easily excluded, the model also navigates more complex land-use challenges.

In the most restrictive scenario, the model applies environmental and national defense considerations in addition to standard exclusions for physical obstacles, protected lands, and regulatory setbacks.

### Grid Connection Costs

The cost of connecting a project to the electrical grid is estimated by:

1. Calculating the cost of a new spur line using a least-cost-path algorithm.

2. Estimating associated network and substation upgrade costs.

!!! tip "Projects De-Risked"

    Whether optimizing assets or scouting greenfield developments, this tool translates technical complexity into investment clarity.