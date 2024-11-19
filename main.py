from qiskit import QuantumCircuit


def bitsNames(circuit: QuantumCircuit, isQubit: bool = True) -> dict:
    bitsDictionary = {}
    if isQubit:
        bitsList = circuit.qubits
    else:
        bitsList = circuit.clbits
    for i, bits in enumerate(bitsList):
        print(bits)
        index = bits._index
        registerName = bits._register.name
        qubitName = registerName + index.__str__()
        bitsDictionary[qubitName] = i
    return bitsDictionary


def convert(circuit: QuantumCircuit) -> str:
    qubitsList = bitsNames(circuit)
    clbitsList = bitsNames(circuit, isQubit=False)
    print(qubitsList)
    print(clbitsList)
    # print(circuit.data)
    # for circuitInstruction in circuit.data:
    #   operation = circuitInstruction.operation
    #   qubits = circuitInstruction.qubits
    #   clbits = circuitInstruction.clbits

    #   print(operation)
    #   print(qubits)
    #   print(clbits)
    #   print("")
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
