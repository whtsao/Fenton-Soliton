"""
Walkley 1999 experiment: a solitary wave reflection after a runup on slope
"""
from proteus import Domain, Context
from proteus.mprans import SpatialTools as st
from proteus import WaveTools as wt
from math import *
import numpy as np

#---tsao add---#
#import proteus.TwoPhaseFlow.TwoPhaseFlowProblem as TpFlow

opts=Context.Options([
    # predefined test cases
    ("water_level", 0.7, "Height of free surface above seabed"),
    # tank
    ("tank_dim", (45., 1.), "Dimensions of the tank"),
    ("toe", 25., "Toe of slope"),
    ("x0", 5., "Starting place of soliatry wave"),
    ("generation", True, "Generate waves at the left boundary (True/False)"),
    ("free_slip", True, "Should tank walls have free slip conditions "
                        "(otherwise, no slip conditions will be applied)."),
    # waves
    ("waves", True, "Generate waves (True/False)"),
#    ("wave_period", 2.0, "Period of the waves"),
    ("wave_height", 0.07, "Height of the waves"),
    ("wave_depth", 0.7, "Wave depth"),
    ("wave_dir", (1.,0.,0.), "Direction of the waves (from left boundary)"),
#    ("wave_wavelength", 9.8*2.0**2/(2.0*pi), "Direction of the waves (from left boundary)"), #calculated by FFT
#    ("wave_type", 'Linear', "type of wave"),
    #("Bcoeff", np.array([0.01402408, 0.00008097, 0.00000013, 0.00000000, 0.00000000,
    #                      0.00000000, 0.00000000, 0.00000000]), "Bcoeffs"),
    #("Ycoeff", np.array([0.01246994, 0.00018698, 0.00000300, 0.00000006, 0.00000000,
    #                      0.00000000, 0.00000000, 0.00000000]), "Ycoeffs"),
    ("fast", False, "switch for fast cosh calculations in WaveTools"),
    # mesh refinement
    ("refinement", False, "Gradual refinement"),
    ("he", 0.05, "Set characteristic element size"),
    ("he_max", 10, "Set maximum characteristic element size"),
    ("he_max_water", 10, "Set maximum characteristic in water phase"),
    ("refinement_freesurface", 0.1,"Set area of constant refinement around free surface (+/- value)"),
    ("refinement_caisson", 0.,"Set area of constant refinement (Box) around caisson (+/- value)"),
    ("refinement_grading", np.sqrt(1.1*4./np.sqrt(3.))/np.sqrt(1.*4./np.sqrt(3)), "Grading of refinement/coarsening (default: 10% volume)"),
    # numerical options
    ("gen_mesh", True, "True: generate new mesh every time. False: do not generate mesh if file exists"),
    ("use_gmsh", False, "True: use Gmsh. False: use Triangle/Tetgen"),
    ("movingDomain", False, "True/False"),
    ("T", 5.0, "Simulation time"),
    ("dt_init", 0.001, "Initial time step"),
    ("dt_fixed", None, "Fixed (maximum) time step"),
    ("timeIntegration", "BackwardEuler", "Time integration scheme (backwardEuler/VBDF)"),
    ("cfl", 0.33 , "Target cfl"),
    ("nsave",  10, "Number of time steps to save per second"),   # this is the sampling rate for output
    ("useRANS", 0, "RANS model"),
    ])


# ----- CONTEXT ------ #

# tank options
waterLevel = opts.water_level
tank_dim = opts.tank_dim

# waves
#omega = 1.
if opts.waves is True:
#    period = opts.wave_period
#    omega = 2*np.pi/opts.wave_period
    height = opts.wave_height
    mwl = opts.water_level
    depth = opts.wave_depth
    direction = opts.wave_dir
    toe = opts.toe
    x0 = opts.x0
    fast = opts.fast

# generate a solitary wave
    waves = wt.SolitaryWaveFenton(waveHeight=height,
			    mwl=mwl,
                    	    depth=depth,
                   	    g=np.array([0., -9.81, 0.]),
                   	    waveDir=direction,
                            #trans = np.zeros(3,"d"),
			    trans = np.array([x0, 0., 0.]),
                    	    fast = opts.fast)

