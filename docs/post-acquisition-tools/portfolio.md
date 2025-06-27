# Post-Acquisition Playbook: Where to Overbuild

Investors targeting fiber expansion or copper overbuilds must navigate shifting competitive dynamics. In many markets, cable and fixed wireless - once considered inferior - now offer top-tier speeds, __especially where 5G powers fixed wireless deployments__. This intelligence helps avoid costly overbuilds into already well-served areas and pinpointing zones where new infrastructure can drive value. 

<div class="responsive-iframe">
  <div id="loading-message" style="position: absolute; top: 0; width: 100%; font-size: 18px; font-weight: bold;">
    Interactive Map is Loading...
  </div>
  <iframe 
    src="https://juliawawrykowicz.github.io/examples/rivalry_Denver.html" loading="lazy"
    onload="document.getElementById('loading-message').style.display='none';">
  </iframe>
</div>

<style>
.responsive-iframe{position:relative;padding-top:56.25%;height:0;}
.responsive-iframe iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0;}
</style>

!!! abstract "Broadband Deployment Maps"

    Interactive map shows the highest-speed offerings per city block in Denver. It identifies where 2 Gbps cable internet from Comcast or 300 Mbps fixed wireless internet from Verizon are the top offerings. Zoom in to view any city block.

## Model Components

- __Technology__: Covers all fixed-broadband types: copper, cable, fiber, and fixed wireless.

- __Speed__: Ranks providers by speed performance; e.g, 5G fixed wireless may outperform cable 

- __Building IDs__: Assesses broadband availability and speed at the individual building level 

- __City Blocks Geolocaion__: Visualizes competition by city block for localized market insight

``` mermaid
graph LR
  
  C[All Offerings per Bld] --> D[Top Offering for Each Provider per Bld];
  I[Rank Provider's Offerings by Bld] --> D[Top Offering for Each Provider per Bld];
  D --> E[Top Provider-Offering per Bld];
  J[Rank Providers by Bld] --> E[Top Provider-Offering per Bld];
  H[Blds per Block] --> F[Top Provider-Offering per Block];
  E --> F[Top Provider-Offering per Block];
  F --> G[Map];
  A[City Boundaries] --> B[City Blocks Geometry];
  B --> G;
  
```