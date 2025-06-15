#!/usr/bin/env python3

from absl.testing import absltest
from qiskit import QuantumCircuit

import qiskit_quantikz as qq


class QuantikzTests(absltest.TestCase):
    def test_xgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \gate{X} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(1)
        circuit.x(0)

        result = qq.qiskit_to_quantikz(circuit)

        self.assertEqual(result, actual_result)

    def test_ygate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \gate{Y} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(1)
        circuit.y(0)

        result = qq.qiskit_to_quantikz(circuit)

        self.assertEqual(result, actual_result)

    def test_cxgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \\
\lstick{${q_1}$} & \targ{} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(2)
        circuit.cx(0, 1)

        result = qq.qiskit_to_quantikz(circuit)

        self.assertEqual(result, actual_result)

    def test_xcgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \targ{} & \\
\lstick{${q_1}$} & \ctrl{-1} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(2)
        circuit.cx(1, 0)

        result = qq.qiskit_to_quantikz(circuit)

        self.assertEqual(result, actual_result)

    def test_czgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \\
\lstick{${q_1}$} & \ctrl{-1} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(2)
        circuit.cz(0, 1)

        result = qq.qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_czgate_space(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{2} & \\
\lstick{${q_1}$} & \qw & \\
\lstick{${q_2}$} & \ctrl{-2} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(3)
        circuit.cz(0, 2)

        result = qq.qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_rxgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \gate{R_x(0.5)} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(1)
        circuit.rx(0.5, 0)

        result = qq.qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_swap(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \swap{1} & \\
\lstick{${q_1}$} & \targX{} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(2)
        circuit.swap(0, 1)

        result = qq.qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_swap_with_space(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \swap{1} & \\
\lstick{${q_1}$} & \qw & \\
\lstick{${q_2}$} & \targX{} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(3)
        circuit.swap(0, 2)

        result = qq.qiskit_to_quantikz(circuit)
        print(result)
        self.assertEqual(result, actual_result)

    def test_ccx(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{2} & \\
\lstick{${q_1}$} & \ctrl{1} & \\
\lstick{${q_2}$} & \targ{} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(3)
        circuit.ccx(0, 1, 2)

        result = qq.qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_ccz(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{2} & \\
\lstick{${q_1}$} & \ctrl{1} & \\
\lstick{${q_2}$} & \ctrl{0} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(3)
        circuit.ccz(0, 1, 2)

        result = qq.qiskit_to_quantikz(circuit)
        self.assertEqual(result, actual_result)

    def test_crxgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \\
\lstick{${q_1}$} & \gate{R_x(0.5)} & \\
\end{quantikz}
"""

        circuit = QuantumCircuit(2)
        circuit.crx(0.5, 0, 1)

        result = qq.qiskit_to_quantikz(circuit)
        print(result)
        self.assertEqual(result, actual_result)

    def test_cswap(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \\
\lstick{${q_1}$} & \swap{1} & \\
\lstick{${q_2}$} & \targX{} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(3)
        circuit.cswap(0, 1, 2)

        result = qq.qiskit_to_quantikz(circuit)
        print(result)
        self.assertEqual(result, actual_result)

    def test_cx_measure_no_cl_bits(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \meter{} & \qw & \\
\lstick{${q_1}$} & \targ{} & \qw & \meter{} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(2, 2)
        circuit.cx(0, 1)
        circuit.measure([0, 1], [0, 1])
        result = qq.qiskit_to_quantikz(circuit, include_clbits=False)
        print(result)
        self.assertEqual(result, actual_result)

    def test_cx_measure_cl_bits(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{1} & \meter{} & \qw & \\
\lstick{${q_1}$} & \targ{} & \qw & \meter{} & \\
\lstick{${c_0}$} & \qw & \cw & \qw & \\
\lstick{${c_1}$} & \qw & \qw & \cw & \\
\end{quantikz}"""

        circuit = QuantumCircuit(2, 2)
        circuit.cx(0, 1)
        circuit.measure([0, 1], [0, 1])
        result = qq.qiskit_to_quantikz(circuit, include_clbits=True)
        print(result)
        self.assertEqual(result, actual_result)

    def test_cswap_space_between_swaps_and_controls(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \ctrl{2} & \\
\lstick{${q_1}$} & \qw & \\
\lstick{${q_2}$} & \swap{2} & \\
\lstick{${q_3}$} & \qw & \\
\lstick{${q_4}$} & \targX{} & \\
\end{quantikz}"""

        circuit = QuantumCircuit(5)
        circuit.cswap(0, 2, 4)

        result = qq.qiskit_to_quantikz(circuit)
        print(result)
        self.assertEqual(result, actual_result)


if __name__ == "__main__":
    absltest.main()