#    waves = wt.SolitaryWave(waveHeight=height,
#                            mwl=mwl,
#                            depth=depth,
#                            g=np.array([0., -9.81, 0.]),
#                            waveDir=direction,
#                            #trans = np.zeros(3,"d"),
#                            trans = np.array([x0, 0., 0.]),
#                            fast = opts.fast)

#    waves = wt.MonochromaticWaves(period=period,
#                                  waveHeight=height,
#                                  mwl=mwl,
#                                  depth=depth,
#                                  g=np.array([0., -9.81, 0.]),
#                                  waveDir=direction,
#                                  wavelength=opts.wave_wavelength,
#                                  waveType=opts.wave_type,
#                                  #Ycoeff=np.array(opts.Ycoeff),
#                                  #Bcoeff=np.array(opts.Bcoeff),
#                                  #Nf=len(opts.Bcoeff),
#                                  fast=opts.fast)
#    wavelength = waves.wavelength

# ----- DOMAIN ----- #

domain = Domain.PlanarStraightLineGraphDomain()

# refinement
he = opts.he
smoothing = he*3.

# ----- TANK ------ #

boundaryOrientations = {'y-': np.array([0., -1.,0.]),
                        'y+': np.array([0., +1.,0.]),
                        'x-': np.array([-1., 0.,0.]),
                        'x+': np.array([+1., 0.,0.]),
}

boundaryTags = {'y-': 1,
                'y+': 2,
                'x-': 3,
                'x+': 4,
}

vertices = [( 0.00, 0.00),
            (25.00, 0.00),
            (45.00, 0.40),
            (45.00, 1.00), 
            ( 0.00, 1.00)]
vertexFlags = [boundaryTags['x-'], #( 0.00, 0.00),
               boundaryTags['y-'], #( 6.00, 0.00),
               boundaryTags['y-'], #(12.00, 0.30),
               boundaryTags['y+'], #(14.00, 0.30), 
               boundaryTags['x-']]#( 0.00, 0.75)]

nVertices = len(vertices)
segments = [(i, (i+1)%nVertices) for i in range(nVertices)]
segmentFlags = [boundaryTags['y-'],
                boundaryTags['y-'],
                boundaryTags['x+'],
                boundaryTags['y+'],
                boundaryTags['x-']]

regions = [[0.1, 0.1]]

regionFlags=np.array([1])

tank = st.CustomShape(domain,
                      vertices=vertices,
                      vertexFlags=vertexFlags,
                      segments=segments,
                      segmentFlags=segmentFlags,
                      regions=regions,
                      regionFlags=regionFlags,
                      boundaryTags=boundaryTags,
                      boundaryOrientations=boundaryOrientations)

tank.facets = np.array([[[i for i in range(len(segments))]]])

# ----- GENERATION / ABSORPTION LAYERS ----- #

#dragAlpha = 10.*omega/1e-6

#if opts.generation:
#    tank.setGenerationZones(x_n=True, waves=waves, dragAlpha=dragAlpha, smoothing = smoothing)


# ----assign the velocity field to create solitary wave---- #
#toe = opts.toe

#class zero(object):
#    def uOfXT(self,x,t):
#        return 0.0

#class clsvof_init_cond(object):
#    def uOfXT(self,x,t):
#        return x[1] - (waves.eta(x,0) + opts.water_level)    

#epsFact_consrv_heaviside=3.0
#wavec =  np.sqrt(9.81 * (depth+opts.wave_height))

#def weight(x,t):
#    return 1.0-smoothedHeaviside(epsFact_consrv_heaviside*opts.he,
#                                 (x[1] - (max(waves.eta(x, t%(toe/wavec)),
#                                 waves.eta(x+toe, t%(toe/wavec)))
#                                             +opts.water_level)))
        
#class vel_u(object):
#    def uOfXT(self, x, t):
#        if x[1] <= waves.eta(x,t) + opts.water_level:
#            return weight(x,t)*waves.u(x,t)[0]
#        else:
#            return 0.0

