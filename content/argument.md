---
title: The Argument
nav: The Argument
description: "The conceptual claim of the ISMIR 2026 paper, set out as a reply to Georgina Born's critique of MIR: for backstage workers the problem is absence, not reduction, and encoding them is an ontological intervention."
---

# The Argument

<p class="lead">A reply to Georgina Born, point by point, with the evidence that keeps it from being a gesture.</p>

The paper is a dataset paper, a network study and an audio study, but the reason it exists is a philosophical one. Georgina Born's 2020 call for a diversified and critical MIR [@Born2020] asks the field to examine what its data infrastructures assume about music. We take her critique seriously and answer it from a case where the usual answer does not apply. This page sets out that exchange as it stands in the paper, in three moves, each paired with our response and with the place in the study where the response is cashed out.

| Born's point (as read in the paper) | Our response | Where it is tested |
|---|---|---|
| MIR's datasets and benchmarks encode assumptions about **what music is, who makes it, and which aspects of music-making merit representation**; the field's institutional composition naturalizes agendas shaped by the commercial digital music economy. | We agree, and change all three terms: a non-Western historical repertoire, the backstage rather than the star, and collaboration ties and backstage sound rather than consumer-facing attributes. | PASMA; Figs. 2 and 3 |
| Reducing music to computational knowledge representations risks **conflating epistemology with ontology**, flattening the embodied and social existence of music into data. | For the subjects of this study the condition is not reduction but **absence**. Inscription into the very infrastructure Born criticizes is what grants them **digital existence**; the act is an **ontological intervention**, not a representation. | Section 5.1; the convergence of two independent methods on 1978 |
| The remedy is **agonistic interdisciplinarity**: computational and humanistic disciplines engaging as equals, each able to transform the other's assumptions. | The study is built as an instance of it: the question comes from music history and labour studies, the tools from MIR, and each side changes what the other can claim. | Sections 2.1, 5.2 and the Conclusion |

## 1. What the infrastructure assumes

Born's intervention goes beyond a call for topical variety. She identifies a structural condition: a field drawn overwhelmingly from computer science has naturalized research agendas shaped by the commercial digital music economy, and the datasets and benchmarks that anchor its research encode particular assumptions about what music is, who makes it, and which aspects of music-making merit representation [@Born2020]. The paper's opening pages show how those assumptions look from the backstage. Audio features and metadata are mobilized for consumer-facing ends: recommendation matches listeners to products by the names of credited performers; hit prediction treats success as a property of songs or artists. Recorded music, however, is a collective technical and artistic practice [@Small1998], assembled by arrangers, session musicians, engineers and producers working inside specific studios and technologies [@Campelo2015; @horning2013chasing]. These workers are invisible in MIR not because they are unimportant but because the field's data and questions were never designed to see them.

Our first response is simply to agree and to act on all three of Born's terms at once. **What music**: postwar Taiwanese popular music, 1957 to 1991, a repertoire almost never studied in MIR. **Who makes it**: the backstage, the people in small print on the sleeve. **Which aspects merit representation**: not the attributes a consumer application needs, but who worked with whom, and what the instrumental tracks sound like once the star's voice has been removed. The PASMA dataset is the material form of that answer; the [Dataset](dataset.html) page documents it.

## 2. Absence, not reduction

Born's deeper warning is ontological. Reducing music to classes, attributes and relations risks conflating epistemology with ontology, taking the data model for the thing itself and flattening the embodied and social existence of music into data [@Born2020]. The paper takes the warning seriously and argues for a reversal in one specific case.

For historically marginalized subjects such as the session musicians in our study, the situation is not one of *reduction* but of *absence*. They have never been encoded in any database at all. In an era in which what is not in the metadata does not circulate, is not searched, and is not cited, absence from metadata is tantamount to erasure from the historical record. For these workers, being inscribed into the very epistemological infrastructure that Born criticizes is precisely what grants them *digital existence*: a concrete presence in the computational record from which they had been excluded. The paper therefore appropriates MIR's knowledge-representation tools not as instruments of reduction but as a means of *ontological intervention*, restoring the historical existence of hidden labourers by making their collaborative ties visible and analysable for the first time.

Three things keep this from being a slogan.

First, the intervention is an **act, not a description**. Section 5.1 of the paper says it plainly: by encoding these workers into PASMA, modelling their ties as a network, and extracting their sonic traces through vocal separation and MERT embeddings, we have *created* their digital existence for the first time. The workers were historically present but digitally absent; after the study they exist in a form that can be linked, queried and argued with. That is what "ontological" means here. The claim is about existence in the record, not about what music ultimately is.

