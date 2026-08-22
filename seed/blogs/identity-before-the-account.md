---
title: "Identity Before the Account"
slug: "identity-before-the-account"
summary: "Giving every visitor a server-issued actor id means reading history exists before signup — and survives it."
categories: ["engineering", "product"]
series: "foundations"
series_position: 1
---
Most platforms start a reader's history at signup. Everything before that — the
articles they read while deciding whether to sign up — is discarded, which is
exactly the period you would most like to understand.

## Actors

Canerly issues every visitor a server-generated actor id on their first
request, and returns it as a token the client echoes back on every subsequent
one. No account, no email, no consent dialog, because it identifies a session
lineage rather than a person.

Reading history, positions, and engagement events all attach to the actor.

## Merge on signup

When the visitor eventually creates an account, the actor is not thrown away —
it is merged into the new user, and everything they read beforehand comes with
them.

> The reader who signs up on their fourth article should find the first three
> waiting for them.

The merge is the part worth getting right. It runs once, inside the transaction
that creates the user, and it is idempotent: replaying it cannot duplicate
history.

## The failure mode to avoid

Dropping the actor token on a single request mints a *new* actor, silently. The
visitor's history forks, and the merge at signup finds only the fragment from
whichever branch they happened to be on.

So the token is echoed on every request and re-read from every response, and
the proxy that does it is the only place that touches it.
