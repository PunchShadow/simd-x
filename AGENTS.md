# Repository Guidelines

## Project Structure & Module Organization
`lib/` hosts GPU kernels, graph primitives, and shared headers; `cpu_alg/` keeps CPU references for parity checks. Application wrappers live in `test/optimal/<app>` (for example `test/optimal/bfs_high_diameter`), each bundling a `Makefile`, CUDA sources, and tuning headers. Dataset converters sit in `other_sys_script/`, while `test/README.md` captures the baseline variants—assume repo-root-relative paths unless a script says otherwise.

## Build, Test, and Development Commands
Run builds within a target application directory to keep object files localized:
```bash
cd test/optimal/bfs_high_diameter && make            # default optimized binary
cd test/optimal/pagerank && make debug=1            # emit symbols + O0
cd test/optimal && bash make.bash bfs_high_diameter # batch helper for CI
```
Use `monitor=1` or `check=1` flags to enable runtime counters and edge verification. `make clean` removes generated objects and binaries so artifacts do not leak into other apps.

## Coding Style & Naming Conventions
CUDA/C++ sources use tab-indented blocks with braces on their own lines (see `lib/gpu_graph.cuh`). Keep kernels in `.cu`, host utilities in `.h/.hpp`, and reuse existing typedefs (`vertex_t`, `index_t`, `weight_t`) for consistent sizing. Prefer snake_case for functions and camelCase for template parameters, guard every header, and fix `nvcc -Wall` warnings instead of muting them.

## Testing Guidelines
Each application exposes a `test` target; point it at `.mtx_beg_pos.bin` and `.mtx_csr.bin` fixtures before scaling up. Add new tests inside the matching `test/optimal/<app>` folder and keep binaries named `<app>.bin` so scripts continue to auto-discover them. Gate heavy assertions behind the `check` flag to avoid penalizing profiling builds, and document at least one reproducible dataset/command pair in every review.

## Commit & Pull Request Guidelines
Write commits in imperative tense with a short subsystem tag (e.g., `lib: tighten reducer bounds`). Squash “fix typo” follow-ups before pushing. Each PR needs the problem statement, architectural summary, exact build/test commands with datasets, and GPU capability assumptions. Add profiler screenshots only when they prove a regression fix or performance claim.

## Data & Configuration Tips
Keep raw graph files outside the repo and feed binaries preprocessed edge lists via `other_sys_script/*_graph_converter.bash`. Store absolute dataset paths in local env files instead of editing Makefiles, and default any new runtime flag to “off” with its usage documented in `readme.md`.
