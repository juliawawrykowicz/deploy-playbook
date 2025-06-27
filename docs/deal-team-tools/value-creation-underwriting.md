# Maximize Fiber ROI in Emerging Markets

Identify the best connectivity path for each unserved location - factoring in demand, mobile coverage, tower visibility, and fiber proximity - to prioritize deployment with the highest IRR.

<div class="responsive-iframe">
  <div id="loading-message" style="position: absolute; top: 0; width: 100%; font-size: 18px; font-weight: bold;">
    Interactive Map is Loading...
  </div>
  <iframe 
    src="https://juliawawrykowicz.github.io/examples/Brazil_Map.html" loading="lazy"
    onload="document.getElementById('loading-message').style.display='none';">
  </iframe>
</div>

<style>
.responsive-iframe{position:relative;padding-top:56.25%;height:0;}
.responsive-iframe iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0;}
</style>

!!! abstract "Example: School Connectivity Map"

    Explore the interactive map below: hover over each school to view site-specific connectivity data.

## Model Components

- __Satellite Detection__: Uses AI and satellite imagery to pinpoint schools in the target country

- __Terrain Analysis__: Determines line-of-sight from each nearby tower to candidate locations

- __Telecom Infrastructure__: Maps mobile coverage, towers, and fiber access points

- __Local Demographics__: Measures population density within defined radii of each site

- __Demand Forecast__: Converts population data into location-specific demand projections

- __Cost Estimate__: Compares buildout costs for fiber, fixed wireless, and mobile internet options


``` mermaid
graph LR
  A[Terrain Analysis] --> E[Technical Feasibility];
  B[Telecom Infrastructure] --> E;
  C[Local Demographics] --> F[Demand Forecast];
  E --> G[Cost Estimate];
  G --> H[Recommended Connectivity Option per Site];
  F --> H;

  
```