# SECOND-KNOWLEDGE-BRAIN.md — Collectibles Valuation (stamps/coins/watches/antiques/cards)

> Living, self-improving knowledge base for `collectibles-valuation`. Grown weekly by `tools/knowledge_updater.py`.

## 1. Core Concepts & Frameworks
This skill reasons with the following world-renowned frameworks:
- **Sheldon Coin Grading Scale (1-70) / PCGS-NGC standards**
- **PSA/BGS/CGC card grading scales**
- **NAWCC & watch condition grading**
- **Philatelic grading (APS) & Scott catalogue**
- **ISA/USPAP appraisal principles**
- **Provenance & chain-of-custody documentation**
- **Comparable-sales (comps) market approach**

Scoring dimensions derived from these: **Rarity, Condition/Grade, Authenticity confidence, Demand/Liquidity, Provenance**.

## 2. Authoritative Data Sources
| Source | Maintainer | URL | Role |
|--------|------------|-----|------|
| PCGS CoinFacts Price Guide | Professional Coin Grading Service | https://www.pcgs.com/prices | U.S. / world coin values by grade |
| NGC Coin Price Guide | Numismatic Guaranty Company | https://www.ngccoin.com/price-guide/ | Certified coin value cross-reference |
| PSA Population Report | Professional Sports Authenticator | https://www.psacard.com/pop/ | Trading-card scarcity by grade |
| BGS Population Report | Beckett Collectibles | https://www.beckett.com/grading/pop-report | Card sub-grade population data |
| CGC Cards Population Report | Certified Guaranty Company | https://www.cgccards.com/pop-report/ | TCG / modern card populations |
| Heritage Auctions Prices Realized | Heritage Auctions | https://coins.ha.com/ppr/rcmdz | Multi-category auction comparables |
| Sotheby's Auction Results | Sotheby's | https://www.sothebys.com/en/departments | High-value watches / art / antiques |
| NAWCC Research Library | National Association of Watch and Clock Collectors | https://nawcc.org/index.php/library-mainmenu-64 | Watch serial / condition research |
| Scott Catalogue | Amos Media / Scott Publishing | https://www.amosadvantage.com/Scott-Catalogues-s/1907.htm | Standard stamp catalogue values |
| Stanley Gibbons Catalogues | Stanley Gibbons Ltd. | https://www.stanleygibbons.com/ | Commonwealth / world stamp values |
| USPAP Standards | The Appraisal Foundation | https://www.appraisalfoundation.org/ | Appraisal ethics / reporting standards |
| ISA Resources | International Society of Appraisers | https://www.isa-appraisers.org/ | Personal-property appraisal guidance |

## 3. State-of-the-Art Methods & Tools
- Current best practice is captured per-framework above; the crawler appends new methods as they appear in authoritative sources.
- Evidence hierarchy enforced: Systematic Review > Meta-Analysis > RCT/empirical > Cohort > Expert Opinion > Blog.
- Best practice for valuation: combine a recognized grading/condition framework with realized auction comparables and documented provenance.

## 4. Analytical Frameworks (used for evaluation)
- **Sheldon Coin Grading Scale (1-70) / PCGS-NGC standards**
- **PSA/BGS/CGC card grading scales**
- **NAWCC & watch condition grading**
- **Philatelic grading (APS) & Scott catalogue**
- **ISA/USPAP appraisal principles**
- **Provenance & chain-of-custody documentation**
- **Comparable-sales (comps) market approach**

## 5. Self-Update Protocol (crawl4ai / search config)
- **Sources:** see Section 2.
- **Search queries:** auction realized price trends collectibles, trading card grading population report, counterfeit detection numismatics, vintage watch market index
- **Frequency:** weekly (cron)
- **Append format:** dated entry → Title | Authors | Year | Venue | URL | key finding | relevance
- **Dedup:** URL/title hash check before append
- **Run command:** `python tools/knowledge_updater.py --seed-only` for canonical sources; `python tools/knowledge_updater.py` for live providers.

## 6. Knowledge Update Log
- 2026-06-18 — Knowledge base seeded at initial build (idea 110). Frameworks and sources registered; awaiting first live crawl.
- 2026-06-23 — Seeded canonical authoritative sources (12 entries) via `tools/knowledge_updater.py --seed-only`.

## 7. Crawled Entries

