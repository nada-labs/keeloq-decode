#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr

class keeloq_dec_bb(gr.basic_block):
    """
    Decodes Keeloq transmissions

    Excpects the input to be preceeded by a digital_correlate_access_code_bb_0
    block set to 101010101010101010101010000000000, the preamble.

    Data is expected to be coming in at the rate of 1 sample per symbol, where
    a symbol is one timing unit.

    Outputs 7 bytes of packed, decoded data, if valid.
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="keeloq_dec_bb",
            in_sig=[numpy.int8],
            out_sig=[numpy.int8])
        self.state = 0
        self.sym_count = 0
        self.bit_count = 0
        self.byte = 0
        self.sym = 0
        self.packet = []

    def forecast(self, noutput_items, ninput_items_required):
        #setup size of input_items[i] for work call
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def general_work(self, input_items, output_items):
        out0 = output_items[0]
        in0 = input_items[0]
        processed = 0

        for sym in in0:
            if self.state == 0 and sym == 3:
                #found the first symbol after the preamble
                #move to the next state AND FALL THROUGH
                self.state = 1
            if self.state == 1:
                #shift in the bit
                self.sym = (self.sym << 1) | (sym & 0x01)
                self.sym_count += 1

                #have we decoded a full bit?
                if self.sym_count == 3:
                    self.sym_count = 0

                    dec_bit = None
                    if self.sym == 0b110:
                        #'0' bit
                        dec_bit = 0
                    elif self.sym == 0b100:
                        #'1' bit
                        dec_bit = 1
                    else:
                        #decoding error. reset state and break out of loop
                        self.reset_state()
                        break

                    #store the bit LSB first and reset the symbol
                    self.byte = self.byte | (dec_bit << (self.bit_count &
                                                         0x07))
                    self.bit_count += 1
                    self.sym = 0

                    # do we need to store the byte?
                    if self.bit_count % 8 == 0:
                        self.packet.append(self.byte)
                        self.byte = 0
                    elif self.bit_count == 66:
                        #we're done receiving, append last byte
                        self.packet.append(self.byte)
                        #output the decoded data.
                        for i in range(len(self.packet)):
                            out0[i] = self.packet[i]
                        processed = len(self.packet)

                        self.reset_state()

        self.consume(0, len(input_items[0]))
        return processed

    def reset_state(self):
        self.state = 0
        self.sym_count = 0
        self.bit_count = 0
        self.byte = 0
        self.sym = 0
        self.packet = []

    def setup(self):
        gr.basic_block.setup(self)
        self.reset_state()

