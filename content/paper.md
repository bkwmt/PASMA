---
title: The Paper
nav: Paper
description: "Abstract, figures, tables, poster, video and citation for the ISMIR 2026 paper Digital Existence as Ontological Intervention: Backstage Networks in Postwar Taiwanese Popular Music."
---

# The Paper

<p class="lead">Ming Cheng, Yung-Chuan Chang, Chien-Chang Yang and Li Su. <em>Digital Existence as Ontological Intervention: Backstage Networks in Postwar Taiwanese Popular Music.</em> Proceedings of the 27th International Society for Music Information Retrieval Conference (ISMIR 2026), Abu Dhabi, 8–12 November 2026.</p>

Nominated for the ISMIR 2026 Best Paper Award.

<div class="btns">
<a class="btn" href="assets/pdf/ISMIR2026_459_paper.pdf">Paper (PDF, 8 MB)</a>
<a class="btn ghost" href="assets/pdf/ISMIR2026_459_poster.pdf">Poster (A0 landscape, PDF)</a>
<a class="btn ghost" href="#video">Video</a>
<a class="btn ghost" href="#cite">Cite</a>
</div>

## Abstract

The historical narrative of popular music privileges front-stage stars, and music information retrieval (MIR) has largely reproduced this bias. Backstage laborers, arrangers, session musicians, engineers, remain absent from the field's datasets and research questions. Responding to Born's (2020) call for a critical MIR [@Born2020], we argue that encoding historically marginalized music workers into computational databases constitutes an *ontological intervention* that grants them *digital existence* in an era where absence from metadata means erasure from history. We introduce the Private Archive of Scanned Music Artifacts (PASMA), a dataset reconstructed by an LLM pipeline from {唱片數} Taiwanese vinyl liner notes spanning {年份起}–{年份迄}, and combine Social Network Analysis with MERT embeddings on vocal-separated stems. The collaboration network transformed sharply around 1978, when multitrack recording shifted it from a fragmented, high-modularity ecology to a centralized giant component bridged by elite intermediaries. MERT embeddings indicate that the arrangement traditions defined by these network communities occupy distinct regions in acoustic space. These findings demonstrate that MIR's computational tools, redirected toward the backstage, can decode historical power structures and restore the visibility of the laborers who built the soundscapes of postwar Taiwan.

## The dataset in one figure

![Figure 1. The PASMA data reconstruction pipeline: scanned liner notes pass through OCR with LLM post-correction, credit extraction into (person or institution, role, album) triples, release-year cross-checking, entity disambiguation, and role classification into a controlled vocabulary. A domain expert checks every stage.](assets/img/pipeline.png)

See the [Dataset](dataset.html) page for the sources, the role taxonomy and the validation procedure.

## The network turned around 1978

Credits are projected into a collaboration network: two persons share an edge if they are credited on the same album, weighted by the number of shared albums. Circles are persons, diamonds institutions; colour is role. Each panel is cumulative from {年份起}.

<div class="fig-row">
<figure><img src="assets/img/network_1957_1976.jpg" alt="Cumulative collaboration network 1957–1976" loading="lazy"><figcaption>(a) 1957–1976. Fragmented. Record labels at the centre; lyricists are the bridges; the Taiwanese-language community stands apart.</figcaption></figure>
<figure><img src="assets/img/network_1957_1978.jpg" alt="Cumulative collaboration network 1957–1978" loading="lazy"><figcaption>(b) 1957–1978. The threshold. A cohort of musicians from the American military clubs appears, not yet absorbed.</figcaption></figure>
<figure><img src="assets/img/network_1957_1991.jpg" alt="Cumulative collaboration network 1957–1991" loading="lazy"><figcaption>(c) 1957–1991. One giant component. Recording studios sit at the centre; labels and lyricists are pushed to the edge.</figcaption></figure>
</div>

![Legend for the network figures: node colours by role, diamonds for institutions, red rings for the top bridging actors.](assets/img/network_legend.png)

Three structural metrics, computed on {滑動窗年數}-year sliding windows, turn together in the same window:

- the average clustering coefficient [@WattsStrogatz1998] falls from **{clustering_1960}** (1960) to below **{clustering_after1978}** after 1978;
- the largest connected component crosses **{LCC_ratio}** of all actors around 1976 and stays there;
- Louvain modularity [@Blondel2008] drops from **{modularity_early1970s}** (early 1970s) to **{modularity_1980}** (1980).

![Figure: the three metrics over time on five-year sliding windows. Local triadic closure, global connectedness and community partition strength are mathematically distinct properties that need not co-vary; their simultaneous transition marks 1976–1978 as a structural threshold.](assets/img/temporal_curves.png)

## Who bridges the network changed

Role enrichment among the top {橋接者前N} bridging actors (lowest Burt constraint [@Burt1992]) across the three cumulative periods. Values above 1 mean the role is over-represented among the bridges; “—” means absent from the top {橋接者前N}.

