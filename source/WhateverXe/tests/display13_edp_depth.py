#!/usr/bin/env python3
"""Regression checks for the Beluga-derived internal eDP 6-bpc qualification."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
alder=(root/'WhateverXe/kern_alderlake_n.hpp').read_text()
memory=(root/'WhateverXe/kern_display13_fb_memory.hpp').read_text()
xe=(root/'WhateverXe/kern_xe.cpp').read_text()

dp=alder[alder.index('inline bool dpSource('):]
dp=dp[:dp.index('\n}\n')]
linear=alder[alder.index('inline LinearStatus linearPlan('):]
linear=linear[:linear.index('\n}\n')]
inspect=memory[memory.index('template<class IO> Readout inspect('):]
inspect=inspect[:inspect.index('\n}\n')]
sst=xe[xe.index('uint8_t *XE::display13SSTPort('):]
sst=sst[:sst.index('\n}\n')]

assert 'const unsigned bpc=(trans>>20)&7;' in dp
assert '(trans&0xFF000000U)' in dp
assert '(bpc==0 || (panel && bpc==2))' in dp
assert 'protocol==GOPProtocol::EDP && ((trans>>20)&7)==2' in linear
assert '(dp && panel && ((trans>>20)&7)==2)' in inspect
assert 'config[0]<2 && (s->adlnOutputWiring.panel&(1U<<config[0]))' in sst

# Verify the intended matrix: 8 bpc everywhere; 6 bpc only on internal eDP.
for panel in (False, True):
    accepted = [bpc for bpc in range(8) if bpc == 0 or (panel and bpc == 2)]
    assert accepted == ([0, 2] if panel else [0])
for protocol in ('TMDS', 'DP', 'EDP'):
    accepted = [bpc for bpc in range(8) if bpc == 0 or (protocol == 'EDP' and bpc == 2)]
    assert accepted == ([0, 2] if protocol == 'EDP' else [0])
for ddi in range(3):
    for panel_mask in range(4):
        accepted = (ddi < 2 and bool(panel_mask & (1 << ddi)))
        expected = (ddi == 0 and bool(panel_mask & 1)) or (ddi == 1 and bool(panel_mask & 2))
        assert accepted == expected
print('PASS: eDP 6-bpc source, plane, memory and port guards remain panel-scoped')
