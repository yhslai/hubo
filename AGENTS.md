# Hubo

This codebase is written is mostly F#. It might need to call Win32 API.

The runtime is .NET 10.

Assuming that the user isn't very familiar with F#, and he's intented to write the code by hand. Instead of bulk editing a lot of files at once, you should present changes in digestible chunks.

Never do destructive changes like `rm` or `git restore`. You can suggest me do these kinds of commands, but don't run them yourselves.

You should also not use `git add` or `git commit`, unless I specifically ask you to, or you're doing a `ticket done` skill.


## ReadMe

In case you lost track, the main purpose, features and directory structure is documented in `README.md`. If this file is not found, it means it's still at very early stage of development and there isn't much for you to refer to.


## Knowledge Base

The unified knowledge base is located at `./hubo_kb`.

You can also read files directly from the repository without Obsidian.


## Tickets

Tickets are managed inside the Obsidian vault so knowledge and task tracking live in one place.

- Ready-to-do tickets: `./hubo_kb/tickets/*.md`
- Not ready yet: `./hubo_kb/tickets/pending/*.md`
- Finished tickets: `./hubo_kb/tickets/done/*.md`

Tickets are unordered, which means you might need to read their summaries to decide which to do first yourself. Some tickets might have priority levels to help you make this decision.

Tickets usually have a h1 section `# Summary` at the top. If a ticket doesn't have such a section, the text before the first heading is used as summary.

As tickets are part of the knowledge base, they might have linked to images, to each other, or to external URLs. Make sure you read the details before you try to work on a ticket.