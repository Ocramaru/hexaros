# .agents

`.agents/` is a convention created by Marco Cassar for keeping coding-agent notes tied to the folder they describe. It is being tested privately before a public release, so the tooling that reads these files is not part of this repo.

Any directory can hold an `.agents/` folder. The notes sit next to the code, travel with it through git, and are scoped to that directory: an `.agents/` higher up the tree covers more ground, and one deeper in narrows or overrides it.

| File | Answers |
|---|---|
| `context.md` | what this directory assumes and how its parts fit together: the context needed to change it correctly |
| `learned.md` | what experiments showed and the traps that already cost time, so they are only paid once |
| `todo.md` | open features for this directory |

The notes reach an agent automatically. A set of hooks (agent tool hooks and git hooks) resolves the notes and standards that govern a file when it is edited and injects them into the agent's context, so a session working here starts with `context.md` already loaded and is pointed at `learned.md` and `todo.md` when it needs them. Without that tooling the files are plain markdown and still read fine.
