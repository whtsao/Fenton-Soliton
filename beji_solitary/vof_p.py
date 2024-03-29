from proteus.default_p import *
from proteus.ctransportCoefficients import smoothedHeaviside
from proteus.mprans import VOF
from proteus import Context
from proteus import WaveTools as wt

ct = Context.get()
domain = ct.domain
nd = domain.nd
mesh = domain.MeshOptions

genMesh = mesh.genMesh
movingDomain = ct.movingDomain
T = ct.T

# generate a solitary wave
waves = wt.SolitaryWaveFenton(waveHeight=ct.height,
			mwl=ct.mwl,
                    	depth=ct.depth,
                   	g=np.array([0., -9.81, 0.]),
                   	waveDir=ct.direction,
                        #trans = np.zeros(3,"d"),
			trans = np.array([ct.x0, 0., 0.]),
                    	fast = ct.fast)

#waves = wt.SolitaryWave(waveHeight=ct.height,
#                        mwl=ct.mwl,
#                        depth=ct.depth,
#                        g=np.array([0., -9.81, 0.]),
#                        waveDir=ct.direction,
#                        #trans = np.zeros(3,"d"),
#                        trans = np.array([ct.x0, 0., 0.]),
#                        fast = ct.fast)

LevelModelType = VOF.LevelModel
if ct.useOnlyVF:
    RD_model = None
    LS_model = None
else:
    RD_model = 3
    LS_model = 2

coefficients = VOF.Coefficients(LS_model=int(ct.movingDomain)+LS_model,
                                V_model=int(ct.movingDomain)+0,
                                RD_model=int(ct.movingDomain)+RD_model,
                                ME_model=int(ct.movingDomain)+1,
                                checkMass=True,
                                useMetrics=ct.useMetrics,
                                epsFact=ct.epsFact_vof,
                                sc_uref=ct.vof_sc_uref,
                                sc_beta=ct.vof_sc_beta,
                                movingDomain=ct.movingDomain)

dirichletConditions = {0: lambda x, flag: domain.bc[flag].vof_dirichlet.init_cython()}

advectiveFluxBoundaryConditions = {0: lambda x, flag: domain.bc[flag].vof_advective.init_cython()}

diffusiveFluxBoundaryConditions = {0: {}}

class VF_IC:
    def uOfXT(self, x, t):
        return smoothedHeaviside(ct.epsFact_consrv_heaviside*ct.opts.he,x[nd-1]-ct.waterLevel-waves.eta(x,0))

#class VF_IC:
#    def uOfXT(self, x, t):
#        return smoothedHeaviside(ct.epsFact_consrv_heaviside*ct.opts.he,x[nd-1]-ct.waterLevel)

initialConditions = {0: VF_IC()}
