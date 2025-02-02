# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 12:46:18 2018

@author: hcji
"""

import os
import numpy as np
from jpype import isJVMStarted, startJVM, getDefaultJVMPath, JPackage
import PyFingerprint

if not isJVMStarted():
    cdk_path = os.path.join(PyFingerprint.__path__[0], 'CDK', 'cdk-2.2.jar')
    startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % cdk_path)
    cdk = JPackage('org').openscience.cdk
    

sp = cdk.smiles.SmilesParser(cdk.DefaultChemObjectBuilder.getInstance())
def cdk_parser_smiles(smi):
    try:
        mol = sp.parseSmiles(smi)
    except:
        raise IOError('invalid smiles input')
    return mol

fp_map  = {}

def get_fingerprinter(name, size, depth): 
    ### This was getting made every time!
    _fingerprinters = {"daylight":lambda : cdk.fingerprint.Fingerprinter(size, depth)
                       , "extended":lambda : cdk.fingerprint.ExtendedFingerprinter(size, depth)
                       , "graph":lambda : cdk.fingerprint.GraphOnlyFingerprinter(size, depth)
                       , "maccs":lambda : cdk.fingerprint.MACCSFingerprinter()
                       , "pubchem":lambda : cdk.fingerprint.PubchemFingerprinter(cdk.silent.SilentChemObjectBuilder.getInstance())
                       , "estate":lambda : cdk.fingerprint.EStateFingerprinter()
                       , "hybridization":lambda : cdk.fingerprint.HybridizationFingerprinter(size, depth)
                       , "lingo":lambda : cdk.fingerprint.LingoFingerprinter(depth)
                       , "klekota-roth":lambda : cdk.fingerprint.KlekotaRothFingerprinter()
                       , "shortestpath":lambda : cdk.fingerprint.ShortestPathFingerprinter(size)
                       , "signature": lambda : cdk.fingerprint.SignatureFingerprinter(depth)
                       , "circular": lambda : cdk.fingerprint.CircularFingerprinter()
                       , "cdk": lambda : cdk.fingerprint.SubstructureFingerprinter()
                            }
    if name not in _fingerprinters: 
        raise IOError('invalid fingerprint type')

    return _fingerprinters[name]()

def cdk_fingerprint(smi, fp_type="daylight", size=1024, depth=6, output='bit'):
    if fp_type == 'maccs':
        nbit = 166
    elif fp_type == 'estate':
        nbit = 79
    elif fp_type == 'cdk':
        nbit = 307
    elif fp_type == 'pubchem':
        nbit = 881
    elif fp_type == 'klekota-roth':
        nbit = 4860
    else:
        nbit = size

    mol = cdk_parser_smiles(smi)

    # Pull from cache if it exists
    if (fp_type, size, depth) in fp_map: 
        fingerprinter = fp_map[(fp_type, size, depth)]
    else:
        fingerprinter = get_fingerprinter(fp_type, size, depth)
        fp_map[(fp_type, size, depth)] = fingerprinter

    fp_obj = fingerprinter.getBitFingerprint(mol)
    bits = np.array(fp_obj.getSetbits())
    if output == 'bit':
        return bits
    else:  
        vec = np.zeros(nbit, dtype=np.uint8)
        vec[bits] = 1
        return vec

def cdk_fingerprints(smis, fp_type="daylight", size=1024, depth=6, output='bit'):
    if fp_type == 'maccs':
        nbit = 166
    elif fp_type == 'estate':
        nbit = 79
    elif fp_type == 'cdk':
        nbit = 307
    elif fp_type == 'pubchem':
        nbit = 881
    elif fp_type == 'klekota-roth':
        nbit = 4860
    else:
        nbit = size

    _fingerprinters = {"daylight":lambda : cdk.fingerprint.Fingerprinter(size, depth)
                       , "extended":lambda : cdk.fingerprint.ExtendedFingerprinter(size, depth)
                       , "graph":lambda : cdk.fingerprint.GraphOnlyFingerprinter(size, depth)
                       , "maccs":lambda : cdk.fingerprint.MACCSFingerprinter()
                       , "pubchem":lambda : cdk.fingerprint.PubchemFingerprinter(cdk.silent.SilentChemObjectBuilder.getInstance())
                       , "estate":lambda : cdk.fingerprint.EStateFingerprinter()
                       , "hybridization":lambda : cdk.fingerprint.HybridizationFingerprinter(size, depth)
                       , "lingo":lambda : cdk.fingerprint.LingoFingerprinter(depth)
                       , "klekota-roth":lambda : cdk.fingerprint.KlekotaRothFingerprinter()
                       , "shortestpath":lambda : cdk.fingerprint.ShortestPathFingerprinter(size)
                       , "signature": lambda : cdk.fingerprint.SignatureFingerprinter(depth)
                       , "circular": lambda : cdk.fingerprint.CircularFingerprinter()
                       , "cdk": lambda : cdk.fingerprint.SubstructureFingerprinter()
                            }
    if fp_type not in _fingerprinters: 
        raise IOError('invalid fingerprint type')

    fingerprinter = _fingerprinters[fp_type]()

    output_list = []
    for smi in smis: 
        mol = cdk_parser_smiles(smi)
        fp_obj = fingerprinter.getBitFingerprint(mol)
        bits = np.array(fp_obj.getSetbits())
        if output == 'bit':
            output_list.append(bits)
        else:  
            vec = np.zeros(nbit, dtype=np.uint8)
            vec[bits] = 1
            output_list.append(vec)
    return output_list
