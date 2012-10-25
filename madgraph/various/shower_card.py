################################################################################
#
# Copyright (c) 2011 The MadGraph Development team and Contributors
#
# This file is a part of the MadGraph 5 project, an application which 
# automatically generates Feynman diagrams and matrix elements for arbitrary
# high-energy processes in the Standard Model and beyond.
#
# It is subject to the MadGraph license which should accompany this 
# distribution.
#
# For more information, please visit: http://madgraph.phys.ucl.ac.be
#
################################################################################
"""A File for splitting"""

import sys
import re
import os

pjoin = os.path.join

class ShowerCardError(Exception):
    pass

class ShowerCard(dict):
    """ """
    true = ['.true.', 't', 'true', '1']
    false = ['.false.', 'f', 'false', '0']
    logical_vars = ['ue_enabled', 'hadronize', 'b_stable', 'pi_stable', 'wp_stable', 
                    'wm_stable', 'z_stable', 'h_stable', 'tap_stable', 'tam_stable', 
                    'mup_stable', 'mum_stable', 'is_4lep', 'is_bbar']
    path_vars = ['hwpppath', 'thepegpath', 'hepmcpath']
    string_vars = ['extralibs', 'extrapaths', 'includepaths', 'analyse']
    int_vars = ['maxprint','nevents','rnd_seed', 'rnd_seed2', 'modbos_1', 'modbos_2']
    float_vars = ['maxerrs', 'lambda_5']

    # names_dict has the following structure:
    # var : {PYTHIA6: varpy6, HERWIG6: varhw6, HERWIGPP: varhwpp}
    # where varpy, varhw6 and varhwpp are mc_dependent names
    # if a mc is not there, that variable is not supposed to be
    # used / written for thar mc
    names_dict = {\
            'ue_enabled' : {'HERWIG6':'lhsoft', 'PYTHIA6': 'mstp_81', 'HERWIGPP': 'ue_hwpp'},
            'nevents' : {'HERWIG6':'nevents', 'PYTHIA6': 'nevents', 'HERWIGPP': 'nevents'},
            'hadronize' : {'PYTHIA6': 'mstp_111', 'HERWIGPP': 'hadronize_hwpp'},
            'b_stable' : {'HERWIG6':'b_stable_hw', 'PYTHIA6': 'b_stable_py', 'HERWIGPP': 'b_stable_hwpp'},
            'pi_stable' : {'HERWIG6':'pi_stable_hw', 'PYTHIA6': 'pi_stable_py', 'HERWIGPP': 'pi_stable_hwpp'},
            'wp_stable' : {'HERWIG6':'wp_stable_hw', 'PYTHIA6': 'wp_stable_py', 'HERWIGPP': 'wp_stable_hwpp'},
            'wm_stable' : {'HERWIG6':'wm_stable_hw', 'PYTHIA6': 'wm_stable_py', 'HERWIGPP': 'wm_stable_hwpp'},
            'z_stable' : {'HERWIG6':'z_stable_hw', 'PYTHIA6': 'z_stable_py', 'HERWIGPP': 'z_stable_hwpp'},
            'h_stable' : {'HERWIG6':'h_stable_hw', 'PYTHIA6': 'h_stable_py', 'HERWIGPP': 'h_stable_hwpp'},
            'tap_stable' : {'HERWIG6':'taup_stable_hw', 'PYTHIA6': 'taup_stable_py', 'HERWIGPP': 'taup_stable_hwpp'},
            'tam_stable' : {'HERWIG6':'taum_stable_hw', 'PYTHIA6': 'taum_stable_py', 'HERWIGPP': 'taum_stable_hwpp'},
            'mup_stable' : {'HERWIG6':'mup_stable_hw', 'PYTHIA6': 'mup_stable_py', 'HERWIGPP': 'mup_stable_hwpp'},
            'mum_stable' : {'HERWIG6':'mum_stable_hw', 'PYTHIA6': 'mum_stable_py', 'HERWIGPP': 'mum_stable_hwpp'},
            'is_4lep' : {'PYTHIA6':'is_4l_py'},
            'is_bbar' : {'HERWIG6':'is_bb_hw'},
            'maxprint' : {'HERWIG6':'maxpr_hw', 'PYTHIA6': 'maxpr_py', 'HERWIGPP': 'maxpr_hwpp'},
            'rnd_seed' : {'HERWIG6':'rndevseed1_hw', 'PYTHIA6': 'rndevseed_py', 'HERWIGPP': 'rndevseed_hwpp'},
            'rnd_seed2' : {'HERWIG6':'rndevseed2_hw'},
            'modbos_1' : {'HERWIG6':'modbos_1'},
            'modbos_2' : {'HERWIG6':'modbos_2'},
            'maxerrs' : {'HERWIG6':'err_fr_hw', 'PYTHIA6': 'err_fr_py', 'HERWIGPP': 'err_fr_hwpp'},
            'lambda_5' : {'HERWIG6':'lambdaherw', 'PYTHIA6': 'lambdapyth'},
            'analyse' : {'HERWIG6':'hwuti', 'PYTHIA6':'pyuti', 'HERWIGPP':'hwpputi'}}
    stdhep_dict = {'HERWIG6':'mcatnlo_hwan_stdhep.o', 'PYTHIA6':'mcatnlo_pyan_stdhep.o'}
    
    def __init__(self, card=None, testing=False):
        """ if testing, card is the content"""
        self.testing = testing
        dict.__init__(self)
        self.keylist = self.keys()
            
        if card:
            self.read_card(card)

    
    def read_card(self, card_path):
        """read the shower_card, if testing card_path is the content"""
        if not self.testing:
            content = open(card_path).read()
        else:
            content = card_path
        lines = [l for l in content.split('\n') \
                    if '=' in l and not l.startswith('#')] 
        for l in lines:
            args =  l.split('#')[0].split('=')
            key = args[0].strip().lower()
            value = args[1].strip()
            #key
            if key in self.logical_vars:
                if value.lower() in self.true:
                    self[key] = True
                elif value.lower() in self.false:
                    self[key] = False
                else:
                    raise ShowerCardError('%s is not a valid value for %s' % \
                            (value, key))
            elif key in self.path_vars:
                if os.path.isdir(value):
                    self[key] = value
                elif value.lower() == 'none':
                    self[key] = None
                else:
                    raise ShowerCardError('%s is not a valid directory' % \
                            (value))
            elif key in self.string_vars:
                self[key] = value
            elif key in self.int_vars:
                try:
                    self[key] = int(value)
                except ValueError:
                    raise ShowerCardError('%s is not a valid value for %s. An integer number is expected' % \
                            (key, value))
            elif key in self.float_vars:
                try:
                    self[key] = float(value)
                except ValueError:
                    raise ShowerCardError('%s is not a valid value for %s. A floating point number is expected' % \
                            (key, value))
            else:
                raise ShowerCardError('Unknown entry: %s = %s' % (key, value))
            self.keylist.append(key)



    def write_card(self, shower, card_path):
        """write the shower_card for shower in card_path.
        if self.testing, card_path takes the value of the string"""

        if shower.startswith('PYTHIA6'):
            self.shower = 'PYTHIA6'
        else:
            self.shower = shower
        lines = []
        bool_dict = {True: '.true.', False: '.false.'}
        bool_dict_num = {True: '1', False: '0'}
        for key in self.keylist:
            value = self[key]
            if key in self.logical_vars:
                # deal with special case for pythia:
                if key in ['ue_enabled', 'hadronize'] and self.shower == 'PYTHIA6':
                    value = bool_dict_num[value]
                else:
                    value = bool_dict[value]
            elif key in self.path_vars or key in self.string_vars:
                # deal in a special way with analyse
                if key == 'analyse':
                    if value is None or not value:
                        try:
                            value = self.stdhep_dict[self.shower]
                        except KeyError:
                            pass
                    try:
                        line = '%s="%s"' % (self.names_dict[key][self.shower].upper(), value)
                        lines.append(line)
                        continue
                    except KeyError:
                        continue
                if value is None or not value:
                    value = ''
                else:
                    value = '"%s"' % value

                line = '%s=%s' % (key.upper(), value)
                lines.append(line)
                continue
            elif key in self.int_vars:
                value = '%d' % value
            elif key in self.float_vars:
                value = '%4.3f' % value
            else:
                raise ShowerCardError('Unknown key: %s = %s' % (key, value))
            try:
                line = '%s=%s' % (self.names_dict[key][self.shower].upper(), value.upper())
                lines.append(line)
            except KeyError:
                pass

        if self.testing:
            return ('\n'.join(lines) + '\n')
        else:
            open(card_path, 'w').write(('\n'.join(lines) + '\n'))
