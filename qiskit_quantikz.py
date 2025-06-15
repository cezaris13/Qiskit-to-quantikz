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


# --- Helper render functions ---


def _init_lines(sub: QuantumCircuit, include_clbits: bool):
    q_lines = [[] for _ in range(sub.num_qubits)]
    c_lines = [[] for _ in range(sub.num_clbits if include_clbits else 0)]
    return q_lines, c_lines


def _add_slices(
    token_slice: str, col: int, slice_all: bool, slice_titles: Optional[Dict[int, str]]
):
    if slice_all:
        return rf"\slice{{{col+1}}}"
    if slice_titles and col in slice_titles:
        return rf"\slice{{{slice_titles[col]}}}"
    return ""


def _render_measure(
    instr, qargs, cargs, sub: QuantumCircuit, q_lines, c_lines, token_slice: str
):
    measured = {sub.qubits.index(q) for q in qargs}
    for i in range(sub.num_qubits):
        q_lines[i].append((r"\meter{}" if i in measured else r"\qw") + token_slice)
    # Classical bits only if drawn
    for j in range(len(c_lines)):
        # check if this clbit is written to by any measurement
        # map c_lines index j to sub.clbits index
        written = False
        for idx, c in enumerate(cargs):
            if sub.clbits.index(c) == j:
                written = True
                break
        c_lines[j].append((r"\cw" if written else r"\qw") + token_slice)


def _render_swap(qargs, sub: QuantumCircuit, q_lines, c_lines, token_slice: str):
    i0, i1 = sorted((sub.qubits.index(qargs[0]), sub.qubits.index(qargs[1])))
    for i in range(sub.num_qubits):
        if i == i0:
            q_lines[i].append(rf"\swap{{{i1}}}" + token_slice)
        elif i == i1:
            q_lines[i].append(r"\targX{}" + token_slice)
        else:
            q_lines[i].append(r"\qw" + token_slice)
    for _ in range(len(c_lines)):
        c_lines[_].append(r"\qw" + token_slice)


def _render_cswap(
    instr, qargs, sub: QuantumCircuit, q_lines, c_lines, token_slice: str
):
    ctrl = sub.qubits.index(qargs[0])
    s0 = sub.qubits.index(qargs[1])
    s1 = sub.qubits.index(qargs[2])
    for i in range(sub.num_qubits):
        if i == ctrl:
            off = s0 - ctrl
            q_lines[i].append(rf"\ctrl{{{off}}}" + token_slice)
        elif i == s0:
            q_lines[i].append(r"\swap{}" + token_slice)
        elif i == s1:
            q_lines[i].append(r"\targX{}" + token_slice)
        else:
            q_lines[i].append(r"\qw" + token_slice)
    for _ in range(len(c_lines)):
        c_lines[_].append(r"\qw" + token_slice)


def _render_multi_qubit(
    instr, qargs, sub: QuantumCircuit, q_lines, c_lines, token_slice: str
):
    idxs = [sub.qubits.index(q) for q in qargs]
    ctrls, tgt = idxs[:-1], idxs[-1]
    name = instr.name.lower()
    if name in ("ccx", "mct") or "x" in name:
        targ_sym = r"\targ{}"
    elif name in ("ccz") or name.endswith("z"):
        targ_sym = r"\ctrl{0}"
    else:
        targ_sym = rf"\gate{{{instr.name.upper()}}}"
    for i in range(sub.num_qubits):
        if i in ctrls:
            off = tgt - i
            q_lines[i].append(rf"\ctrl{{{off}}}" + token_slice)
        elif i == tgt:
            q_lines[i].append(targ_sym + token_slice)
        else:
            q_lines[i].append(r"\qw" + token_slice)
    for _ in range(len(c_lines)):
        c_lines[_].append(r"\qw" + token_slice)