#class vel_v(object):
#    def uOfXT(self, x, t):
#        if x[1] <= waves.eta(x,t) + opts.water_level:
#            return weight(x,t)*waves.u(x,t)[1]


# ----- BOUNDARY CONDITIONS ----- #

# Waves
#tank.BC['x-'].setUnsteadyTwoPhaseVelocityInlet(waves, smoothing=smoothing, vert_axis=1)

# apply BC on wall boundaries
tank.BC['y+'].setAtmosphere()

if opts.free_slip:
    tank.BC['y-'].setFreeSlip()
    tank.BC['x+'].setFreeSlip()
#    if not opts.generation:
    tank.BC['x-'].setFreeSlip()
else:  # no slip
    tank.BC['y-'].setNoSlip()
    tank.BC['x+'].setNoSlip()
    tank.BC['x-'].setNoSlip()



# ----- GAUGES ----- #
column_gauge_locations = (((10.0,          0.0, 0.0), (10.0, tank_dim[1], 0.0)),
                          ((25.0,          0.0, 0.0), (25.0, tank_dim[1], 0.0)),
                          ((41.25,  16.25/50.0, 0.0), (41.25, tank_dim[1], 0.0)),
                          ((42.75,  17.75/50.0, 0.0), (42.75, tank_dim[1], 0.0)),
                          ((44.99,  19.99/50.0, 0.0), (44.99, tank_dim[1], 0.0)))

tank.attachLineIntegralGauges('vof',
                              gauges=((('vof',),column_gauge_locations),),
#		              activeTime=(dt_init, T),	#--- tsao add ---#
#                	      sampleRate=dt_out,		#--- tsao add ---#
                              fileName='column_gauges.csv')

# ----- ASSEMBLE DOMAIN ----- #

domain.MeshOptions.use_gmsh = opts.use_gmsh
domain.MeshOptions.genMesh = opts.gen_mesh
domain.MeshOptions.he = he
domain.use_gmsh = opts.use_gmsh
st.assembleDomain(domain)


# ----- REFINEMENT OPTIONS ----- #

import py2gmsh
from MeshRefinement import geometry_to_gmsh
mesh = geometry_to_gmsh(domain)

field_list = []
box = 0.1001

box1 = py2gmsh.Field.Box(mesh=mesh)
box1.VIn = 0.03
box1.VOut = he
box1.XMin = 0.0
box1.XMax = tank_dim[0]
box1.YMin = waterLevel-box 
box1.YMax = waterLevel+box 
field_list += [box1]

p0 = py2gmsh.Entity.Point([0.0, waterLevel+box, 0.], mesh=mesh)
p1 = py2gmsh.Entity.Point([tank_dim[0], waterLevel+box, 0.], mesh=mesh) 
p2 = py2gmsh.Entity.Point([0.0, waterLevel-box, 0.], mesh=mesh)
p3 = py2gmsh.Entity.Point([tank_dim[0], waterLevel-box, 0.], mesh=mesh) 
l1 = py2gmsh.Entity.Line([p0, p1], mesh=mesh)
l2 = py2gmsh.Entity.Line([p2, p3], mesh=mesh)

grading = 1.05
bl2 = py2gmsh.Field.BoundaryLayer(mesh=mesh)
bl2.hwall_n = 0.03
bl2.ratio = grading
bl2.EdgesList = [l1, l2]
field_list += [bl2]


fmin = py2gmsh.Field.Min(mesh=mesh)
fmin.FieldsList = field_list
mesh.setBackgroundField(fmin)

mesh.Options.Mesh.CharacteristicLengthMax = he

domain.MeshOptions.genMesh = opts.gen_mesh
domain.MeshOptions.use_gmsh = opts.use_gmsh
domain.use_gmsh = opts.use_gmsh

geofile = 'mesh'
mesh.writeGeo(geofile+'.geo')
domain.geofile = geofile


##########################################
# Numerical Options and other parameters #
##########################################

rho_0=998.2
nu_0 =1.004e-6
rho_1=1.205
nu_1 =1.500e-5
sigma_01=0.0
g = [0., -9.81]



