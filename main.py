from qiskit import QuantumCircuit


def convert(circuit: QuantumCircuit) -> str:
    return print(circuit)


if __name__ == "__main__":
    circuit = QuantumCircuit(3)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(0, 2)

    response = convert(circuit)
    print(response)
