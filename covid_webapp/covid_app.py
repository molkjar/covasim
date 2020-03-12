'''
Sciris app to run the web interface.
'''

# Imports
import os
import sys
import mpld3
import sciris as sc
import scirisweb as sw
import covid_webapp as cw # Short for "Covid webapp model"

# Change to current folder and create the app
app = sw.ScirisApp(__name__, name="Covid-ABM")
app.sessions = dict() # For storing user data
flask_app = app.flask_app

#%% Define the API

@app.register_RPC()
def get_defaults():
    ''' Get parameter defaults '''

    max_pop = 1e5
    max_days = 365

    sim_pars = {}
    sim_pars['scale']            = {'best':100,  'min':1,   'max':1e9,      'name':'Population scale factor'}
    sim_pars['n']                = {'best':35000,'min':1,   'max':max_pop,  'name':'Population size'}
    sim_pars['n_infected']       = {'best':20,   'min':1,   'max':max_pop,  'name':'Initial infections'}
    sim_pars['n_days']           = {'best':60,   'min':1,   'max':max_days, 'name':'Duration (days)'}
    sim_pars['intervene']        = {'best':30,   'min':-1,  'max':max_days, 'name':'Intervention start (day)'}
    sim_pars['unintervene']      = {'best':44,   'min':-1,  'max':max_days, 'name':'Intervention end (day)'}
    sim_pars['intervention_eff'] = {'best':0.9,  'min':0.0, 'max':1.0,      'name':'Intervention effectiveness'}
    sim_pars['seed']             = {'best':1,    'min':1,   'max':1e9,      'name':'Random seed'}

    epi_pars = {}
    epi_pars['r0']        = {'best':2.0,  'min':0.0, 'max':5.0, 'name':'R0 (infectiousness)'}
    epi_pars['contacts']  = {'best':20,   'min':0.0, 'max':100, 'name':'Number of contacts'}
    epi_pars['incub']     = {'best':5.0,  'min':1.0, 'max':30,  'name':'Incubation period (days)'}
    epi_pars['incub_std'] = {'best':1.0,  'min':0.0, 'max':30,  'name':'Incubation variability (days)'}
    epi_pars['dur']       = {'best':8.0,  'min':1.0, 'max':30,  'name':'Infection duration (days)'}
    epi_pars['dur_std']   = {'best':2.0,  'min':0.0, 'max':30,  'name':'Infection variability (days)'}
    epi_pars['cfr']       = {'best':0.02, 'min':0.0, 'max':1.0, 'name':'Case fatality rate'}
    epi_pars['timetodie'] = {'best':22.0, 'min':1.0, 'max':60,  'name':'Days until death'}

    output = {'sim_pars': sim_pars, 'epi_pars': epi_pars}
    return output


@app.register_RPC()
def get_version():
    ''' Get the version '''
    output = f'{cw.__version__} ({cw.__versiondate__})'
    return output


@app.register_RPC()
def get_sessions(session_id=None):
    ''' Get the sessions '''
    try:
        session_list = app.sessions.keys()
        if not session_id:
            session_id = len(session_list)+1
            session_list.append(session_id)
            app.sessions[str(session_id)] = sc.objdict()
            print(f'Created session {session_id}')
        output = {'session_id':session_id, 'session_list':session_list, 'err':''}
    except Exception as E:
        err = f'Session retrieval failed! ({str(E)})'
        print(err)
        output = {'session_id':1, 'session_list':[1], 'err':err}
    return output


@app.register_RPC()
def plot_sim(sim_pars=None, epi_pars=None, verbose=True):
    ''' Create, run, and plot everything '''

    err = ''

    try:
        # Fix up things that JavaScript mangles
        sim_pars = sc.odict(sim_pars)
        epi_pars = sc.odict(epi_pars)
        pars = {}
        pars['verbose'] = verbose # Control verbosity here
        for key,entry in sim_pars.items() + epi_pars.items():
            pars[key] = float(entry['best'])
    except Exception as E:
        err1 = f'Parameter conversion failed! {str(E)}'
        print(err1)
        err += err1

    # Handle sessions
    sim = cw.Sim()
    sim.update_pars(pars=pars)

    if verbose:
        print('Input parameters:')
        print(pars)

    # Core algorithm
    try:
        sim.run(do_plot=False)
    except Exception as E:
        err3 = f'Sim run failed! ({str(E)})'
        print(err3)
        err += err3

    # Plotting
    try:
        fig_args = {'figsize':(8,9)}
        axis_args = {'left':0.15, 'bottom':0.1, 'right':0.9, 'top':0.95, 'wspace':0.2, 'hspace':0.25}
        kwargs = dict(fig_args=fig_args, axis_args=axis_args, font_size=12, use_grid=False)
        fig = sim.plot(**kwargs) # Plot the sim
        mpld3.plugins.connect(fig, mpld3.plugins.MousePosition(fontsize=12, fmt='.4r')) # Add data cursor
        graphjson = sw.mpld3ify(fig, jsonify=False)  # Convert to dict
    except Exception as E:
        err4 = f'Plotting failed!  ({str(E)})'
        print(err4)
        err += err4
        graphjson ={}# {'err':err}

    return {'graph':graphjson, 'err':err}  # Return the JSON representation of the Matplotlib figure



#%% Run the server
if __name__ == "__main__":

    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    if len(sys.argv) > 1:
        app.config['SERVER_PORT'] = int(sys.argv[1])
    else:
        app.config['SERVER_PORT'] = 8188
    if len(sys.argv) > 2:
        autoreload = int(sys.argv[2])
    else:
        autoreload = 1

    app.run(autoreload=True)