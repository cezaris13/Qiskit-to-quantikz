from qiskit import QuantumCircuit
from typing import List, Optional, Union, Dict


def _split_circuit_by_indices(
    qc: QuantumCircuit, boundaries: List[int]
) -> List[QuantumCircuit]:
    """
    Split a QuantumCircuit into subcircuits by explicit instruction-index boundaries.
    """
    subcircuits = []
    for start, end in zip(boundaries[:-1], boundaries[1:]):
        sub = QuantumCircuit(qc.num_qubits, qc.num_clbits)
        for circuit_instruction in qc.data[start:end]:
            instr, qargs, cargs = circuit_instruction.operation, circuit_instruction.qubits, circuit_instruction.clbits
            sub.append(instr, qargs, cargs)
        subcircuits.append(sub)
    return subcircuits


def _split_circuit_by_count(qc: QuantumCircuit, num_subcircuits: int) -> List[QuantumCircuit]:
    """
    Evenly split a QuantumCircuit's instructions into num_subcircuits parts.
    """
    total_ops = len(qc.data)
    breaks = [round(i * total_ops / num_subcircuits) for i in range(num_subcircuits + 1)]
    return _split_circuit_by_indices(qc, breaks)


# --- Helper render functions ---


def _init_lines(sub: QuantumCircuit, include_clbits: bool):
    q_lines = [[] for _ in range(sub.num_qubits)]
    c_lines = [[] for _ in range(sub.num_clbits if include_clbits else 0)]
    return q_lines, c_lines


def _add_slices(col: int, slice_all: bool, slice_titles: Optional[Dict[int, str]]):
    if slice_all:
        return rf"\slice{{{col+1}}}"
    if slice_titles and col in slice_titles:
        return rf"\slice{{{slice_titles[col]}}}"
    return ""


def _render_measure(
    qargs, cargs, sub: QuantumCircuit, q_lines, c_lines, token_slice: str
):
    measured = {sub.qubits.index(q) for q in qargs}
    for i in range(sub.num_qubits):
        q_lines[i].append((r"\meter{}" if i in measured else r"\qw") + token_slice)
    for j in range(len(c_lines)):
        written = any(sub.clbits.index(c) == j for c in cargs)
        c_lines[j].append((r"\cw" if written else r"\qw") + token_slice)


def _render_swap(qargs, sub: QuantumCircuit, q_lines, c_lines, token_slice: str):
    i0, i1 = sorted((sub.qubits.index(qargs[0]), sub.qubits.index(qargs[1])))
    for i in range(sub.num_qubits):
        if i == i0:
            q_lines[i].append(rf"\swap{{{i1-i0}}}" + token_slice)
        elif i == i1:
            q_lines[i].append(r"\targX{}" + token_slice)
        else:
            q_lines[i].append(r"\qw" + token_slice)
    for _ in range(len(c_lines)):
        c_lines[_].append(r"\qw" + token_slice)


def _render_unitary_gate(instr, qargs, sub: QuantumCircuit, q_lines, c_lines, token_slice: str):
    i0, _ = sorted((sub.qubits.index(qargs[0]), sub.qubits.index(qargs[1])))
    for i in range(sub.num_qubits):
        if i == i0:
            q_lines[i].append(rf"\gate[{instr.num_qubits}]{{{instr.name}}}" + token_slice)
        else:
            q_lines[i].append(r"\qw" + token_slice)
    for _ in range(len(c_lines)):
        c_lines[_].append(r"\qw" + token_slice)


