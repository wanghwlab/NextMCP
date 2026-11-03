# Repository Skill Sources

This directory stores repository-side skill source packages.

It is not part of the `nextmcp` server runtime:

- the server does not discover this directory
- the server does not expose these skills through MCP tools
- completed skills must still be installed on the client side, under
  `~/.agents/skills/` for Codex or `~/.claude/skills/` for Claude Code

Current layout is class-based:

- `skills/experts/` for pipeline-specific expert skills
- `skills/meta/` for skill-generation and maintenance skills

## Relationship Map

```mermaid
---
config:
  theme: base
  htmlLabels: false
  themeVariables:
    fontFamily: Arial, sans-serif
    fontSize: 16px
    lineColor: "#475569"
  flowchart:
    useMaxWidth: true
    nodeSpacing: 24
    rankSpacing: 40
    wrappingWidth: 210
    curve: linear
---
flowchart TD
    A["`Versioned pipeline checkout or enabled MCP material inspection`"]

    B["`pipeline-expert-skill-creator`"]

    C["`skills/experts/
    PIPELINE-expert-skill/`"]

    D["`Client agent uses
    expert skill with nextmcp`"]

    E["`pipeline-test-contract-builder`"]

    F["`pipeline-test-
    mode-classifier`"]

    G["`pipeline-test-
    config-localizer`"]

    H["`pipeline-test-
    converter`"]

    I["`tests/pipeline_support/
    PIPELINE/smoke.yaml`"]

    J["`tests/pipeline_support/
    PIPELINE/smoke.task.md`"]

    K["`Completed smoke run`"]

    L["`Saved eval bundle`"]

    M["`pipeline-smoke-evaluator`"]

    N["`Simple smoke verdict`"]

    A --> B
    B --> C
    C --> D

    A --> E
    E --> F
    E --> G
    E --> H

    F --> I
    G --> I
    H --> I
    H --> J

    D --> K
    K --> L

    I --> M
    L --> M
    M --> N

    classDef source fill:#F1F5F9,stroke:#64748B,color:#0F172A,stroke-width:1.5px;
    classDef tool fill:#EFF6FF,stroke:#3B82F6,color:#172554,stroke-width:1.5px;
    classDef file fill:#F0FDF4,stroke:#16A34A,color:#14532D,stroke-width:1.5px;
    classDef execution fill:#FFF7ED,stroke:#EA580C,color:#7C2D12,stroke-width:1.5px;
    classDef verdict fill:#F5F3FF,stroke:#7C3AED,color:#4C1D95,stroke-width:2px;

    class A source;
    class B,E,F,G,H,M tool;
    class C,I,J,L file;
    class D,K execution;
    class N verdict;
```



This flow has three main paths:

- build or refresh one expert skill from pipeline materials
- build one smoke contract from upstream pipeline tests
- evaluate one completed smoke run against its hidden contract

This repository does not currently ship a concrete operator skill source package.
Generic nextmcp usage guidance is carried by the MCP tool docstrings instead.

Current source packages:

- `skills/experts/ampliseq-expert-skill/`
- `skills/experts/atacseq-expert-skill/`
- `skills/experts/chipseq-expert-skill/`
- `skills/experts/epitopeprediction-expert-skill/`
- `skills/experts/fetchngs-expert-skill/`
- `skills/experts/mag-expert-skill/`
- `skills/experts/methylseq-expert-skill/`
- `skills/experts/nanoseq-expert-skill/`
- `skills/experts/rnaseq-expert-skill/`
- `skills/experts/rnafusion-expert-skill/`
- `skills/experts/riboseq-expert-skill/`
- `skills/experts/sarek-expert-skill/`
- `skills/experts/scrnaseq-expert-skill/`
- `skills/meta/pipeline-expert-skill-creator/`
- `skills/meta/pipeline-smoke-evaluator/`
- `skills/meta/pipeline-test-config-localizer/`
- `skills/meta/pipeline-test-contract-builder/`
- `skills/meta/pipeline-test-converter/`
- `skills/meta/pipeline-test-mode-classifier/`

**Use the existing `skills/` source packages as the starting point, or generate a new package with
`skill-creator` plus `pipeline-expert-skill-creator`.**

See the [expert package guide](experts/README.md) for current versions, offline questions,
and the all-13 evaluation script. 
See the [meta skill guide](meta/README.md) for generation,
updates, test preparation, and installation. 
