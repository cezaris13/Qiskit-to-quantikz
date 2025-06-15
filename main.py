from qiskit import QuantumCircuit
from typing import List, Optional, Union, Dict


def split_circuit_by_indices(
    qc: QuantumCircuit, boundaries: List[int]
) -> List[QuantumCircuit]:
    """
    Split a QuantumCircuit into subcircuits by explicit instruction-index boundaries.
    """
    subcircuits = []
    for start, end in zip(boundaries[:-1], boundaries[1:]):
        sub = QuantumCircuit(qc.num_qubits, qc.num_clbits)
        for instr, qargs, cargs in qc.data[start:end]:
            sub.append(instr, qargs, cargs)
        subcircuits.append(sub)
    return subcircuits


def split_circuit_by_count(qc: QuantumCircuit, n_slices: int) -> List[QuantumCircuit]:
    """
    Evenly split a QuantumCircuit's instructions into n_slices parts.
    """
    total_ops = len(qc.data)
    breaks = [round(i * total_ops / n_slices) for i in range(n_slices + 1)]
    return split_circuit_by_indices(qc, breaks)


def qiskit_to_quantikz(
    qc: QuantumCircuit,
    include_clbits: bool = True,
    n_slices: Optional[int] = None,
    slice_indices: Optional[List[int]] = None,
    barrier_names: Optional[List[str]] = None,
    slice_titles: Optional[Dict[int, str]] = None,
    slice_all: bool = False,
) -> Union[str, List[str]]:
    """
    Convert a Qiskit QuantumCircuit into quantikz LaTeX, supporting CX, CZ, SWAP, CSWAP,
    Toffoli (CCX), CCZ, and arbitrary multi-controlled gates with correct symbols.
    """
    # Determine slices
    if slice_indices:
        bounds = sorted({0, *slice_indices, len(qc.data)})
        subcircs = split_circuit_by_indices(qc, bounds)
    elif n_slices and n_slices > 1:
        subcircs = split_circuit_by_count(qc, n_slices)
    else:
        subcircs = [qc]

    def render(sub: QuantumCircuit) -> str:
        nonlocal barrier_queue
        n_q = sub.num_qubits
        n_c = sub.num_clbits if include_clbits else 0
        q_lines = [[] for _ in range(n_q)]
        c_lines = [[] for _ in range(n_c)]
        for col, (instr, qargs, cargs) in enumerate(sub.data):
            name = instr.name.lower()
            token_slice = ""
            if slice_all:
                token_slice = rf"\slice{{{col+1}}}"
            elif slice_titles and col in slice_titles:
                token_slice = rf"\slice{{{slice_titles[col]}}}"

            # Measurement
            if name == "measure":
                measured = {sub.qubits.index(q) for q in qargs}
                written = (
                    {sub.clbits.index(c) for c in cargs} if include_clbits else set()
                )
                for i in range(n_q):
                    q_lines[i].append(
                        (r"\meter{}" if i in measured else r"\qw") + token_slice
                    )
                for j in range(n_c):
                    c_lines[j].append(
                        (r"\cw" if j in written else r"\qw") + token_slice
                    )
                continue

            # SWAP gates (quantikz: \swap{} + \qswap{})
            if name == "swap" and instr.num_qubits == 2:
                i0, i1 = sorted(
                    (sub.qubits.index(qargs[0]), sub.qubits.index(qargs[1]))
                )
                for i in range(n_q):
                    if i == i0:
                        q_lines[i].append(rf"\swap{{{i1}}}" + token_slice)
                    elif i == i1:
                        q_lines[i].append(r"\targX{}" + token_slice)
                    else:
                        q_lines[i].append(r"\qw" + token_slice)
                for _ in c_lines:
                    _.append(r"\qw" + token_slice)
                continue

            # CSWAP (Fredkin)
            if name in ("cswap", "fredkin") and instr.num_qubits == 3:
                ctrl = sub.qubits.index(qargs[0])
                s0 = sub.qubits.index(qargs[1])
                s1 = sub.qubits.index(qargs[2])
                # use SWAP symbols on targets
                for i in range(n_q):
                    if i == ctrl:
                        off = s0 - ctrl
                        q_lines[i].append(rf"\ctrl{{{off}}}" + token_slice)
                    elif i == s0:
                        q_lines[i].append(r"\swap{}" + token_slice)
                    elif i == s1:
                        q_lines[i].append(r"\targX{}" + token_slice)
                    else:
                        q_lines[i].append(r"\qw" + token_slice)
                for _ in c_lines:
                    _.append(r"\qw" + token_slice)
                continue

            # Multi-controlled gates (>=3 qubits, not Fredkin)
            if instr.num_qubits >= 3 and name not in ("cswap", "fredkin"):
                idxs = [sub.qubits.index(q) for q in qargs]
                ctrls, tgt = idxs[:-1], idxs[-1]
                # decide target symbol
                if name in ("ccx", "mct") or "x" in name:
                    targ_sym = r"\targ{}"
                elif name in ("ccz") or name.endswith("z"):
                    targ_sym = r"\ctrl{}"
                else:
                    targ_sym = rf"\gate{{{instr.name.upper()}}}"
                for i in range(n_q):
                    if i in ctrls:
                        off = tgt - i
                        q_lines[i].append(rf"\ctrl{{{off}}}" + token_slice)
                    elif i == tgt:
                        q_lines[i].append(targ_sym + token_slice)
                    else:
                        q_lines[i].append(r"\qw" + token_slice)
                for _ in c_lines:
                    _.append(r"\qw" + token_slice)
                continue

            # Two-qubit gates
            if instr.num_qubits == 2:
                ctrl, tgt = sub.qubits.index(qargs[0]), sub.qubits.index(qargs[1])
                if name in ("cx", "cnot"):
                    for i in range(n_q):
                        if i == ctrl:
                            q_lines[i].append(rf"\ctrl{{{tgt-ctrl}}}" + token_slice)
                        elif i == tgt:
                            q_lines[i].append(r"\targ{}" + token_slice)
                        else:
                            q_lines[i].append(r"\qw" + token_slice)
                elif name == "cz":
                    for i in range(n_q):
                        if i == ctrl:
                            q_lines[i].append(rf"\ctrl{{{tgt-ctrl}}}" + token_slice)
                        elif i == tgt:
                            q_lines[i].append(rf"\ctrl{{{ctrl-tgt}}}" + token_slice)
                        else:
                            q_lines[i].append(r"\qw" + token_slice)
                else:
                    g = instr.name.upper()
                    for i in range(n_q):
                        if i == ctrl:
                            q_lines[i].append(rf"\ctrl{{{tgt-ctrl}}}" + token_slice)
                        elif i == tgt:
                            q_lines[i].append(rf"\gate{{{g}}}" + token_slice)
                        else:
                            q_lines[i].append(r"\qw" + token_slice)
                for _ in c_lines:
                    _.append(r"\qw" + token_slice)
                continue

            # Single-qubit gates
            targets = {sub.qubits.index(q) for q in qargs}
            for i in range(n_q):
                if i in targets:
                    q_lines[i].append(rf"\gate{{{instr.name.upper()}}}" + token_slice)
                else:
                    q_lines[i].append(r"\qw" + token_slice)
            for _ in c_lines:
                _.append(r"\qw" + token_slice)

        # Labels
        for i, line in enumerate(q_lines):
            line.insert(0, rf"\lstick{{${{q_{i}}}$}}")
        if include_clbits:
            for j, line in enumerate(c_lines):
                line.insert(0, rf"\lstick{{${{c_{j}}}$}}")

        rows = [" & ".join(l) + r" \\" for l in q_lines]
        if include_clbits:
            rows += [" & ".join(l) + r" \\" for l in c_lines]
        body = "\n".join(rows)
        return "\n".join([r"\begin{quantikz}", body, r"\end{quantikz}"])

    outputs = [render(s) for s in subcircs]
    return outputs if len(outputs) > 1 else outputs[0]


if __name__ == "__main__":
    # Demo including CZ and CY
    circuit = QuantumCircuit(3, 3)
    for i in range(6):
        circuit.h(i % 3)
        circuit.cx(i % 3, (i + 1) % 3)
        circuit.cz(i % 3, (i + 1) % 3)
        circuit.cy(i % 3, (i + 1) % 3)
    circuit.ccx(0, 1, 2)
    circuit.ccz(0, 1, 2)
    circuit.swap(0, 2)
    circuit.measure([0, 1, 2], [0, 1, 2])

    parts = qiskit_to_quantikz(circuit, include_clbits=False, n_slices=2)
    for idx, tex in enumerate(parts, 1):
        print(f"% Slice {idx}")
        print(tex)
