---
layout: default
---

[![Matrix](https://matrix.org/images/matrix-logo-white.svg)](https://matrix.org) ![Presence v2 Logo](/assets/logo.png){:height="32px"} Is Presence Fixed Yet?

# No, but we're making progress.

Today, presence is one of [Matrix]'s least-deployed core features. Even with efforts to improve implementations[^1],
**almost every major public Matrix deployment disables federated presence**, citing privacy and performance concerns[^2]. 

The root problem is architectural. Today, Matrix servers distribute presence to anyone who shares a room with a user,
even if the two users have never interacted. Small servers regularly send updates upwards of 100,000 times an hour[^3].
This expense results in server operators disabling presence entirely, which in turn results in a poor user experience
for the large public servers where it matters most.

The goal of the Presence v2 initiative is simple: make presence useful for users while reducing its cost to servers.
We hope that through improvements, presence can be a valued feature available to many more Matrix users.

A [group of community members](/contributors) including maintainers of the [Continuwuity] homeserver, have been working on
a coordinated set of Matrix Spec Change proposals (MSCs) to dramatically reduce presence's footprint on federation traffic,
improve privacy, and better align presence with the social use case.

If you are interested in helping improve Presence for the Matrix community, please join us in [#presence-v2:zirco.dev].

## The Proposals

### [MSC4495: Selective Presence][MSC4495]

Selective Presence substantially cuts down on the amount of presence data sent by requiring users to explicitly indicate
which other users or rooms they want to share their presence with, rather than sending presence to all users that can see
them. Alongside our other proposals, this will both create a new privacy model for presence and overall reduce how much
presence data is sent.

- **Status:** Proposal (Community Review)
- **How you can help:** Provide review on [MSC4495] on the MSC tracker, or implement it in clients/servers
- **Implementations:**
    - 🚧 **Ruma:** [#2546](https://github.com/ruma/ruma/pull/2546) (merged)
    - 🚧 **[Continuwuity]**: [#2034](https://forgejo.ellis.link/continuwuation/continuwuity/pulls/2034) (open)
    - 🔲 **Client:** TBD

### [MSC4532: Revised Social Presence][MSC4532]

Revised Social Presence is a proposal to remodel presence information to better support social use cases, including
overrides and a `busy` status. This proposal also makes major improvements in privacy, alongside fixing some
long-standing visual bugs. A [complementary post](/analysis) is also available to show the positive impacts Revised
Social Presence will have on the Matrix ecosystem.

- **Status:** Proposal (Community Review)
- **How you can help:** Provide review on [MSC4532] on the MSC tracker, or implement it in clients/servers
- **Implementations:**
    - 🚧 **Ruma:** [WIP branch](https://github.com/thetayloredman/ruma/tree/ln/msc4532)
    - 🚧 **[Continuwuity]:** WIP
    - 🔲 **Client:** TBD

### Sliding Sync Extension: Presence

We are exploring a [Sliding Sync (MSC4186)][sliding-sync] extension to reduce the amount of presence data sent
to clients. This would allow clients to only receive presence for users they are actively viewing, resulting in
reduced bandwidth usage and improved performance for clients.

- **Status:** Concept
- **How you can help:** Join [#presence-v2:zirco.dev] and participate in discussion and design conversations

### Fetchable Presence

Finally, we are exploring a proposal to allow users to publish their presence data without sending it to every user
who can see them. Instead, users would be able to fetch presence data for other users on demand, preserving existing
presence workflows while reducing traffic sent unnecessarily.

- **Status:** Concept
- **How you can help:** Join [#presence-v2:zirco.dev] and participate in discussion and design conversations

---

Not affiliated with the Matrix.org Foundation or New Vector Ltd.  
Last updated <span id="last-updated-ago"></span> ago (<span id="last-updated-ts"></span>).  
[This website is open source.][github]

<script>
    window.lastUpdated = new Date("{{ site.time | date_to_xmlschema }}");
</script>
<script src="./js/last-updated.js"></script>

---

[^1]: Synapse has had a meta-issue open about improving presence performance for 5 years: [#15877]

[^2]:
    Since 2018, homeserver operators have had performance concerns related to presence, and even
    raised them as bugs in Synapse. [#3971], [#9339]

[^3]:
    Based on a [2020 analysis][presence-v1-rates] of an Element deployment with 66 daily active users.
    Disabling presence resulted in a ~19Hz reduction in outbound federation transactions, or 68,400
    fewer federation transactions per hour.

[Matrix]: https://matrix.org/
[Continuwuity]: https://continuwuity.org/
[#presence-v2:zirco.dev]: https://matrix.to/#/#presence-v2:zirco.dev
[#3971]: https://github.com/matrix-org/synapse/issues/3971
[#9339]: https://github.com/matrix-org/synapse/issues/9339
[#15877]: https://github.com/element-hq/synapse/issues/15877
[github]: https://github.com/thetayloredman/ispresencefixedyet.com
[MSC4495]: https://github.com/matrix-org/matrix-spec-proposals/pull/4495
[MSC4532]: https://github.com/matrix-org/matrix-spec-proposals/pull/4532
[presence-v1-rates]: https://github.com/matrix-org/matrix-spec-proposals/pull/4259/changes#r2858835260
[sliding-sync]: https://github.com/matrix-org/matrix-spec-proposals/pull/4186