from math import *
from proteus import MeshTools, AuxiliaryVariables
import numpy
import proteus.MeshTools
from proteus import Domain
from proteus.Profiling import logEvent
from proteus.default_n import *
from proteus.ctransportCoefficients import smoothedHeaviside
from proteus.ctransportCoefficients import smoothedHeaviside_integral


#----------------------------------------------------
# Boundary conditions and other flags
#----------------------------------------------------
movingDomain=opts.movingDomain
checkMass=False
applyCorrection=True
applyRedistancing=True
freezeLevelSet=True

#----------------------------------------------------
# Time stepping and velocity
#----------------------------------------------------
weak_bc_penalty_constant = 100.0
dt_init = opts.dt_init
T = opts.T
nDTout = int(opts.T*opts.nsave)
timeIntegration = opts.timeIntegration
if nDTout > 0:
    dt_out= (T-dt_init)/nDTout
else:
    dt_out = 0
runCFL = opts.cfl
dt_fixed = opts.dt_fixed

#----------------------------------------------------

#  Discretization -- input options
useOldPETSc=False
useSuperlu = not True
spaceOrder = 1
useHex     = False
useRBLES   = 0.0
useMetrics = 1.0
useVF = 1.0
useOnlyVF = False
useRANS = opts.useRANS # 0 -- None
            # 1 -- K-Epsilon
            # 2 -- K-Omega, 1998
            # 3 -- K-Omega, 1988
# Input checks
if spaceOrder not in [1,2]:
    print("INVALID: spaceOrder" + spaceOrder)
    sys.exit()

if useRBLES not in [0.0, 1.0]:
    print("INVALID: useRBLES" + useRBLES)
    sys.exit()

if useMetrics not in [0.0, 1.0]:
    print("INVALID: useMetrics")
    sys.exit()

#  Discretization
nd = 2
if spaceOrder == 1:
    hFactor=1.0
    if useHex:
         basis=C0_AffineLinearOnCubeWithNodalBasis
         elementQuadrature = CubeGaussQuadrature(nd,3)
         elementBoundaryQuadrature = CubeGaussQuadrature(nd-1,3)
    else:
         basis=C0_AffineLinearOnSimplexWithNodalBasis
         elementQuadrature = SimplexGaussQuadrature(nd,3)
         elementBoundaryQuadrature = SimplexGaussQuadrature(nd-1,3)
         #elementBoundaryQuadrature = SimplexLobattoQuadrature(nd-1,1)
elif spaceOrder == 2:
    hFactor=0.5
    if useHex:
        basis=C0_AffineLagrangeOnCubeWithNodalBasis
        elementQuadrature = CubeGaussQuadrature(nd,4)
        elementBoundaryQuadrature = CubeGaussQuadrature(nd-1,4)
    else:
        basis=C0_AffineQuadraticOnSimplexWithNodalBasis
        elementQuadrature = SimplexGaussQuadrature(nd,4)
        elementBoundaryQuadrature = SimplexGaussQuadrature(nd-1,4)


# Numerical parameters
sc = 0.5 # default: 0.5. Test: 0.25
sc_beta = 1.5 # default: 1.5. Test: 1.
epsFact_consrv_diffusion = 1. # default: 1.0. Test: 0.1
ns_forceStrongDirichlet = False
backgroundDiffusionFactor=0.01
if useMetrics:
    ns_shockCapturingFactor  = sc
    ns_lag_shockCapturing = True
    ns_lag_subgridError = True
    ls_shockCapturingFactor  = sc
    ls_lag_shockCapturing = True
    ls_sc_uref  = 1.0
    ls_sc_beta  = sc_beta
    vof_shockCapturingFactor = sc
    vof_lag_shockCapturing = True
    vof_sc_uref = 1.0
    vof_sc_beta = sc_beta
    rd_shockCapturingFactor  =0.9
    rd_lag_shockCapturing = False
    epsFact_density    = 3.
    epsFact_viscosity  = epsFact_curvature  = epsFact_vof = epsFact_consrv_heaviside = epsFact_consrv_dirac = epsFact_density
    epsFact_redistance = 1.5
    epsFact_consrv_diffusion = epsFact_consrv_diffusion
    redist_Newton = True#False
    kappa_shockCapturingFactor = sc
    kappa_lag_shockCapturing = True
    kappa_sc_uref = 1.0
    kappa_sc_beta = sc_beta
    dissipation_shockCapturingFactor = sc
    dissipation_lag_shockCapturing = True
    dissipation_sc_uref = 1.0
    dissipation_sc_beta = sc_beta
