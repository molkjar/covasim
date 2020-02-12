'''
Test that the parameters and data files are being created correctly.
'''

import pytest
import sciris as sc
from covid_abm import parameters as cov_pars

def test_parameters():
    sc.heading('Testing the parameters')
    pars = cov_pars.make_pars()
    sc.pp(pars)
    return pars

def test_data():
    sc.heading('Testing data loading')
    data = cov_pars.load_data()
    sc.pp(data)
    
    # Check that it is looking for the right file
    with pytest.raises(FileNotFoundError):
        data = cov_pars.load_data(filename='file_not_found.csv')
    
    return data

if __name__ == '__main__':
    sc.tic()
    pars = test_parameters()
    data = test_data()
    sc.toc()

print('Done.')