Second, the intervention needed **both instruments**. Archival reconstruction alone would re-inscribe the silences of an industry that did not name its workers; audio analysis alone would dissolve the historical specificity into a placeless acoustic record. Only the pairing lets the sound of the backstage be heard as the sound of particular people in a particular industry at a particular moment.

Third, we do not pretend the encoding is innocent. Fifteen role categories and five institution types are a reduction of hundreds of printed credit labels; a collaboration edge is a reduction of a working relationship; a MERT embedding is a reduction of a performance. The paper's position is that for the backstage this reduction is the price of existence, and that it is a price worth paying when the alternative is not a richer ontology but no entry at all. The [Historical Context](history.html) page is where the reduced record is reconnected to the lives it stands for.

## 3. The evidence that gives the claim substance

An intervention that only asserted existence would be a gesture. The paper's results are what make it a finding, and the structure of the evidence matters for the argument.

**Two methods that never met.** From the credits we built a collaboration network and measured it on five-year sliding windows; three structural properties that need not move together, local clustering, global connectedness and community modularity, turn in the same window, 1976 to 1978. From the recordings, with no dates given to the model, MERT embeddings of the vocal-separated stems split at 1978. The two paths share no data. Their convergence on the same watershed is not a methodological coincidence; it indicates that the social reorganization of backstage labour left measurable traces in the sound itself. The existence the dataset grants is therefore not arbitrary: the people it names form structures that the sound independently confirms.

**Archival silence as evidence.** The obvious objection is that the fragmented early network is an artefact of incomplete data: early liner notes did not credit technical staff. The paper accepts the concern and turns it around. In the pre-multitrack era, recording labour was not yet professionalized to the point where engineers and producers could demand credit; their absence from the sleeve reflects a real condition, not merely a documentation gap. The sudden, dense formalization of technical credits after 1978 captures the moment when backstage intermediaries, empowered by multitrack recording and organized through studio-based workflows, consolidated enough industrial power to be named. Silence in the archive is itself a historical fact about who could claim to exist.

**Technology is not a neutral tool.** The paper reads the transformation through the Social Construction of Technology [@Pinch1984] and through Horning's account of studio practice as a co-construction of technology and its users [@horning2013chasing]. In those terms the transition from silence to visibility is the moment a new relevant social group achieved *closure*: the stabilization of multitrack recording as a technology was inseparable from the stabilization of the social roles that operated it. Bourdieu's cultural intermediaries [@Bourdieu1993], the arrangers and engineers who became gatekeepers of production, are the people the network identifies as its bridges. The network's structural transformation and the archival transformation are two expressions of one process.

## 4. Agonistic interdisciplinarity, instantiated

Born's proposed remedy is agonistic interdisciplinarity: a mode of engagement in which computational and humanistic disciplines interact as equals, each capable of transforming the other's methods and assumptions [@Born2020]. The paper attempts to be an instance of it rather than a citation of it.

The research question originates in music history and labour studies: who actually made the music, and under what conditions. The computational tools, network analysis and audio embeddings, reveal patterns inaccessible to archival reading alone; no amount of reading liner notes would have dated the structural threshold to a two-year window, or shown that an arranger's social omnipresence has an acoustic counterpart. The historical framing, in turn, prevents those patterns from collapsing into decontextualized pattern recognition: the 1978 break is not a feature of a time series but the industrial adoption and standardization of a recording technology, with names, studios and policies attached. Each side changes what the other is entitled to claim.

What MIR gains from the exchange is a purpose its conventional applications neither anticipate nor accommodate: a historiographic one. The paper's closing sentence states the demand. If MIR is to diversify its objects and its methods, it must be willing to ask not only what algorithms can optimize, but what histories they can restore.

## 5. What remains open

The paper names its own limits, and the argument depends on keeping them in view. The dataset rests on the documentary practices of liner notes, which varied across labels and periods; the causal link between multitrack technology and network centralization cannot be fully disentangled from concurrent factors such as market growth, policy shifts and the entry of international labels; and the embedding evidence is visual, read from projections rather than tested statistically. None of these weakens the ontological claim, which concerns existence in the record. They do bound the historical claim, and the [Historical Context](history.html) page is our attempt to meet that bound with sources rather than with assertion.
