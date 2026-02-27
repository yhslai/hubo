# Hubo

This codebase is written is mostly F#. It might need to call Win32 API.

The runtime is .NET 10.

Assuming that the user isn't very familiar with F#, and he's intented to write the code by hand. Instead of bulk editing a lot of files at once, you should present changes in digestible chunks.

Never do destructive changes like `rm` or `git restore`.


## Overview

In case you lost track, the main purpose, features and directory structure is documented in `OVERVIEW.md`. If this file is not found, it means it's still at very early stage of development and there isn't much for you to refer to.


## Tickets

The features to be implemented are stored in `./tickets`. Tickets are unordered, which means you might need to read their summaries to decide which to do first yourself. Some tickets might have priority levels to help you make this decision.

The ready-to-do tickets are stored in `./tickets` without nesting subdirectory. Tickets that are in `./tickets/pending` are NOT ready to be implemented. Tickets that are in `./tickets/done` are finished. These tickets are not for you to do.


## Knowledge Base

The knowledge base is located at `./<project_name>_kb`. It's an Obsidian vault that can be opened in Obsidian with `Start-Process "obsidian://open?vault=<project_name>_kb"`. However you could read the content directly to consult the knowledge base without getting Obsidian involved.

