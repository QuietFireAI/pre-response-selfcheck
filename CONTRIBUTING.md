# Contributing

Thanks for your interest in the DispatcherAgents stack.

## The one rule that governs everything else

Any change that adds or strengthens a claim about what these tools do or what effects they produce must come with a corresponding entry (or update) in the stack-wide claims ledger: [dispatcher-agents/EVIDENCE.md](https://github.com/QuietFireAI/dispatcher-agents/blob/master/EVIDENCE.md). A claim that cannot be classified (MEASURED / OBSERVED / HYPOTHESIS / DESIGN CLAIM / POSITION) does not ship. This applies to maintainers too.

## Practical guidelines

- Open an issue before large changes so direction can be agreed first.
- Keep PRs focused: one concern per PR.
- For code: Python 3.9+, standard library preferred (the stack ships with zero required dependencies where possible). Include or update tests where they exist.
- For docs: claims must match their evidence class. Replications, negative results, and falsifications are welcome contributions -- a documented failure of one of this stack's hypotheses is treated as a first-class contribution, not an attack.

## Reporting findings

If you run one of the stack's preregistered experiments (see the findings/ directory in dispatcher-agents), open an issue titled `[REPLICATION]` with your raw data attached, whichever way the result went.

## License

By contributing, you agree your contributions are licensed under the MIT License.