def _render_two_qubit(
    instr, qargs, sub: QuantumCircuit, q_lines, c_lines, token_slice: str
):
    ctrl, tgt = sub.qubits.index(qargs[0]), sub.qubits.index(qargs[1])
    name = instr.name.lower()
    for i in range(sub.num_qubits):
        if name in ("cx", "cnot") and i == ctrl:
            q_lines[i].append(rf"\ctrl{{{tgt-ctrl}}}" + token_slice)
        elif name in ("cx", "cnot") and i == tgt:
            q_lines[i].append(r"\targ{}" + token_slice)
        elif name == "cz" and i == ctrl:
            q_lines[i].append(rf"\ctrl{{{tgt-ctrl}}}" + token_slice)
        elif name == "cz" and i == tgt:
            q_lines[i].append(rf"\ctrl{{{ctrl-tgt}}}" + token_slice)
        elif i == ctrl:
            q_lines[i].append(rf"\ctrl{{{tgt-ctrl}}}" + token_slice)
        elif i == tgt:
            q_lines[i].append(rf"\gate{{{instr.name.upper()}}}" + token_slice)
        else:
            q_lines[i].append(r"\qw" + token_slice)
    for _ in range(len(c_lines)):
        c_lines[_].append(r"\qw" + token_slice)


def _render_default(
    instr, qargs, sub: QuantumCircuit, q_lines, c_lines, token_slice: str
):
    targets = {sub.qubits.index(q) for q in qargs}
    for i in range(sub.num_qubits):
        if i in targets:
            q_lines[i].append(rf"\gate{{{instr.name.upper()}}}" + token_slice)
        else:
            q_lines[i].append(r"\qw" + token_slice)
    for _ in range(len(c_lines)):
        c_lines[_].append(r"\qw" + token_slice)


def render(
    sub: QuantumCircuit,
    include_clbits: bool = True,
    slice_titles: Optional[Dict[int, str]] = None,
    slice_all: bool = False,
) -> str:
    """
    Render a single QuantumCircuit subcircuit into Quantikz LaTeX.
    """
    q_lines, c_lines = _init_lines(sub, include_clbits)
    for col, (instr, qargs, cargs) in enumerate(sub.data):
        token_slice = _add_slices("", col, slice_all, slice_titles)
        name = instr.name.lower()
        if name == "measure":
            _render_measure(instr, qargs, cargs, sub, q_lines, c_lines, token_slice)
        elif name == "swap" and instr.num_qubits == 2:
            _render_swap(qargs, sub, q_lines, c_lines, token_slice)
        elif name in ("cswap", "fredkin") and instr.num_qubits == 3:
            _render_cswap(instr, qargs, sub, q_lines, c_lines, token_slice)
        elif instr.num_qubits >= 3 and name not in ("cswap", "fredkin"):
            _render_multi_qubit(instr, qargs, sub, q_lines, c_lines, token_slice)
        elif instr.num_qubits == 2:
            _render_two_qubit(instr, qargs, sub, q_lines, c_lines, token_slice)
        else:
            _render_default(instr, qargs, sub, q_lines, c_lines, token_slice)
    for i, line in enumerate(q_lines):
        line.insert(0, rf"\lstick{{${{q_{i}}}$}}")
    if c_lines:
        for j, line in enumerate(c_lines):
            line.insert(0, rf"\lstick{{${{c_{j}}}$}}")
    rows = [" & ".join(l) + r" & \\" for l in q_lines]
    rows += [" & ".join(l) + r" & \\" for l in c_lines] if c_lines else []
    body = "\n".join(rows)
    return "\n".join([r"\begin{quantikz}", body, r"\end{quantikz}"])


def qiskit_to_quantikz(
    qc: QuantumCircuit,
    include_clbits: bool = True,
    n_slices: Optional[int] = None,
    slice_indices: Optional[List[int]] = None,
    slice_titles: Optional[Dict[int, str]] = None,
    slice_all: bool = False,
) -> Union[str, List[str]]:
    """
    Convert a Qiskit QuantumCircuit into quantikz LaTeX, supporting various gates.
    """
    if slice_indices:
        bounds = sorted({0, *slice_indices, len(qc.data)})
        subcircs = split_circuit_by_indices(qc, bounds)
    elif n_slices and n_slices > 1:
        subcircs = split_circuit_by_count(qc, n_slices)
    else:
        subcircs = [qc]
    outputs = [render(s, include_clbits, slice_titles, slice_all) for s in subcircs]
    return outputs if len(outputs) > 1 else outputs[0]