else:
    ns_shockCapturingFactor  = 0.9
    ns_lag_shockCapturing = True
    ns_lag_subgridError = True
    ls_shockCapturingFactor  = 0.9
    ls_lag_shockCapturing = True
    ls_sc_uref  = 1.0
    ls_sc_beta  = 1.0
    vof_shockCapturingFactor = 0.9
    vof_lag_shockCapturing = True
    vof_sc_uref  = 1.0
    vof_sc_beta  = 1.0
    rd_shockCapturingFactor  = 0.9
    rd_lag_shockCapturing = False
    epsFact_density    = 1.5
    epsFact_viscosity  = epsFact_curvature  = epsFact_vof = epsFact_consrv_heaviside = epsFact_consrv_dirac = epsFact_density
    epsFact_redistance = 0.33
    epsFact_consrv_diffusion = 10.0
    redist_Newton = False#True
    kappa_shockCapturingFactor = 0.9
    kappa_lag_shockCapturing = True#False
    kappa_sc_uref  = 1.0
    kappa_sc_beta  = 1.0
    dissipation_shockCapturingFactor = 0.9
    dissipation_lag_shockCapturing = True#False
    dissipation_sc_uref  = 1.0
    dissipation_sc_beta  = 1.0

ns_nl_atol_res = 1e-6#max(1.0e-6,0.001*domain.MeshOptions.he**2)
vof_nl_atol_res = 1e-6#max(1.0e-6,0.001*domain.MeshOptions.he**2)
ls_nl_atol_res = 1e-6#max(1.0e-6,0.001*domain.MeshOptions.he**2)
mcorr_nl_atol_res = 1e-6#max(1.0e-6,0.0001*domain.MeshOptions.he**2)
rd_nl_atol_res = 0.1*domain.MeshOptions.he
kappa_nl_atol_res = 1e-6#max(1.0e-6,0.001*domain.MeshOptions.he**2)
dissipation_nl_atol_res = 1e-6#max(1.0e-6,0.001*domain.MeshOptions.he**2)
mesh_nl_atol_res = 1e-6#max(1.0e-6,0.001*domain.MeshOptions.he**2)
mesh.writeGeo(geofile+'.geo')

#turbulence
ns_closure=0 #1-classic smagorinsky, 2-dynamic smagorinsky, 3 -- k-epsilon, 4 -- k-omega

if useRANS == 1:
    ns_closure = 3
elif useRANS >= 2:
    ns_closure == 4

def twpflowPressure_init(x, t):
    p_L = 0.0
    phi_L = tank_dim[nd-1] - waterLevel- waves.eta(x,0)
    phi = x[nd-1] - waterLevel - waves.eta(x,0)
    return p_L -g[nd-1]*(rho_0*(phi_L - phi)+(rho_1 -rho_0)*(smoothedHeaviside_integral(epsFact_consrv_heaviside*opts.he,phi_L)
                                                         -smoothedHeaviside_integral(epsFact_consrv_heaviside*opts.he,phi)))

#def twpflowPressure_init(x, t):
#    p_L = 0.0
#    phi_L = tank_dim[nd-1] - waterLevel
#    phi = x[nd-1] - waterLevel
#    return p_L -g[nd-1]*(rho_0*(phi_L - phi)+(rho_1 -rho_0)*(smoothedHeaviside_integral(epsFact_consrv_heaviside*opts.he,phi_L)
#                                                         -smoothedHeaviside_integral(epsFact_consrv_heaviside*opts.he,phi)))
#
