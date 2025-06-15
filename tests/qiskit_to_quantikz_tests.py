#!/usr/bin/env python3

from absl.testing import absltest
from qiskit import QuantumCircuit

import qiskit_quantikz as qq


class QuantikzTests(absltest.TestCase):
    def test_xgate(self):
        actual_result = r"""\begin{quantikz}
\lstick{${q_0}$} & \gate{X} \\
\end{quantikz}"""

        circuit = QuantumCircuit(1)
        circuit.x(0)

        result = qq.qiskit_to_quantikz(circuit)

        self.assertEqual(result, actual_result)


if __name__ == "__main__":
    absltest.main()
