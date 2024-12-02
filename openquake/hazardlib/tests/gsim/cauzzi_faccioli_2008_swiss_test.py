# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (C) 2012-2023 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.

from openquake.hazardlib.tests.gsim.utils import BaseGSIMTestCase
from openquake.hazardlib.gsim.cauzzi_faccioli_2008_swiss import (
    CauzziFaccioli2008SWISS01,
    CauzziFaccioli2008SWISS04,
    CauzziFaccioli2008SWISS08)
# Test data was prepared and provided by L. Danciu/B. Edwards


class CauzziFaccioli2008SWISS01TestCase(BaseGSIMTestCase):
    GSIM_CLASS = CauzziFaccioli2008SWISS01

    def test_all(self):
        self.check('CF08Swiss/CF08_MEAN_VsK_1.csv',
                   'CF08Swiss/cf_2008_phis_ss_embeded.csv',
                   max_discrep_percentage=0.50)


class CauzziFaccioli2008SWISS04TestCase(BaseGSIMTestCase):
    GSIM_CLASS = CauzziFaccioli2008SWISS04

    def test_all(self):
        self.check('CF08Swiss/CF08_MEAN_VsK_4.csv',
                   'CF08Swiss/cf_2008_phis_ss_embeded.csv',
                   max_discrep_percentage=0.50)


class CauzziFaccioli2008SWISS08TestCase(BaseGSIMTestCase):
    GSIM_CLASS = CauzziFaccioli2008SWISS08

    def test_all(self):
        self.check('CF08Swiss/CF08_MEAN_VsK_8.csv',
                   'CF08Swiss/cf_2008_phis_ss_embeded.csv',
                   max_discrep_percentage=0.50)