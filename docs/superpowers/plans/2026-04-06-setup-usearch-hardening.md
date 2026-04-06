# Setup and Unified Search Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `setup` safer and more consistent in agent/non-interactive flows, and make `usearch` gracefully degrade when vector search cannot initialize.

**Architecture:** Keep the fix narrow. Add regression tests around the current public behavior, then update `setup.py` to distinguish interactive vs non-interactive prompts, unify MinerU recommendation logic around a shared availability signal, and avoid writing unnecessary `config.local.yaml` files. Update `index.py` so unified search treats runtime vector initialization failures as degradation rather than a hard failure.

**Tech Stack:** Python, pytest, argparse-driven CLI helpers

---

### Task 1: Guard `usearch` graceful degradation

**Files:**
- Modify: `tests/test_index.py`
- Modify: `scholaraio/index.py`

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run the targeted test and confirm it fails for the current runtime exception path**
- [ ] **Step 3: Implement minimal degradation logic in `unified_search()`**
- [ ] **Step 4: Re-run the targeted test and confirm it passes**

### Task 2: Make non-interactive `setup` safe by default

**Files:**
- Modify: `tests/test_setup.py`
- Modify: `scholaraio/setup.py`

- [ ] **Step 1: Add a regression test showing EOF/non-interactive prompts do not auto-install**
- [ ] **Step 2: Run the targeted setup test and confirm it fails**
- [ ] **Step 3: Implement prompt metadata so EOF/non-interactive input can be distinguished from explicit Enter**
- [ ] **Step 4: Re-run the targeted setup test and confirm it passes**

### Task 3: Unify MinerU recommendation and free-token guidance

**Files:**
- Modify: `tests/test_setup.py`
- Modify: `scholaraio/setup.py`

- [ ] **Step 1: Add regression tests for CLI-present/no-token recommendation and messaging**
- [ ] **Step 2: Run the targeted tests and confirm current behavior is wrong**
- [ ] **Step 3: Implement shared MinerU availability details used by both check and wizard, keeping MinerU preferred when the path is viable**
- [ ] **Step 4: Re-run the targeted tests and confirm they pass**

### Task 4: Avoid unnecessary `config.local.yaml` writes

**Files:**
- Modify: `tests/test_setup.py`
- Modify: `scholaraio/setup.py`

- [ ] **Step 1: Add regression tests covering empty/no-op key collection and explicit non-default parser persistence**
- [ ] **Step 2: Run the targeted tests and confirm current behavior writes too eagerly**
- [ ] **Step 3: Implement minimal write gating**
- [ ] **Step 4: Re-run the targeted tests and confirm they pass**

### Task 5: Verification

**Files:**
- Verify: `tests/test_setup.py`
- Verify: `tests/test_index.py`

- [ ] **Step 1: Run focused pytest commands for setup/index regressions**
- [ ] **Step 2: Run a real `scholaraio setup check --lang zh` smoke test**
- [ ] **Step 3: Run a real `scholaraio usearch "drag reduction" --top 5` smoke test in the current environment and confirm graceful degradation instead of crash**
