import psi4

global molecularBuffer
global gridDensity
global radii
global vdwScaling
global radiiScaling

psi4.set_memory('48GB')
psi4.set_num_threads(32)
psi4.core.set_output_file('Psi4.log', True)

chargeTheory = "MULLIKEN_CHARGES" # partial charge method only
theory = 'm06-2x'
logfile = 'miniFMO.log'
FMOEConvTol = 1e-9 # How tight should the FMO1 procedures try to converge to 
FMOQConvTol = 1e-12 # How tight should the FMO1 procedures try to converge to 
molecularBuffer = 100 # How many Åe+1 larger than the molecule should the point generation box be
gridDensity = 3 # How many Åe-1 between each grid point. CHELPG suggests 3-8 (0.3-0.8Å)
radii = 2.8 # The outer limit of the point cloud for each atom. 2.8 is the CHELPG default
vdwScaling = 1.0 # the factor by which to multiply the vdw radii by for the ESP cutoff. CHELPG uses 1.2
radiiScaling = 2.0

psi4.set_options({
    'basis': '6-31+G*',
    'scf_type': 'df',
    'dft_spherical_points': 590,
    'dft_radial_points': 99,
})

fragGeomList = ["""
0 1
H     25.904390   27.848220   23.245700
C     26.470510   27.902150   24.163850
C     25.927170   28.660700   25.265740
C     27.751410   27.354020   24.324460
H     24.937600   29.074340   25.139050
C     26.729710   28.931990   26.356300
H     28.185700   26.797340   23.507210
C     28.398860   27.482910   25.547670
H     26.198040   29.520580   27.089300
C     27.966830   28.300910   26.608940
H     29.350290   26.976460   25.616150
C     28.440660   28.528530   27.939860
C     29.648020   27.796620   28.338100
H     27.846560   29.178710   28.564930
C     30.217500   27.842830   29.667880
H     30.205080   27.219820   27.614650
C     29.664900   28.783210   30.746270
O     31.020870   27.028720   30.019350
C     28.549890   28.376020   31.525920
C     30.174050   30.078760   30.911010
H     28.085440   27.402110   31.479150
C     27.834070   29.321180   32.320740
N     31.328500   30.526690   30.384250
C     29.488230   30.982450   31.737720
H     26.890930   29.057520   32.776110
C     28.284440   30.641330   32.415620
H     31.367190   31.477100   30.044640
H     31.609700   30.069330   29.528770
H     29.800690   31.993900   31.951620
H     27.577720   31.313980   32.878760
""", """
1 1
N     31.653600   26.758130   33.903150
C     30.881120   25.759630   33.135450
C     30.665740   27.295740   34.845820
C     29.824920   25.169710   34.059840
C     29.671140   26.144090   35.167120
C     32.678690   26.069910   34.589330
C     32.295760   27.800410   33.015230
H     31.459060   25.016470   32.586090
H     30.423510   26.405690   32.386250
H     31.077290   27.791250   35.725140
H     30.068760   28.090760   34.398980
H     30.186060   24.238930   34.497250
H     28.907800   25.076670   33.478180
H     29.851120   25.705750   36.148730
H     28.682850   26.603090   35.193570
H     32.296190   25.306480   35.266800
H     33.228390   25.597470   33.775250
H     33.286820   26.763930   35.169520
H     32.847190   27.275340   32.235270
H     31.495290   28.324630   32.493180
C     33.185780   28.900880   33.722480
H     34.036870   28.567460   34.316270
H     32.584810   29.454500   34.443900
C     33.762770   29.801160   32.664250
H     33.034970   30.327560   32.046750
H     34.184520   29.087500   31.956500
C     34.844940   30.832950   33.228910
H     34.510960   31.651970   33.865900
H     35.377560   31.381890   32.452330
H     35.574120   30.274730   33.816110
""", """
1 1
N     24.343380   26.585780   28.336450
C     23.716990   25.689870   29.267680
C     25.797200   26.362130   28.301590
C     24.522630   24.326930   28.996910
C     25.821240   24.785540   28.423490
C     23.840610   26.342190   26.996640
C     24.016480   28.009520   28.661010
H     22.660970   25.424660   29.318680
H     23.998200   26.153390   30.213280
H     26.336940   26.640390   27.396400
H     26.371130   26.784850   29.126220
H     23.919800   23.711150   28.329440
H     24.611770   23.765400   29.926870
H     26.039050   24.302020   27.471190
H     26.614520   24.312340   29.002180
H     24.019890   27.069270   26.204600
H     24.166510   25.428830   26.498990
H     22.754240   26.295190   26.921220
H     24.575240   28.110220   29.591470
H     24.405950   28.766750   27.980550
C     22.518790   28.368590   28.992020
H     22.032320   27.643340   29.644290
H     21.964520   28.616880   28.086900
C     22.219640   29.706960   29.751320
H     21.312840   30.226240   29.441230
H     23.019330   30.419160   29.547930
C     22.280410   29.478840   31.294270
H     23.232190   29.140330   31.703680
H     21.611330   28.655560   31.544560
H     21.952320   30.382720   31.807550
""", """
1 1
N     27.991300   34.117760   28.551900
C     26.549730   34.180120   28.228050
C     27.950540   33.129620   29.674730
C     25.854740   32.813990   28.401850
C     26.893250   32.003780   29.211530
C     28.669480   33.522560   27.434680
C     28.600120   35.406930   28.864820
H     26.258490   34.473910   27.219600
H     26.133440   34.892260   28.940550
H     28.924250   32.683400   29.876940
H     27.670400   33.631060   30.601110
H     25.488060   32.372910   27.474970
H     25.065370   32.948310   29.141410
H     27.434870   31.304920   28.574090
H     26.313190   31.582940   30.032830
H     28.355410   32.560970   27.028710
H     28.619610   34.208850   26.589330
H     29.735490   33.369500   27.602870
H     29.594710   35.158200   29.235030
H     28.815750   35.991400   27.970400
C     28.060590   36.358510   30.001250
H     28.280780   35.914710   30.972160
H     26.994260   36.546940   29.876630
C     28.739510   37.746720   29.981760
H     28.971000   38.301880   29.072740
H     29.765650   37.570970   30.304640
C     28.166780   38.728820   30.924480
H     27.150700   39.003290   30.641010
H     28.701310   39.678670   30.937010
H     28.058600   38.387860   31.954110
""", """
1 1
N     32.788520   22.641920   28.746750
C     33.449180   21.678460   29.629060
C     32.028460   21.763600   27.825200
C     33.653890   20.430780   28.839320
C     32.898940   20.472720   27.518820
C     31.918400   23.550990   29.564750
C     33.886040   23.444230   28.084230
H     32.873110   21.429350   30.520230
H     34.412260   22.009610   30.017520
H     30.998630   21.643090   28.161400
H     31.967590   22.149530   26.807630
H     33.584320   19.489470   29.384490
H     34.724600   20.463300   28.637750
H     32.293950   19.613940   27.227990
H     33.695030   20.520500   26.775810
H     31.216820   22.999190   30.190370
H     32.401520   24.261520   30.235450
H     31.230740   24.078360   28.903610
H     34.582440   23.828780   28.829380
H     34.551280   22.769670   27.545230
C     33.433630   24.685300   27.235120
H     32.583440   25.242000   27.629270
H     33.003430   24.389570   26.278270
C     34.484340   25.690400   26.715430
H     34.013230   26.314740   25.956250
H     35.323230   25.210880   26.211010
C     35.042910   26.764750   27.651620
H     34.190990   27.401010   27.891430
H     35.707570   27.443550   27.117240
H     35.445970   26.426700   28.606280
""", """
1 1
N     27.626540   20.107930   28.004810
C     27.915370   21.566160   28.082170
C     28.838940   19.586040   28.647210
C     28.433110   21.824980   29.493350
C     29.029610   20.503720   29.919870
C     26.358010   19.802030   28.708190
C     27.557540   19.573670   26.647710
H     26.967070   22.056810   27.862880
H     28.670070   21.921200   27.380400
H     28.818510   18.552890   28.994030
H     29.729650   19.640380   28.021290
H     27.732970   22.202050   30.238820
H     29.147370   22.647770   29.524040
H     28.537620   20.163600   30.831110
H     30.086480   20.457980   30.182620
H     26.246680   18.723810   28.822890
H     26.301400   20.154080   29.738220
H     25.386170   20.048020   28.280270
H     26.737200   20.083910   26.142950
H     28.467780   19.850460   26.115780
C     27.161660   18.164840   26.497230
H     26.976430   17.968970   25.441090
H     26.213260   17.825080   26.913420
C     28.199620   17.057440   26.840150
H     28.205130   16.942090   27.924020
H     29.227270   17.266940   26.543260
C     27.723700   15.669960   26.508140
H     28.336580   14.938930   27.035470
H     27.835990   15.465530   25.443390
H     26.667940   15.449460   26.665770
""", """
-1 1
H     33.548600   32.698470   31.462530
C     32.934890   33.414540   30.915970
O     32.636310   34.502570   31.855150
H     33.332770   33.811660   29.982110
H     32.041310   32.957920   30.490410
S     31.405200   35.420480   31.532410
O     31.700580   35.925130   30.226620
O     31.337720   36.409520   32.603610
O     30.237930   34.564350   31.536320
""", """
-1 1
H     21.932510   31.993610   27.981570
C     22.163180   31.538350   27.018440
O     21.804700   32.396220   25.899080
H     23.238510   31.361830   26.993510
H     21.798260   30.513440   26.951520
S     22.257250   33.978520   26.064960
O     21.982180   34.647440   24.758820
O     23.692960   33.939220   26.308390
O     21.465970   34.462610   27.173890
""", """
-1 1
H     26.882630   23.623530   34.719120
C     26.527710   23.509110   33.694890
O     25.500510   24.475750   33.543540
H     27.359250   23.605270   32.996750
H     26.187910   22.473710   33.670790
S     25.825780   25.784280   32.589540
O     26.694750   26.593170   33.443950
O     24.565370   26.458190   32.337000
O     26.483890   25.323090   31.332180
""", """
-1 1
H     28.323690   30.093580   23.420560
C     28.516410   31.005800   23.985210
O     29.417220   31.876860   23.177990
H     27.586560   31.512670   24.243220
H     29.001850   30.977170   24.960720
S     29.351310   32.062490   21.634670
O     30.265740   33.086630   21.344980
O     27.931000   32.410850   21.366160
O     29.775920   30.802490   21.136570
""", """
-1 1
H     32.274350   28.004050   26.320240
C     31.678800   28.618880   25.645400
O     31.263410   29.857650   26.167110
H     32.255580   28.690170   24.723260
H     30.818430   28.042930   25.304590
S     32.233600   30.508200   27.306130
O     32.234090   29.517840   28.397980
O     31.568740   31.749800   27.611320
O     33.551100   30.765650   26.689520
"""]