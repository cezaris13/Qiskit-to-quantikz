from qiskit import QuantumCircuit


def qubitNames(circuit: QuantumCircuit) -> dict:
    qubitsList = {}
    for qubits in circuit.qubits:
        print(qubits)
        index = 0  # TODO
        qubitName = "q0"  # TODO
        qubitsList[qubitName] = index
    return qubitsList


def convert(circuit: QuantumCircuit) -> str:
    qubitsList = qubitNames(circuit)
    # print(circuit.data)
    for circuitInstruction in circuit.data:
        operation = circuitInstruction.operation
        qubits = circuitInstruction.qubits
        clbits = circuitInstruction.clbits

        print(operation)
        print(qubits)
        print(clbits)
        print("")
    return print(circuit)


if __name__ == "__main__":
    circuit = QuantumCircuit(4, 4)
    circuit.h(0)
    circuit.h(1)
    circuit.cx(0, 1)
    circuit.cx(0, 2)
    circuit.measure([0, 1, 2, 3], [0, 1, 2, 3])

    response = convert(circuit)
    print(response)