def _render_cswap(
    qargs, sub: QuantumCircuit, q_lines, c_lines, token_slice: str
):
    ctrl, s0, s1 = [sub.qubits.index(q) for q in qargs]
    for i in range(sub.num_qubits):
        if i == ctrl:
            off = s0 - ctrl
            q_lines[i].append(rf"\ctrl{{{off}}}" + token_slice)
        elif i == s0:
            q_lines[i].append(rf"\swap{{{s1-s0}}}" + token_slice)
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
    params = getattr(instr, "params", [])
    if name in ("crx", "cry", "crz") and params:
        axis = name[-1]
        theta = params[0]
        for i in range(sub.num_qubits):
            if i == ctrl:
                q_lines[i].append(rf"\ctrl{{{tgt-ctrl}}}" + token_slice)
            elif i == tgt:
                q_lines[i].append(rf"\gate{{R_{axis}({theta})}}" + token_slice)
            else:
                q_lines[i].append(r"\qw" + token_slice)
    else:
        for i in range(sub.num_qubits):
            if name in ("cx","cnot"):
                if i == ctrl:
                    q_lines[i].append(rf"\ctrl{{{tgt-ctrl}}}" + token_slice)
                elif i == tgt:
                    q_lines[i].append(r"\targ{}" + token_slice)
                else:
                    q_lines[i].append(r"\qw" + token_slice)
            elif name == "cz":
                if i == ctrl:
                    q_lines[i].append(rf"\ctrl{{{tgt-ctrl}}}" + token_slice)
                elif i == tgt:
                    q_lines[i].append(rf"\ctrl{{{ctrl-tgt}}}" + token_slice)
                else:
                    q_lines[i].append(r"\qw" + token_slice)
            else:
                if i == ctrl:
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
    name = instr.name.lower()
    params = getattr(instr, "params", [])
    if len(qargs) == 1 and name in ("rx", "ry", "rz") and params:
        axis = name[-1]
        theta = params[0]
        for i in range(sub.num_qubits):
            if sub.qubits.index(qargs[0]) == i:
                q_lines[i].append(rf"\gate{{R_{axis}({theta})}}" + token_slice)
            else:
                q_lines[i].append(r"\qw" + token_slice)
        for _ in range(len(c_lines)):
            c_lines[_].append(r"\qw" + token_slice)
        return
    targets = {sub.qubits.index(q) for q in qargs}
    for i in range(sub.num_qubits):
        if i in targets:
            q_lines[i].append(rf"\gate{{{instr.name.upper()}}}" + token_slice)
        else:
            q_lines[i].append(r"\qw" + token_slice)
    for _ in range(len(c_lines)):
        c_lines[_].append(r"\qw" + token_slice)


def _render(
    sub: QuantumCircuit,
    include_clbits: bool = True,
    slice_titles: Optional[Dict[int, str]] = None,
    slice_all: bool = False,
) -> str:
    """
    Render a single QuantumCircuit subcircuit into Quantikz LaTeX, with optional in-place slice annotations.
    """
    q_lines, c_lines = _init_lines(sub, include_clbits)
    for col, circuit_instruction in enumerate(sub.data):
        instr, qargs, cargs = circuit_instruction.operation, circuit_instruction.qubits, circuit_instruction.clbits
        token_slice = _add_slices(col, slice_all, slice_titles)
        name = instr.name.lower()
        if name == "measure":
            _render_measure(qargs, cargs, sub, q_lines, c_lines, token_slice)
        elif instr.name == "unitary":
            _render_unitary_gate(instr, qargs, sub, q_lines, c_lines, token_slice)
        elif name == "swap" and instr.num_qubits == 2:
            _render_swap(qargs, sub, q_lines, c_lines, token_slice)
        elif name in ("cswap", "fredkin") and instr.num_qubits == 3:
            _render_cswap(qargs, sub, q_lines, c_lines, token_slice)
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
    if c_lines:
        rows += [" & ".join(l) + r" & \\" for l in c_lines]
    body = "\n".join(rows)
    return _remove_last_occurrence(
        "\n".join([r"\begin{quantikz}", body, r"\end{quantikz}"]), r" \\"
    )


def _remove_last_occurrence(s, sub):
    index = s.rfind(sub)
    if index == -1:
        return s
    return s[:index] + s[index + len(sub) :]


def qiskit_to_quantikz(
    qc: QuantumCircuit,
    include_clbits: bool = True,
    num_subcircuits: Optional[int] = None,
    subcircuit_indices: Optional[List[int]] = None,
    slice_titles: Optional[Dict[int, str]] = None,
    slice_all: bool = False,
) -> Union[str, List[str]]:
    """
    Convert a Qiskit QuantumCircuit into quantikz LaTeX.
    - If slice_all or slice_titles is used, returns one string with in-place \\slice annotations.
    - Otherwise, if subcircuit_indices or num_subcircuits>1, returns a list of subcircuit strings.
    """
    if slice_all or (slice_titles and len(slice_titles) > 0):
        return _render(qc, include_clbits, slice_titles, slice_all)
    if subcircuit_indices or (num_subcircuits and num_subcircuits > 1):
        if subcircuit_indices:
            bounds = sorted({0, *subcircuit_indices, len(qc.data)})
            subcircs = _split_circuit_by_indices(qc, bounds)
        else:
            subcircs = _split_circuit_by_count(qc, num_subcircuits)
        return [_render(s, include_clbits, slice_titles, slice_all) for s in subcircs]
    return _render(qc, include_clbits, slice_titles, slice_all)
