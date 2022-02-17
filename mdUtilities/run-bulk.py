#!/usr/bin/env python3

import sys
import argparse
import simtk.openmm as mm
from simtk.openmm import app
import ommhelper as oh
from ommhelper.unit import *
import os

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--nstep", type=int, default=int(1e6), help="number of steps")
parser.add_argument(
    "-t", "--temp", type=float, default=333, help="temperature in Kelvin"
)
parser.add_argument("-p", "--press", type=float, default=1, help="pressure in bar")
parser.add_argument("--dt", type=float, default=0.001, help="step size in ps")
parser.add_argument(
    "--thermostat",
    type=str,
    default="langevin",
    choices=["langevin", "nose-hoover"],
    help="thermostat",
)
parser.add_argument(
    "--barostat",
    type=str,
    default="iso",
    choices=["no", "iso", "semi-iso", "xyz", "xy", "z"],
    help="barostat",
)
parser.add_argument(
    "--cos", type=float, default=0, help="cosine acceleration for viscosity calculation"
)
parser.add_argument(
    "-f", "--field", help="Electric field strength in V/nm", default=0, type=float
)
parser.add_argument("--gro", type=str, default="conf.gro", help="gro file")
parser.add_argument("--psf", type=str, default="topol.psf", help="psf file")
parser.add_argument("--prm", type=str, default="ff.prm", help="prm file")
parser.add_argument("--cpt", type=str, help="load checkpoint")
parser.add_argument(
    "-m",
    "--min",
    type=float,
    default=0,
    help="Tolerance in kJ/mol to minimize energy to before simulation",
)
args = parser.parse_args()


def gen_simulation(
    gro_file="conf.gro",
    psf_file="topol.psf",
    prm_file="ff.prm",
    dt=0.001,
    T=300,
    P=1,
    tcoupl="langevin",
    pcoupl="iso",
    cos=0,
    field=0,
    restart=None,
):
    print("Building system...")
    gro = oh.GroFile(gro_file)
    psf = oh.OplsPsfFile(psf_file, periodicBoxVectors=gro.getPeriodicBoxVectors())
    prm = app.CharmmParameterSet(prm_file)
    system = psf.createSystem(
        prm,
        nonbondedMethod=app.PME,
        nonbondedCutoff=1.2 * nm,
        constraints=app.HBonds,
        rigidWater=True,
        verbose=True,
    )
    is_drude = any(type(f) == mm.DrudeForce for f in system.getForces())

    ### apply TT damping for CLPol force field
    # donors = [atom.idx for atom in psf.atom_list if atom.attype == "HO"]
    # all HO atoms, even those with numbers after.
    # i.e. HO for choline, but also HO3 / HO5 for DHP
    donors = [
        atom.idx
        for atom in psf.atom_list
        if atom.attype.startswith("HO") or atom.attype.startswith("HW")
    ]
    if is_drude and len(donors) > 0:
        print("Add TT damping between HO/HW and Drude dipoles")
        ttforce = oh.CLPolCoulTT(system, donors)
        print(ttforce.getEnergyFunction())

    print("Initializing simulation...")
    if tcoupl == "langevin":
        if is_drude:
            print("Drude Langevin thermostat: 5.0 /ps, 20 /ps")
            integrator = mm.DrudeLangevinIntegrator(
                T * kelvin, 5.0 / ps, 1 * kelvin, 20 / ps, dt * ps
            )
            integrator.setMaxDrudeDistance(0.02 * nm)
        else:
            print("Langevin thermostat: 1.0 /ps")
            integrator = mm.LangevinIntegrator(T * kelvin, 1.0 / ps, dt * ps)
    elif tcoupl == "nose-hoover":
        if is_drude:
            print("Drude temperature-grouped Nose-Hoover thermostat: 10 /ps, 40 /ps")
        else:
            print("Nose-Hoover thermostat: 10 /ps")
        from velocityverletplugin import VVIntegrator

        print("using nose-hoover")
        integrator = VVIntegrator(T * kelvin, 10 / ps, 1 * kelvin, 40 / ps, dt * ps)
        integrator.setUseMiddleScheme(True)
        integrator.setMaxDrudeDistance(0.02 * nm)
    else:
        raise Exception("Available thermostat: langevin, nose-hoover")

    if pcoupl != "no":
        oh.apply_mc_barostat(system, pcoupl, P, T)

    if cos != 0:
        try:
            integrator.setCosAcceleration(cos)
        except:
            raise Exception("Cosine acceleration not compatible with this integrator")

    if field != 0:
        try:
            print(
                f"Electric field strength of {field} applied in the y-direction, acting on all atoms"
            )
            # apply field to all atoms
            atoms = [a.index for a in psf.topology.atoms()]
            # field applied in y-direction
            elecfield = oh.electric_field(system, atoms, [0, field, 0])
        except:
            raise Exception("Electric field cannot be used with this setup")

    _platform = mm.Platform.getPlatformByName("CUDA")
    _properties = {"CudaPrecision": "mixed"}
    sim = app.Simulation(psf.topology, system, integrator, _platform, _properties)
    if restart:
        sim.loadCheckpoint(restart)
        sim.currentStep = (
            round(sim.context.getState().getTime().value_in_unit(ps) / dt / 10) * 10
        )
        sim.context.setTime(sim.currentStep * dt)
    else:
        sim.context.setPositions(gro.positions)
        sim.context.setVelocitiesToTemperature(T * kelvin)

    # For each reporter, check if we should append to the file - allows for restart files to
    # be used in another directory
    append_dcd = "dump.dcd" in os.listdir(".")
    sim.reporters.append(
        app.DCDReporter("dump.dcd", 10000, enforcePeriodicBox=True, append=append_dcd)
    )
    sim.reporters.append(oh.CheckpointReporter("cpt.cpt", 10000))

    append_gro = "dump.gro" in os.listdir(".")
    sim.reporters.append(
        oh.GroReporter("dump.gro", 1000, logarithm=True, append=append_gro)
    )
    # if appending to dumps, also append here
    sim.reporters.append(
        oh.StateDataReporter(
            sys.stdout, 1000, box=False, volume=True, append=append_dcd
        )
    )
    if is_drude:
        append_drude = "T_drude.txt" in os.listdir(".")
        sim.reporters.append(
            oh.DrudeTemperatureReporter("T_drude.txt", 10000, append=append_drude)
        )
    if cos != 0:
        append_cos = "viscosity.txt" in os.listdir(".")
        sim.reporters.append(
            oh.ViscosityReporter("viscosity.txt", 1000, append=append_cos)
        )

    return sim


if __name__ == "__main__":
    oh.print_omm_info()
    sim = gen_simulation(
        gro_file=args.gro,
        psf_file=args.psf,
        prm_file=args.prm,
        dt=args.dt,
        T=args.temp,
        P=args.press,
        tcoupl=args.thermostat,
        pcoupl=args.barostat,
        cos=args.cos,
        restart=args.cpt,
        field=args.field,
    )

    print("Running...")
    oh.energy_decomposition(sim)
    if args.min != 0:
        oh.minimize(sim, args.min, "em.gro")
    sim.step(args.nstep)
