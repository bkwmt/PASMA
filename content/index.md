---
title: PASMA
nav: Overview
description: "PASMA, the Private Archive of Scanned Music Artifacts: a dataset reconstructed from the liner notes of 1,122 Taiwanese vinyl records (1957–1991), and the companion site of the ISMIR 2026 paper Digital Existence as Ontological Intervention."
---

<section class="hero">
<p class="kicker">ISMIR 2026 · Abu Dhabi · Best Paper nominee</p>
<h1>Digital Existence as Ontological Intervention</h1>
<p class="sub">Backstage Networks in Postwar Taiwanese Popular Music</p>
<p class="authors">Ming Cheng · Yung-Chuan Chang · Chien-Chang Yang · Li Su</p>
<p class="affil">Institute of Information Science, Academia Sinica · Graduate Institute of Musicology, National Taiwan University · Taipei, Taiwan</p>
</section>

The arrangers, session musicians and recording engineers who made the sound of postwar Taiwanese popular music appear, if at all, in small print on the sleeve. They have never been encoded in any database. **PASMA** (the Private Archive of Scanned Music Artifacts) writes them in: backstage credits reconstructed from the liner notes of Taiwanese vinyl records, modelled as a collaboration network and set against the sound of the records themselves.

<div class="stats">
<div class="stat"><div class="n">{唱片數}</div><div class="k">vinyl liner notes</div></div>
<div class="stat"><div class="n">{年份起}–{年份迄}</div><div class="k">years covered</div></div>
<div class="stat"><div class="n">{人與機構數}</div><div class="k">people and institutions</div></div>
<div class="stat"><div class="n">{人物角色類數} + {機構類數}</div><div class="k">role categories (persons + institutions)</div></div>
</div>

## What we ask

1. **Who actually makes the music?** Our previous study of the Taiwanese recording studio [@cheng2026dissertation] argues that the backstage, not the star, is where popular music is made. The singer signs the sound; the arrangers, players and engineers produce it. The paper tests this on the collaboration network: in no period do singers appear among the top {橋接者前N} bridging actors (Table 1). The connective tissue of the industry is arrangers, session players, backing vocalists and engineers.
2. **Do people who work together make music that sounds alike?** The same study proposes that backstage workers form relevant social groups around shared taste and working conventions, and that such a group leaves a recognizable mark on the sound. The paper tests this with MERT embeddings of vocal-separated recordings: the four arrangement traditions defined by network communities occupy distinct regions of the acoustic space, and the one arranger who crossed every tradition, Chen Chih-Yuan 陳志遠, produced sound that crosses every cluster; remove his works and the remaining traditions separate more sharply (Fig. 3). The embeddings indicate, rather than prove, that social ties and sound are entangled.
3. **What can computation and history do for each other?** Computation does what reading the archive cannot: it dates the structural threshold to a two-year window and shows that a social position has an acoustic counterpart. History does what computation cannot: it makes 1978 not a kink in a time series but the industrial adoption and standardization of multitrack recording, with studios, people and policies attached. Each side changes what the other is entitled to claim, and MIR gains a purpose its usual applications do not anticipate: a historiographic one.

## A reply to Born

4. Georgina Born's call for a diversified and critical MIR [@Born2020] makes three points the paper takes up. The field's datasets and benchmarks encode assumptions about what music is, who makes it, and which aspects of music-making merit representation. Reducing music to computational knowledge representations risks conflating epistemology with ontology, flattening its embodied and social existence into data. The remedy is *agonistic interdisciplinarity*: computational and humanistic disciplines engaging as equals, each able to transform the other's assumptions.
5. Our reply: we change all three assumptions at once (a non-Western historical repertoire, the backstage rather than the star, collaboration ties and backstage sound rather than consumer-facing attributes). On the warning about reduction we argue for a reversal: for these workers the condition is not reduction but **absence**, and in an age of metadata absence from the record is erasure from history. Being inscribed into the very infrastructure Born criticizes is what grants them **digital existence**. The act is an **ontological intervention**, not a representation. And the study is built as an instance of the remedy, which is point 3 above.

## What the evidence shows

6. **Two methods that never met point to the same year.** From the credits, three network properties that need not move together turn in the same window, 1976–1978. From the recordings, given no dates, MERT embeddings split at 1978. Their convergence indicates that the social reorganization of backstage labour left measurable traces in the sound. What that year was, and who was behind it, is told on the [Historical Context](history.html) page.
7. **Archival silence is itself evidence.** Early liner notes do not credit technical staff; the paper reads this not as a documentation gap but as a condition: engineers and producers had not yet accumulated the professional standing to be named. The dense formalization of credits after 1978 is the moment the backstage consolidated enough power to claim recognition, closure in the sense of the Social Construction of Technology [@Pinch1984].
8. **The encoding is not innocent, and we say so.** {人物角色類數} role categories are a reduction of hundreds of printed credit labels; an edge is a reduction of a working relationship; an embedding is a reduction of a performance. For the backstage this reduction is the price of existence, and it is worth paying when the alternative is not a richer ontology but no entry at all.

<div class="cards">
<a class="card" href="history.html"><b>Historical Context</b><span>The background the paper could not fit: the military clubs, multitrack recording, Chen Chih-Yuan, the four arrangement traditions, with sources.</span></a>
<a class="card" href="people.html"><b>Key People</b><span>Thirteen backstage figures behind the network's key nodes, with portraits and links to their oral histories.</span></a>
<a class="card" href="dataset.html"><b>Dataset</b><span>How PASMA was built: sources, the five-stage LLM pipeline, the role taxonomy, validation, and how to request access.</span></a>
<a class="card" href="paper.html"><b>Paper</b><span>Abstract, figures and tables, the poster, the three-minute video, and how to cite.</span></a>
</div>

<div class="btns">
<a class="btn" href="assets/pdf/ISMIR2026_459_paper.pdf">Paper (PDF)</a>
<a class="btn ghost" href="assets/pdf/ISMIR2026_459_poster.pdf">Poster (PDF)</a>
<a class="btn ghost" href="paper.html#video">3-minute video</a>
<a class="btn ghost" href="paper.html#cite">Cite</a>
</div>

## Access to the data

PASMA is reconstructed from a private collection, and the scans are shared with us on the collector's terms. The dataset is therefore **not publicly downloadable**. Researchers who need the credit data for non-commercial research are welcome to write to us; see the [Dataset](dataset.html#access) page for what we can share and how.

<p class="notice">Scans: private collection of Pei-Ju Lin, founder of the Taipei music space <em>Sounds Good</em>. Portraits on the People page: Taipei Music Center, Taiwan Popular Music Database. Supported by the Academia Sinica project “Innovative Applications of AI in Humanities and Sciences” (AS-IAIA-114-M06).</p>