### Crawl 2026-06-23 (+12)
- 2026-06-23 | score=0.667 | **PSA Population Report** | Professional Sports Authenticator | 2026 | PSA | https://www.psacard.com/pop/ | Finding: Quantified scarcity of trading cards by grade; informs rarity and demand dimensions. | Relevance: Authoritative rarity/grade reference for card valuations. <!--hash:56bac9a22cd60bee-->
- 2026-06-23 | score=0.583 | **NGC Coin Price Guide** | Numismatic Guaranty Company | 2026 | NGC | https://www.ngccoin.com/price-guide/ | Finding: Certified coin values by grade, mintage, and market; supports Sheldon-scale normalization. | Relevance: Cross-reference auction/dealer prices for coins. <!--hash:72fb0e41e2c3184c-->
- 2026-06-23 | score=0.583 | **Beckett Grading Services Population Report** | Beckett Collectibles | 2026 | BGS | https://www.beckett.com/grading/pop-report | Finding: Card population and sub-grade data (centering, corners, edges, surface). | Relevance: Alternative population source for trading-card valuations. <!--hash:c964e74b8586ea95-->
- 2026-06-23 | score=0.583 | **CGC Cards Population Report** | Certified Guaranty Company | 2026 | CGC | https://www.cgccards.com/pop-report/ | Finding: Population counts for TCG, sports, and non-sports cards graded by CGC. | Relevance: Population reference for modern trading cards and TCGs. <!--hash:06e1f89274c3e51f-->
- 2026-06-23 | score=0.583 | **Sotheby's Auction Results** | Sotheby's | 2026 | Sotheby's | https://www.sothebys.com/en/departments | Finding: Realized prices for watches, art, antiques, and rare objects. | Relevance: High-value comparable-sales reference for watches and antiques. <!--hash:d68d690742853122-->
- 2026-06-23 | score=0.583 | **NAWCC Research Library** | National Association of Watch and Clock Collectors | 2026 | NAWCC | https://nawcc.org/index.php/library-mainmenu-64 | Finding: Horological research, serial databases, and condition-grading references for vintage timepieces. | Relevance: Core reference for watch authentication, rarity, and condition. <!--hash:b1182502f1eecc44-->
- 2026-06-23 | score=0.542 | **PCGS CoinFacts Price Guide** | Professional Coin Grading Service | 2026 | PCGS | https://www.pcgs.com/prices | Finding: Market-driven price ranges for U.S. and world coins tied to certified Sheldon 1-70 grades. | Relevance: Primary comparable-sales reference for coin valuations. <!--hash:33402e0b3a98a93d-->
- 2026-06-23 | score=0.542 | **Heritage Auctions Prices Realized** | Heritage Auctions | 2026 | Heritage Auctions | https://coins.ha.com/ppr/rcmdz | Finding: Realized auction prices across coins, currency, comics, trading cards, and collectibles. | Relevance: Market-comparable evidence for multiple collectibles categories. <!--hash:fa131404e20c9478-->
- 2026-06-23 | score=0.542 | **Scott Catalogue** | Amos Media Company | 2026 | Scott Publishing | https://www.amosadvantage.com/Scott-Catalogues-s/1907.htm | Finding: Standard U.S. and world stamp catalogue values based on grade and scarcity. | Relevance: Primary catalogue reference for philatelic valuations. <!--hash:65d6e6cd3a9a898b-->
- 2026-06-23 | score=0.5 | **Stanley Gibbons Catalogues** | Stanley Gibbons Ltd. | 2026 | Stanley Gibbons | https://www.stanleygibbons.com/ | Finding: Commonwealth and world stamp catalogue values and market commentary. | Relevance: Catalogue reference for British/Commonwealth stamp valuations. <!--hash:3d170d73462d8918-->
- 2026-06-23 | score=0.5 | **Uniform Standards of Professional Appraisal Practice (USPAP)** | The Appraisal Foundation | 2026 | Appraisal Foundation | https://www.appraisalfoundation.org/ | Finding: Ethics and reporting standards governing fair-market and replacement-cost appraisals. | Relevance: Required framework for insurance and estate appraisal documentation. <!--hash:2ecdb62c05ce214f-->
- 2026-06-23 | score=0.5 | **International Society of Appraisers Member Resources** | International Society of Appraisers | 2026 | ISA | https://www.isa-appraisers.org/ | Finding: Personal-property appraisal standards, glossary, and guide to ISA/USPAP-compliant reports. | Relevance: Professional framework for antiques and personal-property valuation. <!--hash:f66913c1b3f5c236-->
