# 478-marketbusters
## CSE 478 Fall 2022 Group Project

This semester, we researched the idea of correlation throughout various markets and assets. More specifically, we designed a "Correlation Moving Average Indicator", what we have coined "CORRMA", and created various algorithms to test if it may be used in a profitable trading manner. 

We have various results and codes throughout the repo. Please feel free to take a look, leave feedback, and try them yourself!

Testing Results: https://docs.google.com/spreadsheets/d/1crSXA8EVWAYZEFZIHKW3_GZTUM4e8Z4DNVAMQu4QANU/edit?usp=sharing

Final Presentation: https://docs.google.com/presentation/d/1GpWc5je-Q5FDnF0MsXeYrRv5RKLmwnlG/edit?usp=sharing&ouid=107033263361997095008&rtpof=true&sd=true


## Thoughts revisiting March 2023 (Crypto CORRMA)

I would like to investigate more regarding CORRMA as detailed by our Dec. 2022 final report. There are various aspects that seem overtly "random" that I'd like to deduce why they occur.

Here are some aspects I hope to analyze in the future:
- [ ] Why did the initial findings have such a major jump with ETH vs. BTC? Did changing the window and threshold find some "magic" combination that yielded massive returns? This seems too good to be true. When looking at the data, the win/loss ratio on trades is 53%/47%, but the comparison of average win to average loss is 399.17% win vs. -21.85% loss. That means the algorithm somehow found a unique place to capitalize on massive gains and only take smaller losses comparatively. I think there must be some unique historical circumstances where when ETH diverged from BTC, it most often had large gains, which meant the algorithm found the sweet spot of capitalizing on these gains. This *might not have happened!*
  - [ ] **However**, one thing that gives me some hope that it wasn't "entirely" random is that BTC and ETH *did* have similar cumulative returns charts for the same period (according to the `corrma_analysis()` method of the Jupyter file). This is confusing because QuantConnect shows that ETH B&H from 1/1/2017 is *much* better than BTC, but starting 1/1/2018, ETH is only slightly better. *There might be data discrepancies that I need to investigate*.
- [ ] Investigate the out-of-sample testing further.
- [ ] **Reflect on algorithm design (potential error?). It initially invests into the independent asset IMMEDIATELY, then waits WINDOW number of days until the algorithm is fully initialized... Is this a correct idea? It probably should just wait to invest until the indicator is fully ready.**
- [ ] Apply an SMA indicator to help determine which *way* assets are moving. Divergence could mean one asset moves *differently* - the *direction* is NOT known! Perhaps knowing direction could help determine a better algorithm for acting on CORRMA decisions. 
- [ ] Take some time to apply the CORRMA algorithm to specific stocks & sectors for more insight. Why does the algorithm seem to work so well on crypto but not other assets?
  - [ ] Discussion with Prof. Liu during the semester yielded two thoughts:
    - [ ] 1. "It simply could be random. These things happen and we don't know how it works. More investigation might be needed".
    - [ ] 2. "It might "seem" random to us, but behind the scenes, there may be larger forces at play that lead to this "discovery". We don't know how these assets change value or get traded. There could be some hidden knowledge that we don't know (and may never know) that puts us at a disadvantage."
- [ ] Reorganize the Repo. Remove unnecessary files. 
- [ ] Change repo name & adjust report links accordingly. 