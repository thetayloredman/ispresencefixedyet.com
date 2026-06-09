[![Matrix](https://matrix.org/images/matrix-logo-white.svg)](https://matrix.org) Is Presence Fixed Yet?

# Not at all. But you can help!

Presence is notoriously one of the most "broken" features in the [Matrix] protocol. Even with efforts to improve
server implementations[^1], **almost every major public Matrix deployment disables federated presence**, citing
performance concerns[^2].

Current Matrix presence is fundamentally flawed: Users receive presence data for all users they share rooms with,
even if the two users have never interacted or spoken otherwise. Additionally, presence EDUs sent over federation
have short TTLs and require regular retransmission, resulting in write amplification which prevents current presence
from being enabled on major public deployments where it matters most.

A group of community members including maintainers of the [Continuwuity] homeserver began work on a set of proposals
to dramatically reduce presence's footprint on federation traffic and improve privacy UX for end users. This work,
dubbed "Presence v2," currently consists of four proposals which will improve presence by improving batching behavior,
and most importantly, only sharing presence with interested parties.

If you are interested in helping improve Presence for the Matrix community, please join us in [#presence-v2:zirco.dev].

## The Proposals

* 🚧 **Selective Presence**, reducing load by only sharing presence with interested parties
  * **Status:** Internal Draft
  * **How you can help:** Join [#presence-v2:zirco.dev] and participate in discussion about Selective Presence.
* 🚧 **Incremental Presence**, reducing load by increasing presence TTLs and providing batching behavior
  * **Status:** Concept
* 🔲 **Sliding Sync Extension: Presence**, reducing client-server sync traffic for users not regularly viewed
  * **Status:** Concept
* 🔲 **Fetchable Presence**, allowing users to publish presence data without pushing to every possible user
  * **Status:** Concept

---

Last updated: 2026-06-09  
[This website is open source.][github]

---

[^1]: Synapse has had a meta-issue open about improving presence performance for 5 years: [#9478]
[^2]: Since 2018, homeserver operators have had performance concerns related to presence, and even raised them
      as bugs in Synapse. [#3971], [#9339]

[Matrix]: https://matrix.org/
[Continuwuity]: https://continuwuity.org/
[#presence-v2:zirco.dev]: https://matrix.to/#/#presence-v2:zirco.dev
[#3971]: https://github.com/matrix-org/synapse/issues/3971
[#9339]: https://github.com/matrix-org/synapse/issues/9339
[#9478]: https://github.com/matrix-org/synapse/issues/9478
[github]: https://github.com/thetayloredman/ispresencefixedyet.com
