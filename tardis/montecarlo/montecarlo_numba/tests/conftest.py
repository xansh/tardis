from copy import deepcopy

import pytest
import numpy as np
from numba import njit

from tardis.simulation import Simulation
from tardis.montecarlo.montecarlo_numba import RPacket, PacketCollection
from tardis.montecarlo.montecarlo_numba.numba_interface import Estimators


from tardis.montecarlo.montecarlo_numba.numba_interface import (
    opacity_state_initialize,
    NumbaModel,
    Estimators,
    VPacketCollection,
)


@pytest.fixture(scope="package")
def nb_simulation_verysimple(config_verysimple, atomic_dataset):
    atomic_data = deepcopy(atomic_dataset)
    sim = Simulation.from_config(config_verysimple, atom_data=atomic_data)
    sim.iterate(10)
    return sim


@pytest.fixture(scope="package")
def verysimple_opacity_state(nb_simulation_verysimple):
    return opacity_state_initialize(
        nb_simulation_verysimple.plasma, line_interaction_type="macroatom"
    )


@pytest.fixture(scope="package")
def verysimple_numba_radial_1d_geometry(nb_simulation_verysimple):
    return nb_simulation_verysimple.model.model_state.geometry.to_numba()


@pytest.fixture(scope="package")
def verysimple_numba_model(nb_simulation_verysimple):
    model = nb_simulation_verysimple.model
    return NumbaModel(
        model.time_explosion.to("s").value,
    )


@pytest.fixture(scope="package")
def verysimple_estimators(nb_simulation_verysimple):
    transport = nb_simulation_verysimple.transport

    return Estimators(
        transport.j_estimator,
        transport.nu_bar_estimator,
        transport.j_blue_estimator,
        transport.Edotlu_estimator,
        transport.photo_ion_estimator,
        transport.stim_recomb_estimator,
        transport.bf_heating_estimator,
        transport.stim_recomb_cooling_estimator,
        transport.photo_ion_estimator_statistics,
    )


@pytest.fixture(scope="package")
def verysimple_vpacket_collection(nb_simulation_verysimple):
    spectrum_frequency = (
        nb_simulation_verysimple.transport.spectrum_frequency.value
    )
    return VPacketCollection(
        rpacket_index=0,
        spectrum_frequency=spectrum_frequency,
        number_of_vpackets=0,
        v_packet_spawn_start_frequency=0,
        v_packet_spawn_end_frequency=np.inf,
        temporary_v_packet_bins=0,
    )


@pytest.fixture(scope="package")
def verysimple_3vpacket_collection(nb_simulation_verysimple):
    spectrum_frequency = (
        nb_simulation_verysimple.transport.spectrum_frequency.value
    )
    return VPacketCollection(
        rpacket_index=0,
        spectrum_frequency=spectrum_frequency,
        number_of_vpackets=3,
        v_packet_spawn_start_frequency=0,
        v_packet_spawn_end_frequency=np.inf,
        temporary_v_packet_bins=0,
    )


@pytest.fixture(scope="package")
def verysimple_packet_collection(nb_simulation_verysimple):
    transport = nb_simulation_verysimple.transport
    return PacketCollection(
        transport.input_r,
        transport.input_nu,
        transport.input_mu,
        transport.input_energy,
        transport._output_nu,
        transport._output_energy,
    )


@pytest.fixture(scope="function")
def packet(verysimple_packet_collection):
    return RPacket(
        r=7.5e14,
        nu=verysimple_packet_collection.packets_input_nu[0],
        mu=verysimple_packet_collection.packets_input_mu[0],
        energy=verysimple_packet_collection.packets_input_energy[0],
        seed=1963,
        index=0,
    )


@pytest.fixture(scope="function")
def static_packet():
    return RPacket(
        r=7.5e14,
        nu=0.4,
        mu=0.3,
        energy=0.9,
        seed=1963,
        index=0,
    )


@pytest.fixture()
def set_seed_fixture():
    def set_seed(value):
        np.random.seed(value)

    return njit(set_seed)


@pytest.fixture()
def random_call_fixture():
    def random_call():
        np.random.random()

    return njit(random_call)