| Role | ’57–’76 / ’57–’78 / ’57–’91 |
|---|---|
| Recording engineer | {表1_錄音師} |
| Producer | {表1_製作人} |
| Backing vocal | {表1_和聲} |
| Pop instrumentalist | {表1_流行樂手} |
| Arranger | {表1_編曲} |
| Composer | {表1_作曲} |
| Lyricist | {表1_作詞} |
| Vocalist | {表1_歌手} |
| Performing artist | {表1_表演藝人} |

Lyricists and singers fall below parity; arrangers, players, backing vocalists and engineers take the bridges. Singing stars were never the connective tissue of this industry. The single strongest bridge across the whole period is the arranger CHEN Chih-yuan 陳志遠,[^names] credited on **{陳志遠_專輯數}** albums and connected to **{陳志遠_合作者數}** collaborators, with the lowest constraint score in the network ({陳志遠_constraint} against {第二名_constraint} for the second-ranked actor). His career is told on the [Historical Context](history.html#5-chen-chih-yuan-and-the-segmented-arrangement-19781991) page.

## The sound follows the structure

Because PASMA does not include the recordings, we assembled a separate corpus of {MERT曲數} recordings ({MERT年份}), removed the vocals with Hybrid Demucs [@Defossez2022hybrid], embedded the instrumental stems with MERT-330M [@MERT2023] and projected the embeddings with UMAP [@McInnes2018]. MERT was given no dates. No audio is redistributed.

<div class="fig-row">
<figure><img src="assets/img/mert_year.png" alt="UMAP projection of MERT embeddings coloured by period" loading="lazy"><figcaption>(a) Coloured by period. Recordings before and after 1978 occupy largely distinct regions.</figcaption></figure>
<figure><img src="assets/img/mert_traditions.png" alt="UMAP projection coloured by arrangement tradition" loading="lazy"><figcaption>(b) Coloured by arrangement tradition. Three traditions form their own regions; CHEN Chih-yuan's works spread across the whole space.</figcaption></figure>
<figure><img src="assets/img/mert_without_chen.png" alt="UMAP projection recomputed without CHEN Chih-yuan" loading="lazy"><figcaption>(c) Recomputed without CHEN Chih-yuan and his protégé. The remaining traditions separate more sharply.</figcaption></figure>
</div>

The four arrangement traditions, and what they correspond to historically, are described in [Historical Context, Section 6](history.html#6-four-arrangement-traditions).

## Why it matters

Encoding these workers into a database is an ontological intervention: it gives them a digital existence they never had. The claim is a reply to Born's critique of MIR's data infrastructures [@Born2020], read through the Social Construction of Technology [@Pinch1984], and it is set out point by point on the [Overview](index.html#a-reply-to-born). If MIR is to diversify its objects and its methods, it must ask not only what algorithms can optimize, but what histories they can restore.

<h2 id="video">Three-minute video</h2>

<video controls preload="metadata" poster="assets/video/ISMIR2026_459_thumbnail.jpg">
<source src="assets/video/ISMIR2026_459_video.mp4" type="video/mp4">
<track kind="subtitles" src="assets/video/ISMIR2026_459_subtitles.vtt" srclang="en" label="English" default>
Your browser does not support embedded video. <a href="assets/video/ISMIR2026_459_video.mp4">Download the MP4</a>.
</video>

<p class="small">Narration synthesized with Kokoro TTS from the authors' script; subtitles available as <a href="assets/video/ISMIR2026_459_subtitles.srt">SRT</a>.</p>

<h2 id="cite">How to cite</h2>

```bibtex
@inproceedings{cheng2026pasma,
  author    = {Cheng, Ming and Chang, Yung-Chuan and Yang, Chien-Chang and Su, Li},
  title     = {Digital Existence as Ontological Intervention: Backstage Networks in Postwar {Taiwanese} Popular Music},
  booktitle = {Proceedings of the 27th International Society for Music Information Retrieval Conference (ISMIR)},
  address   = {Abu Dhabi, United Arab Emirates},
  year      = {2026}
}
```

To cite the dataset, cite the paper and add “PASMA (Private Archive of Scanned Music Artifacts), https://bkwmt.github.io/PASMA/”.

## Erratum

Section 4.2 of the camera-ready paper gives CHEN Chih-yuan's dates as 1941–2011. His dates are **1950–2011** (Taipei Music Center, Taiwan Popular Music Database; Cheng 2026). The error does not affect any result.

## Acknowledgments

This work was supported by the Academia Sinica project “Innovative Applications of AI in Humanities and Sciences” (No. AS-IAIA-114-M06). We are deeply grateful to Pei-Ju Lin, founder of the Taipei music space *Sounds Good*, for generously providing scanned images of her private vinyl collection, without which the construction of PASMA would not have been possible.

[^names]: Chinese personal names are written surname first, as they are spoken, with the surname in capitals and the characters at first mention. The paper's own labels, such as the Chen Chih-Yuan tradition, keep its spelling.
