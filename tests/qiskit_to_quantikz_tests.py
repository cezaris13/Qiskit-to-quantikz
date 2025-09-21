#!/usr/bin/env python3

from src.qiskit_to_quantikz_cezaris13.qiskit_quantikz import qiskit_to_quantikz

import sys

from absl.testing import absltest
from qiskit import QuantumCircuit
from qiskit.quantum_info import random_unitary
from qiskit.circuit.library import UnitaryGate

sys.path.append("..")


class QuantikzTests(absltest.TestCase):
    def test_xgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \gate{X} &
\end{quantikz}"""

        circuit = QuantumCircuit(1)
        circuit.x(0)

        result = qiskit_to_quantikz(circuit)

        self.assertEqual(result, actual_result)

    def test_ygate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \gate{Y} &
\end{quantikz}"""

        circuit = QuantumCircuit(1)
        circuit.y(0)

        result = qiskit_to_quantikz(circuit)

        self.assertEqual(result, actual_result)

    def test_cxgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \\
\lstick{${q_1}$} & \targ{} &
\end{quantikz}"""

        circuit = QuantumCircuit(2)
        circuit.cx(0, 1)

        result = qiskit_to_quantikz(circuit)

        self.assertEqual(result, actual_result)

    def test_xcgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \targ{} & \\
\lstick{${q_1}$} & \ctrl{-1} &
\end{quantikz}"""

        circuit = QuantumCircuit(2)
        circuit.cx(1, 0)

        result = qiskit_to_quantikz(circuit)

        self.assertEqual(result, actual_result)

    def test_czgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \\
\lstick{${q_1}$} & \ctrl{-1} &
\end{quantikz}"""

        circuit = QuantumCircuit(2)
        circuit.cz(0, 1)

        result = qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_czgate_space(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{2} & \\
\lstick{${q_1}$} & \qw & \\
\lstick{${q_2}$} & \ctrl{-2} &
\end{quantikz}"""

        circuit = QuantumCircuit(3)
        circuit.cz(0, 2)

        result = qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_rxgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \gate{R_x(0.5)} &
\end{quantikz}"""

        circuit = QuantumCircuit(1)
        circuit.rx(0.5, 0)

        result = qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_swap(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \swap{1} & \\
\lstick{${q_1}$} & \targX{} &
\end{quantikz}"""

        circuit = QuantumCircuit(2)
        circuit.swap(0, 1)

        result = qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_swap_with_space(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \swap{2} & \\
\lstick{${q_1}$} & \qw & \\
\lstick{${q_2}$} & \targX{} &
\end{quantikz}"""

        circuit = QuantumCircuit(3)
        circuit.swap(0, 2)

        result = qiskit_to_quantikz(circuit)
        print(result)
        self.assertEqual(result, actual_result)

    def test_ccx(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{2} & \\
\lstick{${q_1}$} & \ctrl{1} & \\
\lstick{${q_2}$} & \targ{} &
\end{quantikz}"""

        circuit = QuantumCircuit(3)
        circuit.ccx(0, 1, 2)

        result = qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_ccz(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{2} & \\
\lstick{${q_1}$} & \ctrl{1} & \\
\lstick{${q_2}$} & \ctrl{0} &
\end{quantikz}"""

        circuit = QuantumCircuit(3)
        circuit.ccz(0, 1, 2)

        result = qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_crxgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \\
\lstick{${q_1}$} & \gate{R_x(0.5)} &
\end{quantikz}"""

        circuit = QuantumCircuit(2)
        circuit.crx(0.5, 0, 1)

        result = qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_cswap(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \\
\lstick{${q_1}$} & \swap{1} & \\
\lstick{${q_2}$} & \targX{} &
\end{quantikz}"""

        circuit = QuantumCircuit(3)
        circuit.cswap(0, 1, 2)

        result = qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_cswap_space_between_swaps_and_controls(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{2} & \\
\lstick{${q_1}$} & \qw & \\
\lstick{${q_2}$} & \swap{2} & \\
\lstick{${q_3}$} & \qw & \\
\lstick{${q_4}$} & \targX{} &
\end{quantikz}"""

        circuit = QuantumCircuit(5)
        circuit.cswap(0, 2, 4)

        result = qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_cx_measure_no_cl_bits(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \meter{} & \qw & \\
\lstick{${q_1}$} & \targ{} & \qw & \meter{} &
\end{quantikz}"""

        circuit = QuantumCircuit(2, 2)
        circuit.cx(0, 1)
        circuit.measure([0, 1], [0, 1])
        result = qiskit_to_quantikz(circuit, include_clbits=False)
        self.assertEqual(result, actual_result)

    def test_cx_measure_cl_bits(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \meter{} & \qw & \\
\lstick{${q_1}$} & \targ{} & \qw & \meter{} & \\
\lstick{${c_0}$} & \qw & \cw & \qw & \\
\lstick{${c_1}$} & \qw & \qw & \cw &
\end{quantikz}"""

        circuit = QuantumCircuit(2, 2)
        circuit.cx(0, 1)
        circuit.measure([0, 1], [0, 1])
        result = qiskit_to_quantikz(circuit, include_clbits=True)
        self.assertEqual(result, actual_result)

    def test_slicing_all(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.x(0)
        qc.y(0)
        latex = qiskit_to_quantikz(qc, slice_all=True)
        self.assertIn("\\slice{1}", latex)
        self.assertIn("\\slice{2}", latex)
        self.assertIn("\\slice{3}", latex)

        self.assertTrue(latex.strip().endswith("\\end{quantikz}"))
        self.assertFalse(latex.strip().endswith("& \\\\n\\end{quantikz}"))

    def test_slice_titles(self):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.x(0)
        qc.y(0)
        titles = {0: "init", 1: "middle", 2: "end"}
        latex = qiskit_to_quantikz(qc, slice_titles=titles)
        self.assertIn("\\slice{init}", latex)
        self.assertIn("\\slice{middle}", latex)
        self.assertIn("\\slice{end}", latex)

    def test_2_gate_custom_unitary(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \gate[2]{unitary} & \\
\lstick{${q_1}$} & \qw &
\end{quantikz}"""
        u = random_unitary(4).data

        unitary_gate = UnitaryGate(u)

        qc = QuantumCircuit(2)
        qc.append(unitary_gate, [0, 1])
        qc.draw("mpl")

        result = qiskit_to_quantikz(qc)
        self.assertEqual(result, actual_result)

    def test_3_2_gate_custom_unitaries(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \gate[2]{unitary} & \gate[3]{unitary} & \qw & \\
\lstick{${q_1}$} & \qw & \qw & \gate[2]{unitary} & \\
\lstick{${q_2}$} & \qw & \qw & \qw &
\end{quantikz}"""
        u_1 = random_unitary(4).data
        u_2 = random_unitary(8).data

        unitary_gate_1 = UnitaryGate(u_1)
        unitary_gate_2 = UnitaryGate(u_2)

        qc = QuantumCircuit(3)
        qc.append(unitary_gate_1, [0, 1])
        qc.append(unitary_gate_2, [0, 1,2])
        qc.append(unitary_gate_1, [1, 2])
        qc.draw("mpl")

        result = qiskit_to_quantikz(qc)
        self.assertEqual(result, actual_result)


if __name__ == "__main__":
    absltest.main()
