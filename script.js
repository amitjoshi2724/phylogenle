/**
 * Phylogenle - Daily Evolutionary Puzzle Engine
 * Manages daily challenge generation, autocomplete, tree visualization with
 * dynamic font scaling and vertical label staggering, archive calendar, and stats.
 */
import { 
    getTodayDateStr, 
    getPuzzleNumber, 
    getDateForPuzzleNumber,
    getDailyTargetSpecies, 
    parseDate, 
    formatDate,
    getAliasesForSpecies,
    getTargetPresentationName,
    extractScientificName,
    EPOCH_DATE_STR
} from './prng.js?v=tree_order_4';
import { 
    recordDailyCompletion, 
    recordPracticeCompletion,
    getStats, 
    getHistory, 
    getAllGamesLedger,
    getRecordForDate, 
    saveActiveGuesses, 
    loadActiveGuesses, 
    clearActiveGuesses,
    saveActiveHints,
    loadActiveHints,
    clearActiveHints,
    resetDateRecord,
    resetAllHistory,
    onStorageChange
} from './storage.js';
import { getCurrentUser, onAuthChange } from './auth.js'; // Initializes Google Auth singleton & UI

function bootPhylogenle() {
    // DOM Elements
    const inputSection = document.getElementById('input-section') || document.querySelector('.input-section');
    const animalInput = document.getElementById('animal-input');
    const autocompleteList = document.getElementById('autocomplete-list');
    const guessBtn = document.getElementById('guess-btn');
    const giveUpBtn = document.getElementById('give-up-btn');
    const guessesContainer = document.getElementById('guesses-container');
    const gameEndPanel = document.getElementById('game-end-panel');
    const endTitle = document.getElementById('end-title');
    const endMessage = document.getElementById('end-message');
    const playAgainBtn = document.getElementById('play-again-btn');
    const shareResultBtn = document.getElementById('share-result-btn');
    const puzzleBadge = document.getElementById('puzzle-badge');
    const modeDailyBtn = document.getElementById('mode-daily-btn');
    const modePracticeBtn = document.getElementById('mode-practice-btn');
    const targetAlertContainer = document.getElementById('target-alert-container');
    const treeContainer = document.getElementById('tree-container');
    const hintBtn = document.getElementById('hint-btn');
    const hintsCard = document.getElementById('hints-card');
    const hintsList = document.getElementById('hints-list');
    const hintsCountBadge = document.getElementById('hints-count-badge');

    // Modals
    const archiveModal = document.getElementById('archive-modal');
    const statsModal = document.getElementById('stats-modal');
    const helpModal = document.getElementById('help-modal');
    const catalogModal = document.getElementById('catalog-modal');
    const catalogNavBtn = document.getElementById('catalog-nav-btn');
    const catalogBottomBtn = document.getElementById('catalog-bottom-btn');
    const catalogSearchInput = document.getElementById('catalog-search-input');
    const catalogSearchClear = document.getElementById('catalog-search-clear');
    const catalogCladeTabs = document.getElementById('catalog-clade-tabs');
    const catalogContent = document.getElementById('catalog-content');

    // Game State
    let isUnlimited = false;
    let currentDateStr = getTodayDateStr();
    let puzzleNum = getPuzzleNumber(currentDateStr);
    let allSpecies = [];
    let speciesAliases = null;
    let targetSpecies = "";
    let targetPresentationName = "";
    let targetData = {};
    let phylogenyTree = null;
    let currentFocus = -1;
    let guesses = [];
    let guessedSet = new Set();
    let revealedHints = [];
    let isGameOver = false;

    // HTML escape helper
    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Wikipedia Normalization Helper
    function getNormalizedWikiTitle(title) {
        if (!title) return '';
        const clean = title.trim();
        const lower = clean.toLowerCase();
        if (lower === 'root' || lower === 'root (luca)' || lower === 'cellular organisms' || lower === 'luca' || lower === 'life') {
            return 'Last_universal_common_ancestor';
        }
        return clean;
    }

    // Catalog state
    let catalogLoaded = false;
    let catalogMarkdownText = "";
    let catalogSections = {};
    let catalogTaxonomyData = null;
    let currentCatalogClade = "tree";
    let catalogSearchDebounce = null;

    // Calendar state
    const todayObj = parseDate(currentDateStr);
    let calYear = todayObj.getFullYear();
    let calMonth = todayObj.getMonth();

    // Wikipedia Tooltip Setup
    const wikiTooltip = document.getElementById('wiki-tooltip');
    const wikiTitle = wikiTooltip ? wikiTooltip.querySelector('.wiki-title') : null;
    const wikiSnippet = wikiTooltip ? wikiTooltip.querySelector('.wiki-snippet') : null;
    const wikiCatalogBtn = document.getElementById('wiki-catalog-btn');
    let tooltipTimeout;
    let currentTooltipTaxon = '';

    async function showWikiTooltip(e, rankName) {
        if (!wikiTooltip) return;
        clearTimeout(tooltipTimeout);
        currentTooltipTaxon = rankName || '';
        wikiTooltip.classList.remove('hidden');
        
        let left = e.pageX + 10;
        let top = e.pageY + 10;
        
        if (left + 320 > window.innerWidth) {
            left = Math.max(10, window.innerWidth - 330);
        }
        
        wikiTooltip.style.left = left + 'px';
        wikiTooltip.style.top = top + 'px';
        wikiTooltip.style.pointerEvents = 'auto';

        const normQuery = getNormalizedWikiTitle(rankName);
        const lowerName = (rankName || '').trim().toLowerCase();
        const displayTitle = (lowerName === 'root' || lowerName === 'root (luca)' || lowerName === 'cellular organisms' || lowerName === 'luca')
            ? 'Root (LUCA)'
            : rankName;
        
        if (wikiTitle) {
            wikiTitle.innerHTML = `<a href="https://en.wikipedia.org/wiki/${encodeURIComponent(normQuery)}" target="_blank">${displayTitle} &#8594;</a>`;
        }
        if (wikiSnippet) {
            wikiSnippet.textContent = "Loading summary...";
        }

        try {
            const resp = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(normQuery)}`);
            const data = await resp.json();
            if (wikiSnippet) {
                if (data.extract) {
                    wikiSnippet.textContent = data.extract.substring(0, 180) + "...";
                } else {
                    wikiSnippet.textContent = "No Wikipedia summary available.";
                }
            }
        } catch (err) {
            if (wikiSnippet) {
                wikiSnippet.textContent = "Error loading summary.";
            }
        }
    }

    function hideWikiTooltip() {
        if (!wikiTooltip) return;
        tooltipTimeout = setTimeout(() => {
            wikiTooltip.classList.add('hidden');
            wikiTooltip.style.pointerEvents = 'none';
        }, 350);
    }

    if (wikiTooltip) {
        wikiTooltip.addEventListener('mouseenter', () => clearTimeout(tooltipTimeout));
        wikiTooltip.addEventListener('mouseleave', hideWikiTooltip);
    }

    if (wikiCatalogBtn) {
        wikiCatalogBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const targetTaxon = currentTooltipTaxon;
            hideWikiTooltip();
            if (targetTaxon) {
                openCatalogAtTaxon(targetTaxon);
            } else {
                openCatalogModal();
            }
        });
    }

    // Check URL parameters and persisted mode on load
    function checkURLParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const modeParam = urlParams.get('mode');
        const dateParam = urlParams.get('date');
        const savedMode = localStorage.getItem('phylogenle_game_mode');

        if (modeParam === 'unlimited' || modeParam === 'practice') {
            isUnlimited = true;
            localStorage.setItem('phylogenle_game_mode', 'practice');
        } else if (modeParam === 'daily') {
            isUnlimited = false;
            localStorage.setItem('phylogenle_game_mode', 'daily');
        } else if (dateParam && /^\d{4}-\d{2}-\d{2}$/.test(dateParam)) {
            currentDateStr = dateParam;
            puzzleNum = getPuzzleNumber(dateParam);
            isUnlimited = false;
            localStorage.setItem('phylogenle_game_mode', 'daily');
        } else if (savedMode === 'practice') {
            isUnlimited = true;
            const newUrl = window.location.pathname + '?mode=practice';
            window.history.replaceState(null, '', newUrl);
        } else {
            isUnlimited = false;
            localStorage.setItem('phylogenle_game_mode', 'daily');
        }
        updateModeUI();
    }

    function updateModeUI() {
        if (isUnlimited) {
            if (modeDailyBtn) {
                modeDailyBtn.classList.remove('active');
                modeDailyBtn.setAttribute('aria-checked', 'false');
            }
            if (modePracticeBtn) {
                modePracticeBtn.classList.add('active');
                modePracticeBtn.setAttribute('aria-checked', 'true');
            }
            if (puzzleBadge) puzzleBadge.textContent = 'PRACTICE MODE 🧬';
        } else {
            if (modeDailyBtn) {
                modeDailyBtn.classList.add('active');
                modeDailyBtn.setAttribute('aria-checked', 'true');
            }
            if (modePracticeBtn) {
                modePracticeBtn.classList.remove('active');
                modePracticeBtn.setAttribute('aria-checked', 'false');
            }
            const isToday = currentDateStr === getTodayDateStr();
            if (puzzleBadge) {
                puzzleBadge.textContent = `DAILY #${puzzleNum} • ${currentDateStr}${isToday ? ' (TODAY)' : ''}`;
            }
        }
    }

    // Initialize Game
    async function initGame() {
        try {
            if (allSpecies.length === 0 || !phylogenyTree || !speciesAliases) {
                if (guessesContainer && guessesContainer.children.length === 0) {
                    guessesContainer.innerHTML = `<div class="loading-state" style="text-align: center; padding: 2rem; color: var(--text-secondary);"><span style="display:inline-block; font-size: 1.5rem; animation: spin 1.2s linear infinite; margin-bottom: 0.5rem;">🧬</span><br>Loading evolutionary tree of life...</div>`;
                }

                const [speciesResp, treeResp, aliasesResp] = await Promise.all([
                    allSpecies.length === 0 ? fetch('data/species_list.json?v=taxa_v1') : Promise.resolve(null),
                    !phylogenyTree ? fetch('data/phylogeny_tree.json?v=taxa_v1') : Promise.resolve(null),
                    !speciesAliases ? fetch('data/species_aliases.json?v=taxa_v1') : Promise.resolve(null)
                ]);

                if (speciesResp) {
                    if (!speciesResp.ok) throw new Error(`HTTP ${speciesResp.status} loading species list`);
                    allSpecies = await speciesResp.json();
                }

                if (treeResp) {
                    if (!treeResp.ok) throw new Error(`HTTP ${treeResp.status} loading phylogeny tree`);
                    phylogenyTree = await treeResp.json();
                    buildCatalogCladeIndex();
                }

                if (aliasesResp) {
                    if (aliasesResp.ok) {
                        speciesAliases = await aliasesResp.json();
                        window.speciesAliases = speciesAliases;
                    }
                }
            }

            if (isUnlimited) {
                targetSpecies = allSpecies[Math.floor(Math.random() * allSpecies.length)];
                targetPresentationName = getTargetPresentationName(targetSpecies, speciesAliases, Date.now() + "_" + Math.random().toString(36).slice(2));
            } else {
                targetSpecies = getDailyTargetSpecies(allSpecies, currentDateStr);
                targetPresentationName = getTargetPresentationName(targetSpecies, speciesAliases, currentDateStr);
            }
            window.targetSpecies = targetSpecies;
            window.targetPresentationName = targetPresentationName;

            // Reset round variables
            guesses = [];
            guessedSet = new Set();
            revealedHints = [];
            isGameOver = false;
            guessesContainer.innerHTML = '';
            gameEndPanel.classList.add('hidden');
            renderHintsCard();
            if (inputSection) inputSection.style.display = 'flex';
            if (animalInput && animalInput.parentElement) animalInput.parentElement.style.display = '';
            if (guessBtn) guessBtn.style.display = '';
            if (giveUpBtn) giveUpBtn.style.display = '';
            if (hintBtn) hintBtn.style.display = '';
            if (animalInput) animalInput.value = '';

            if (targetAlertContainer) targetAlertContainer.innerHTML = '';

            updateModeUI();

            // If daily, check if already completed
            if (!isUnlimited) {
                const existing = getRecordForDate(currentDateStr);
                if (existing && existing.completed) {
                    restoreCompletedGame(existing);
                    return;
                }

                // Check for in-progress saved guesses and previous target species
                const activeData = loadActiveGuesses(currentDateStr);
                let activeGuesses = null;
                let savedTargetSpecies = null;
                if (activeData) {
                    if (Array.isArray(activeData)) {
                        activeGuesses = activeData;
                    } else if (activeData.guesses) {
                        activeGuesses = activeData.guesses;
                        savedTargetSpecies = activeData.targetSpecies || null;
                    }
                }

                // Check if target changed compared to the active saved session
                if (savedTargetSpecies && savedTargetSpecies !== targetSpecies && activeGuesses && activeGuesses.length > 0) {
                    if (targetAlertContainer) {
                        targetAlertContainer.innerHTML = `
                            <div class="target-mismatch-banner">
                                <div style="font-size: 1.5rem; line-height: 1;">⚠️</div>
                                <div class="mismatch-content">
                                    <strong>Target Organism Updated</strong>
                                    <p>The daily target organism has changed since your last active session. You can continue or restart the puzzle fresh.</p>
                                </div>
                                <button type="button" id="target-mismatch-restart-btn" class="restart-pill-btn">🔄 Restart Puzzle</button>
                            </div>
                        `;
                        const restartBtn = document.getElementById('target-mismatch-restart-btn');
                        if (restartBtn) {
                            restartBtn.addEventListener('click', () => {
                                clearActiveGuesses(currentDateStr);
                                clearActiveHints(currentDateStr);
                                initGame();
                            });
                        }
                    }
                }

                // Check for in-progress saved hints with sanity check against targetSpecies
                const activeHints = loadActiveHints(currentDateStr);
                if (activeHints && Array.isArray(activeHints) && activeHints.length > 0) {
                    const targetRanks = getTargetTaxonomyRanks();
                    // Keep only hints that belong to the active target species
                    const validHints = activeHints.filter(h => {
                        if (h.type === 'species') {
                            const common = (targetPresentationName || targetSpecies.split(' (')[0]).trim();
                            return h.name.includes(`"${common[0]}"`);
                        }
                        return targetRanks[h.rank] && targetRanks[h.rank].name.toLowerCase() === h.name.toLowerCase();
                    });
                    revealedHints = validHints;
                    saveActiveHints(currentDateStr, revealedHints);
                }

                // Interleave active guesses and revealed hints chronologically
                const timeline = [];
                if (activeGuesses && activeGuesses.length > 0) {
                    activeGuesses.forEach((g, idx) => {
                        timeline.push({
                            type: 'guess',
                            data: g,
                            time: g.timestamp || (idx * 2)
                        });
                    });
                }
                if (revealedHints && revealedHints.length > 0) {
                    revealedHints.forEach((h, idx) => {
                        timeline.push({
                            type: 'hint',
                            data: h,
                            hintNumber: idx + 1,
                            time: h.timestamp || (idx * 2 + 1)
                        });
                    });
                }

                if (timeline.length > 0) {
                    guessesContainer.innerHTML = '';
                    timeline.sort((a, b) => a.time - b.time);
                    timeline.forEach(item => {
                        if (item.type === 'guess') {
                            const g = item.data;
                            const guessKey = g.name.toLowerCase();
                            guessedSet.add(guessKey);
                            if (!guesses.some(x => x.name.toLowerCase() === guessKey)) {
                                guesses.push(g);
                            }
                            addGuessToBoard(g.name, g.wikiTitle, {
                                rank: g.lca_rank,
                                lca_name: g.lca_name,
                                major_name: g.major_name || g.lca_name,
                                time: g.tmrca
                            }, g.isMatch, g.guessedAlias);
                        } else {
                            addHintToBoard(item.data, item.hintNumber);
                        }
                    });
                    updateTree();
                    return;
                }
            }

            if (revealedHints.length > 0) {
                updateTree();
            } else {
                drawTree({ name: "?", children: [] });
            }
        } catch (error) {
            console.error("Failed to initialize game:", error);
            guessesContainer.innerHTML = `<div class="error" style="color: #ef4444; padding: 1rem;">Failed to load game data. Please run via a local web server (http://).</div>`;
        }
    }

    function restoreCompletedGame(record) {
        isGameOver = true;
        if (inputSection) inputSection.style.display = 'none';

        if (record.hints && record.hints.length > 0) {
            revealedHints = [...record.hints];
        } else {
            revealedHints = [];
        }

        const hintCount = revealedHints.length;
        const hintSuffix = hintCount > 0 ? ` (${hintCount} hint${hintCount === 1 ? '' : 's'})` : '';

        const finishedTarget = record.targetSpecies || targetSpecies;
        const canonicalCommon = finishedTarget.split(' (')[0];
        const allAliases = getAliasesForSpecies(finishedTarget, speciesAliases);
        const presName = getTargetPresentationName(finishedTarget, speciesAliases, currentDateStr);

        let aliasInfoHtml = '';
        if (presName && presName.toLowerCase() !== canonicalCommon.toLowerCase()) {
            aliasInfoHtml += `<div style="font-size: 0.85rem; color: #a5b4fc; margin-top: 4px;">Featured round presentation name: <strong>${escapeHtml(presName)}</strong></div>`;
        }
        if (allAliases && allAliases.length > 0) {
            const otherAliases = allAliases.filter(a => a.toLowerCase() !== presName.toLowerCase());
            if (otherAliases.length > 0) {
                aliasInfoHtml += `<div style="font-size: 0.8rem; opacity: 0.85; color: var(--text-secondary); margin-top: 2px;">Also known as: <em>${escapeHtml(otherAliases.join(', '))}</em></div>`;
            }
        }

        endTitle.textContent = record.solved ? "You found it! ⭐" : "Organism Revealed";
        endTitle.style.color = record.solved ? "var(--success-color)" : "var(--danger-color)";
        endMessage.innerHTML = `The organism was <strong>${finishedTarget}</strong>.<br>` +
            aliasInfoHtml +
            `<span style="font-size: 0.9rem; color: var(--text-secondary); display: inline-block; margin-top: 6px;">${record.solved ? `Solved in ${record.guessCount} guess${record.guessCount === 1 ? '' : 'es'}${hintSuffix}!` : 'Gave up.'}</span>`;

        const endEmojisRow = document.getElementById('end-emojis-row');
        if (endEmojisRow && record.guesses && record.guesses.length > 0) {
            let emojis = getGameTimelineEmojis(record.guesses, revealedHints);
            if (!record.solved) {
                emojis += ' ⬜'; // White square indicates surrendered / revealed
            }
            endEmojisRow.textContent = emojis;
        }
        gameEndPanel.classList.remove('hidden');

        if (record.guesses && record.guesses.length > 0) {
            guessesContainer.innerHTML = "";
            guesses = [];
            guessedSet.clear();

            // Interleave guesses and hints chronologically
            const timeline = [];
            record.guesses.forEach((g, idx) => {
                timeline.push({
                    type: 'guess',
                    data: g,
                    time: g.timestamp || (idx * 2)
                });
            });
            revealedHints.forEach((h, idx) => {
                timeline.push({
                    type: 'hint',
                    data: h,
                    hintNumber: idx + 1,
                    time: h.timestamp || (idx * 2 + 1)
                });
            });
            timeline.sort((a, b) => a.time - b.time);

            timeline.forEach(item => {
                if (item.type === 'guess') {
                    const g = item.data;
                    const guessKey = g.name.toLowerCase();
                    guessedSet.add(guessKey);
                    guesses.push(g);
                    addGuessToBoard(g.name, g.wikiTitle, {
                        rank: g.lca_rank,
                        lca_name: g.lca_name,
                        major_name: g.major_name || g.lca_name,
                        time: g.tmrca
                    }, g.isMatch, g.guessedAlias);
                } else {
                    addHintToBoard(item.data, item.hintNumber);
                }
            });
            if (!record.solved) {
                addSurrenderRow(record.targetSpecies || targetSpecies);
            }
            updateTree();
        } else {
            const latinMatch = (record.targetSpecies || targetSpecies).match(/\((.*?)\)/);
            const name = (record.targetSpecies || targetSpecies).split(' (')[0];
            const wiki = latinMatch ? latinMatch[1] : name;
            drawTree({
                name: "Animalia",
                rank: "Kingdom",
                isTrunk: true,
                children: [{
                    name: name,
                    wikiTitle: wiki,
                    isMystery: true,
                    isMatch: record.solved,
                    emoji: record.solved ? (getGenusFromEntry(record.targetSpecies || targetSpecies) ? '🟨' : '🟩') : '⬜'
                }]
            });
        }
    }

    // ==========================================================================
    // Feature 2: High-Performance Progressive Infinite-Scroll Autocomplete
    // ==========================================================================
    let currentFilteredCandidates = [];
    let renderedBatchCount = 0;
    const AUTOCOMPLETE_BATCH_SIZE = 120;

    function renderAutocompleteBatch() {
        if (!currentFilteredCandidates || renderedBatchCount >= currentFilteredCandidates.length) {
            updateAutocompleteInfo();
            return;
        }
        const val = animalInput.value.toLowerCase().trim();
        const nextBatch = currentFilteredCandidates.slice(renderedBatchCount, renderedBatchCount + AUTOCOMPLETE_BATCH_SIZE);
        let batchHTML = '';

        for (let i = 0; i < nextBatch.length; i++) {
            const item = nextBatch[i];
            const species = typeof item === 'string' ? item : item.species;
            const matchedAlias = (typeof item === 'object' && item.matchedAlias) ? item.matchedAlias : '';
            const aliasTag = matchedAlias
                ? ` <span class="alias-tag" style="opacity: 0.75; font-size: 0.85em; font-style: italic; color: #a5b4fc;">(aka ${escapeHtml(matchedAlias)})</span>`
                : '';
            let displayHtml = species;
            if (val) {
                const idx = species.toLowerCase().indexOf(val);
                if (idx !== -1) {
                    displayHtml = species.substring(0, idx) + "<strong>" + species.substring(idx, idx + val.length) + "</strong>" + species.substring(idx + val.length);
                }
            }
            displayHtml += aliasTag;

            const aliasAttr = matchedAlias ? ` data-alias="${escapeHtml(matchedAlias)}"` : '';
            if (guessedSet.has(species.toLowerCase())) {
                batchHTML += `<li class="autocomplete-item guessed-item" style="opacity: 0.45; pointer-events: none; cursor: default;" data-value="${escapeHtml(species)}"${aliasAttr}>${displayHtml} (Already Guessed)</li>`;
            } else {
                batchHTML += `<li class="autocomplete-item" data-value="${escapeHtml(species)}"${aliasAttr}>${displayHtml}</li>`;
            }
        }

        renderedBatchCount += nextBatch.length;

        // Remove old counter indicator before appending next batch
        const oldCounter = autocompleteList.querySelector('.autocomplete-counter');
        if (oldCounter) oldCounter.remove();

        autocompleteList.insertAdjacentHTML('beforeend', batchHTML);
        updateAutocompleteInfo();
    }

    function updateAutocompleteInfo() {
        const total = currentFilteredCandidates.length;
        if (total <= 10) return;
        let infoEl = autocompleteList.querySelector('.autocomplete-counter');
        if (!infoEl) {
            infoEl = document.createElement('div');
            infoEl.className = 'autocomplete-counter';
            autocompleteList.appendChild(infoEl);
        } else {
            autocompleteList.appendChild(infoEl);
        }

        if (renderedBatchCount < total) {
            infoEl.textContent = `Showing ${renderedBatchCount.toLocaleString()} of ${total.toLocaleString()} organisms (scroll for more)`;
        } else {
            infoEl.textContent = `All ${total.toLocaleString()} matching organisms loaded`;
        }
    }

    // Toggle Dropdown with complete filtering
    function showDropdown() {
        if (isGameOver) return;
        const val = animalInput.value.toLowerCase().trim();

        if (!val) {
            currentFilteredCandidates = allSpecies;
        } else {
            const exactCommon = [];
            const exactSci = [];
            const headNounMatches = [];
            const prefixWordMatches = [];
            const prefixMatches = [];
            const wordMatches = [];
            const subMatches = [];

            const seenSpecies = new Set();

            for (let i = 0; i < allSpecies.length; i++) {
                const species = allSpecies[i];
                const sLower = species.toLowerCase();
                const idx = sLower.indexOf(val);
                if (idx === -1) continue;

                const common = sLower.split(' (')[0];
                const sci = extractScientificName(sLower);

                seenSpecies.add(sLower);

                if (common === val) {
                    exactCommon.push(species);
                } else if (sci === val) {
                    exactSci.push(species);
                } else if (common.endsWith(' ' + val) || common.endsWith('-' + val)) {
                    headNounMatches.push(species);
                } else if (common.startsWith(val + ' ') || common.startsWith(val + '-')) {
                    prefixWordMatches.push(species);
                } else if (idx === 0) {
                    prefixMatches.push(species);
                } else if (sLower[idx - 1] === ' ' || sLower[idx - 1] === '(' || sLower[idx - 1] === '-') {
                    wordMatches.push(species);
                } else {
                    subMatches.push(species);
                }
            }

            const exactAliasMatches = [];
            const partialAliasMatches = [];
            if (speciesAliases && val.length >= 2) {
                for (const [alias, canonical] of Object.entries(speciesAliases)) {
                    const aLower = alias.toLowerCase();
                    const aIdx = aLower.indexOf(val);
                    if (aIdx !== -1) {
                        const canLower = canonical.toLowerCase();
                        if (!seenSpecies.has(canLower)) {
                            seenSpecies.add(canLower);
                            const aliasObj = {
                                species: canonical,
                                matchedAlias: alias
                            };
                            if (aLower === val || aLower.endsWith(' ' + val)) {
                                exactAliasMatches.push(aliasObj);
                            } else {
                                partialAliasMatches.push(aliasObj);
                            }
                        }
                    }
                }
            }

            currentFilteredCandidates = [
                ...exactCommon,
                ...exactAliasMatches,
                ...exactSci,
                ...headNounMatches,
                ...prefixWordMatches,
                ...prefixMatches,
                ...partialAliasMatches,
                ...wordMatches,
                ...subMatches
            ];
        }

        autocompleteList.innerHTML = '';
        renderedBatchCount = 0;

        if (currentFilteredCandidates.length > 0) {
            renderAutocompleteBatch();
            autocompleteList.classList.add('active');
            autocompleteList.scrollTop = 0;
        } else {
            closeDropdown();
        }
        currentFocus = -1;
    }

    function closeDropdown() {
        autocompleteList.innerHTML = '';
        autocompleteList.classList.remove('active');
        currentFocus = -1;
    }

    // Event delegation on autocompleteList for silky-smooth item selection
    const handleAutocompleteSelect = (e) => {
        const item = e.target.closest('.autocomplete-item');
        if (item && !item.classList.contains('guessed-item')) {
            e.preventDefault();
            animalInput.value = item.getAttribute('data-value');
            const aliasAttr = item.getAttribute('data-alias');
            if (aliasAttr) {
                animalInput.dataset.matchedAlias = aliasAttr;
            } else {
                delete animalInput.dataset.matchedAlias;
            }
            closeDropdown();
            handleGuess();
        }
    };
    autocompleteList.addEventListener('mousedown', handleAutocompleteSelect);
    autocompleteList.addEventListener('click', handleAutocompleteSelect);

    // Infinite scroll listener: renders next batch when near bottom of scroll container
    autocompleteList.addEventListener('scroll', () => {
        if (autocompleteList.scrollTop + autocompleteList.clientHeight >= autocompleteList.scrollHeight - 160) {
            renderAutocompleteBatch();
        }
    });

    animalInput.addEventListener('click', showDropdown);
    animalInput.addEventListener('input', showDropdown);
    animalInput.addEventListener('keyup', (e) => {
        if (e.keyCode !== 38 && e.keyCode !== 40 && e.keyCode !== 13) {
            showDropdown();
        }
    });
    animalInput.addEventListener('focus', showDropdown);

    document.addEventListener('click', (e) => {
        if (!animalInput.contains(e.target) && !autocompleteList.contains(e.target)) {
            closeDropdown();
        }
    });

    animalInput.addEventListener('keydown', (e) => {
        let x = autocompleteList.getElementsByClassName('autocomplete-item');
        if (e.keyCode === 40) { // Down
            currentFocus++;
            if (currentFocus >= x.length - 4 && renderedBatchCount < currentFilteredCandidates.length) {
                renderAutocompleteBatch();
                x = autocompleteList.getElementsByClassName('autocomplete-item');
            }
            addActive(x);
        } else if (e.keyCode === 38) { // Up
            currentFocus--;
            addActive(x);
        } else if (e.keyCode === 13) { // Enter
            e.preventDefault();
            if (currentFocus > -1 && x && x[currentFocus]) {
                const val = x[currentFocus].getAttribute('data-value');
                const aliasAttr = x[currentFocus].getAttribute('data-alias');
                if (val) {
                    animalInput.value = val;
                    if (aliasAttr) {
                        animalInput.dataset.matchedAlias = aliasAttr;
                    } else {
                        delete animalInput.dataset.matchedAlias;
                    }
                    closeDropdown();
                    handleGuess();
                }
            } else if (animalInput.value) {
                closeDropdown();
                handleGuess();
            }
        }
    });

    function addActive(x) {
        if (!x || x.length === 0) return false;
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        x[currentFocus].classList.add('selected');
        x[currentFocus].scrollIntoView({ block: 'nearest' });
    }

    function removeActive(x) {
        for (let i = 0; i < x.length; i++) {
            x[i].classList.remove('selected');
        }
    }

    // Known special higher taxa & genuses in Phylogenle
    const SPECIAL_GENUS_MAP = {

        'fiddler crab (ocypodidae)': { genus: 'Ocypodidae', common: 'Fiddler Crab', sciLower: 'ocypodidae', rank: 'Family' },
        'barn owl (tyto)': { genus: 'Tyto', common: 'Barn Owl', sciLower: 'tyto', rank: 'Genus' },
        'electric eel (electrophorus)': { genus: 'Electrophorus', common: 'Electric Eel', sciLower: 'electrophorus', rank: 'Genus' },
        'leafcutter ant (atta)': { genus: 'Atta', common: 'Leafcutter Ant', sciLower: 'atta', rank: 'Genus' },
        'goliath beetle (goliathus)': { genus: 'Goliathus', common: 'Goliath Beetle', sciLower: 'goliathus', rank: 'Genus' },
        'black widow spider (latrodectus)': { genus: 'Latrodectus', common: 'Black Widow Spider', sciLower: 'latrodectus', rank: 'Genus' },
        'sea lion (otariinae)': { genus: 'Otariinae', common: 'Sea Lion', sciLower: 'otariinae', rank: 'Subfamily' },
        'comb jelly (ctenophora)': { genus: 'Ctenophora', common: 'Comb Jelly', sciLower: 'ctenophora', rank: 'Phylum' },
        'pufferfish (tetraodontidae)': { genus: 'Tetraodontidae', common: 'Pufferfish', sciLower: 'tetraodontidae', rank: 'Family' },
        'bearded dragon (pogona)': { genus: 'Pogona', common: 'Bearded Dragon', sciLower: 'pogona', rank: 'Genus' },
        'clawed frog (xenopus)': { genus: 'Xenopus', common: 'Clawed Frog', sciLower: 'xenopus', rank: 'Genus' },
        'macaque (macaca)': { genus: 'Macaca', common: 'Macaque', sciLower: 'macaca', rank: 'Genus' },
        'lynx (lynx)': { genus: 'Lynx', common: 'Lynx', sciLower: 'lynx', rank: 'Genus' },
        'panda (ailuropoda)': { genus: 'Ailuropoda', common: 'Panda', sciLower: 'ailuropoda', rank: 'Genus' },
        'raccoon (procyon)': { genus: 'Procyon', common: 'Raccoon', sciLower: 'procyon', rank: 'Genus' },
        'hyena (hyaenidae)': { genus: 'Hyaenidae', common: 'Hyena', sciLower: 'hyaenidae', rank: 'Family' },
        'hippopotamus (hippopotamidae)': { genus: 'Hippopotamidae', common: 'Hippopotamus', sciLower: 'hippopotamidae', rank: 'Family' },
        'ladybird (coccinellidae)': { genus: 'Coccinellidae', common: 'Ladybird', sciLower: 'coccinellidae', rank: 'Family' },
        'albatross (diomedeidae)': { genus: 'Diomedeidae', common: 'Albatross', sciLower: 'diomedeidae', rank: 'Family' },
        'giant clam (tridacna)': { genus: 'Tridacna', common: 'Giant Clam', sciLower: 'tridacna', rank: 'Genus' },
        'giraffe (giraffa)': { genus: 'Giraffa', common: 'Giraffe', sciLower: 'giraffa', rank: 'Genus' },
        'gorilla (gorilla)': { genus: 'Gorilla', common: 'Gorilla', sciLower: 'gorilla', rank: 'Genus' },
        'orangutan (pongo)': { genus: 'Pongo', common: 'Orangutan', sciLower: 'pongo', rank: 'Genus' },
        'coelacanth (latimeria)': { genus: 'Latimeria', common: 'Coelacanth', sciLower: 'latimeria', rank: 'Genus' },
        'chinchilla (chinchilla)': { genus: 'Chinchilla', common: 'Chinchilla', sciLower: 'chinchilla', rank: 'Genus' },
        'baboon (papio)': { genus: 'Papio', common: 'Baboon', sciLower: 'papio', rank: 'Genus' },
        'arapaima (arapaima)': { genus: 'Arapaima', common: 'Arapaima', sciLower: 'arapaima', rank: 'Genus' },
        'kiwi (apteryx)': { genus: 'Apteryx', common: 'Kiwi', sciLower: 'apteryx', rank: 'Genus' },
        'spider monkey (ateles)': { genus: 'Ateles', common: 'Spider Monkey', sciLower: 'ateles', rank: 'Genus' },
        'howler monkey (alouatta)': { genus: 'Alouatta', common: 'Howler Monkey', sciLower: 'alouatta', rank: 'Genus' },
        'tree kangaroo (dendrolagus)': { genus: 'Dendrolagus', common: 'Tree Kangaroo', sciLower: 'dendrolagus', rank: 'Genus' },
        'sloth (folivora)': { genus: 'Folivora', common: 'Sloth', sciLower: 'folivora', rank: 'Suborder' },
        'elephant (elephantidae)': { genus: 'Elephantidae', common: 'Elephant', sciLower: 'elephantidae', rank: 'Family' },
        'caecilian (gymnophiona)': { genus: 'Gymnophiona', common: 'Caecilian', sciLower: 'gymnophiona', rank: 'Order' },
        'hedgehog (erinaceinae)': { genus: 'Erinaceinae', common: 'Hedgehog', sciLower: 'erinaceinae', rank: 'Subfamily' },
        'seal (pinnipedia)': { genus: 'Pinnipedia', common: 'Seal', sciLower: 'pinnipedia', rank: 'Clade' },
        'opossum (didelphidae)': { genus: 'Didelphidae', common: 'Opossum', sciLower: 'didelphidae', rank: 'Family' },
        'mole (talpidae)': { genus: 'Talpidae', common: 'Mole', sciLower: 'talpidae', rank: 'Family' },
        'cuttlefish (sepiida)': { genus: 'Sepiida', common: 'Cuttlefish', sciLower: 'sepiida', rank: 'Order' },
        'starfish (asteroidea)': { genus: 'Asteroidea', common: 'Starfish', sciLower: 'asteroidea', rank: 'Class' },
        'chameleon (chamaeleonidae)': { genus: 'Chamaeleonidae', common: 'Chameleon', sciLower: 'chamaeleonidae', rank: 'Family' },
        'squid (decapodiformes)': { genus: 'Decapodiformes', common: 'Squid', sciLower: 'decapodiformes', rank: 'Class' },
        'octopus (octopoda)': { genus: 'Octopoda', common: 'Octopus', sciLower: 'octopoda', rank: 'Order' },
        'seahorse (hippocampus)': { genus: 'Hippocampus', common: 'Seahorse', sciLower: 'hippocampus', rank: 'Genus' },
        'tardigrade (tardigrada)': { genus: 'Tardigrada', common: 'Tardigrade', sciLower: 'tardigrada', rank: 'Phylum' },
        'dragonfly (anisoptera)': { genus: 'Anisoptera', common: 'Dragonfly', sciLower: 'anisoptera', rank: 'Order' },
        'scorpion (scorpiones)': { genus: 'Scorpiones', common: 'Scorpion', sciLower: 'scorpiones', rank: 'Order' },
        'earthworm (lumbricina)': { genus: 'Lumbricina', common: 'Earthworm', sciLower: 'lumbricina', rank: 'Order' },
        'sea urchin (echinoidea)': { genus: 'Echinoidea', common: 'Sea Urchin', sciLower: 'echinoidea', rank: 'Class' },
        'sea cucumber (holothuroidea)': { genus: 'Holothuroidea', common: 'Sea Cucumber', sciLower: 'holothuroidea', rank: 'Class' },
        'sea anemone (actiniaria)': { genus: 'Actiniaria', common: 'Sea Anemone', sciLower: 'actiniaria', rank: 'Order' },
        'stingray (myliobatiformes)': { genus: 'Myliobatiformes', common: 'Stingray', sciLower: 'myliobatiformes', rank: 'Order' },
        'mantis (mantodea)': { genus: 'Mantodea', common: 'Mantis', sciLower: 'mantodea', rank: 'Order' },
        'lobster (nephropidae)': { genus: 'Nephropidae', common: 'Lobster', sciLower: 'nephropidae', rank: 'Family' },
        'bumblebee (bombus)': { genus: 'Bombus', common: 'Bumblebee', sciLower: 'bombus', rank: 'Genus' },
        'wasp (vespidae)': { genus: 'Vespidae', common: 'Wasp', sciLower: 'vespidae', rank: 'Family' },
        'sponge (porifera)': { genus: 'Porifera', common: 'Sponge', sciLower: 'porifera', rank: 'Phylum' },
        'stag beetle (lucanidae)': { genus: 'Lucanidae', common: 'Stag Beetle', sciLower: 'lucanidae', rank: 'Family' },
        'oyster (ostreidae)': { genus: 'Ostreidae', common: 'Oyster', sciLower: 'ostreidae', rank: 'Family' },
        'clam (bivalvia)': { genus: 'Bivalvia', common: 'Clam', sciLower: 'bivalvia', rank: 'Class' },
        'snail (gastropoda)': { genus: 'Gastropoda', common: 'Snail', sciLower: 'gastropoda', rank: 'Class' },
        'millipede (diplopoda)': { genus: 'Diplopoda', common: 'Millipede', sciLower: 'diplopoda', rank: 'Class' },
        'prawn (dendrobranchiata)': { genus: 'Dendrobranchiata', common: 'Prawn', sciLower: 'dendrobranchiata', rank: 'Order' },
        'slug (agriolimacidae)': { genus: 'Agriolimacidae', common: 'Slug', sciLower: 'agriolimacidae', rank: 'Family' },
        'planarian (tricladida)': { genus: 'Tricladida', common: 'Planarian', sciLower: 'tricladida', rank: 'Order' },
        'toad (bufonidae)': { genus: 'Bufonidae', common: 'Toad', sciLower: 'bufonidae', rank: 'Family' },
        'frog (anura)': { genus: 'Anura', common: 'Frog', sciLower: 'anura', rank: 'Order' },
        'lionfish (pterois)': { genus: 'Pterois', common: 'Lionfish', sciLower: 'pterois', rank: 'Genus' },
        'newt (pleurodelinae)': { genus: 'Pleurodelinae', common: 'Newt', sciLower: 'pleurodelinae', rank: 'Subfamily' },
        'blue-ringed octopus (hapalochlaena)': { genus: 'Hapalochlaena', common: 'Blue-ringed octopus', sciLower: 'hapalochlaena', rank: 'Genus' },
        'moray eel (muraenidae)': { genus: 'Muraenidae', common: 'Moray Eel', sciLower: 'muraenidae', rank: 'Family' },
        'nautilus (nautilidae)': { genus: 'Nautilidae', common: 'Nautilus', sciLower: 'nautilidae', rank: 'Family' },
        'mantis shrimp (stomatopoda)': { genus: 'Stomatopoda', common: 'Mantis Shrimp', sciLower: 'stomatopoda', rank: 'Order' },
        'box jellyfish (cubozoa)': { genus: 'Cubozoa', common: 'Box Jellyfish', sciLower: 'cubozoa', rank: 'Class' },
        'horseshoe crab (limulidae)': { genus: 'Limulidae', common: 'Horseshoe Crab', sciLower: 'limulidae', rank: 'Family' },
        'anglerfish (lophiiformes)': { genus: 'Lophiiformes', common: 'Anglerfish', sciLower: 'lophiiformes', rank: 'Order' },
        'catfish (siluriformes)': { genus: 'Siluriformes', common: 'Catfish', sciLower: 'siluriformes', rank: 'Order' },
        'porpoise (phocoenidae)': { genus: 'Phocoenidae', common: 'Porpoise', sciLower: 'phocoenidae', rank: 'Family' },
        'barracuda (sphyraena)': { genus: 'Sphyraena', common: 'Barracuda', sciLower: 'sphyraena', rank: 'Genus' },
        'clownfish (amphiprion)': { genus: 'Amphiprion', common: 'Clownfish', sciLower: 'amphiprion', rank: 'Genus' },
        'piranha (serrasalmidae)': { genus: 'Serrasalmidae', common: 'Piranha', sciLower: 'serrasalmidae', rank: 'Family' },
        'cicada (cicadidae)': { genus: 'Cicadidae', common: 'Cicada', sciLower: 'cicadidae', rank: 'Family' },
        'mosquito (culicidae)': { genus: 'Culicidae', common: 'Mosquito', sciLower: 'culicidae', rank: 'Family' },
        'tarantula (theraphosidae)': { genus: 'Theraphosidae', common: 'Tarantula', sciLower: 'theraphosidae', rank: 'Family' },
        'swallowtail butterfly (papilionidae)': { genus: 'Papilionidae', common: 'Swallowtail Butterfly', sciLower: 'papilionidae', rank: 'Family' },
        'salamander (caudata)': { genus: 'Caudata', common: 'Salamander', sciLower: 'caudata', rank: 'Order' },
        'poison dart frog (dendrobatidae)': { genus: 'Dendrobatidae', common: 'Poison Dart Frog', sciLower: 'dendrobatidae', rank: 'Family' },
        'wombat (vombatidae)': { genus: 'Vombatidae', common: 'Wombat', sciLower: 'vombatidae', rank: 'Family' },
        'warthog (phacochoerus)': { genus: 'Phacochoerus', common: 'Warthog', sciLower: 'phacochoerus', rank: 'Genus' },
        'prairie dog (cynomys)': { genus: 'Cynomys', common: 'Prairie Dog', sciLower: 'cynomys', rank: 'Genus' },
        'hummingbird (trochilidae)': { genus: 'Trochilidae', common: 'Hummingbird', sciLower: 'trochilidae', rank: 'Family' },
        'pelican (pelecanus)': { genus: 'Pelecanus', common: 'Pelican', sciLower: 'pelecanus', rank: 'Genus' },
        'swan (cygnus)': { genus: 'Cygnus', common: 'Swan', sciLower: 'cygnus', rank: 'Genus' },
        'goose (anser)': { genus: 'Anser', common: 'Goose', sciLower: 'anser', rank: 'Genus' },
        'kangaroo (macropus)': { genus: 'Macropus', common: 'Kangaroo', sciLower: 'macropus', rank: 'Genus' },
        'cormorant (phalacrocoracidae)': { genus: 'Phalacrocoracidae', common: 'Cormorant', sciLower: 'phalacrocoracidae', rank: 'Family' },
        'tarsier (tarsiidae)': { genus: 'Tarsiidae', common: 'Tarsier', sciLower: 'tarsiidae', rank: 'Family' },
        'fire ant (solenopsis)': { genus: 'Solenopsis', common: 'Fire Ant', sciLower: 'solenopsis', rank: 'Genus' },
    };

    function getGenusFromEntry(entryStr) {
        if (!entryStr) return null;
        const key = entryStr.toLowerCase();
        if (SPECIAL_GENUS_MAP[key]) return SPECIAL_GENUS_MAP[key];
        const m = entryStr.match(/\(([A-Z][a-z]+)\)$/);
        if (m) {
            return { genus: m[1], common: entryStr.split(' (')[0], sciLower: m[1].toLowerCase(), rank: 'Genus' };
        }
        return null;
    }

    function doesGuessBelongToTargetGenus(guessStr, targetGenusObj) {
        if (!guessStr || !targetGenusObj) return false;
        const gKey = guessStr.toLowerCase();
        const gSci = (extractScientificName(guessStr) || gKey).toLowerCase();
        if (gSci === targetGenusObj.sciLower || gSci.startsWith(targetGenusObj.sciLower + ' ')) {
            return true;
        }
        // Universal phylogenetic lineage check for any rank (Order, Suborder, Family, Genus)
        if (phylogenyTree && phylogenyTree.species) {
            const linG = phylogenyTree.species[gKey];
            const targetKey = `${targetGenusObj.common} (${targetGenusObj.genus})`.toLowerCase();
            const linT = phylogenyTree.species[targetKey];
            if (linG && linT && linT.length > 0) {
                const targetTaxid = linT[linT.length - 1];
                if (linG.includes(targetTaxid)) return true;
            }
        }
        return false;
    }

    function getEvolutionaryComparison(guess, target) {
        const guessKey = guess.toLowerCase();
        const targetKey = target.toLowerCase();
        const targetGenusInfo = getGenusFromEntry(target);

        // 1. Direct string match
        if (guessKey === targetKey) {
            const sci = extractScientificName(guess) || guess;
            const rank = targetGenusInfo ? (targetGenusInfo.rank || "Genus") : "Species";
            return { time: 0.0, rank: rank, lca_name: sci, major_name: sci, major_rank: rank, major_time: 0.0 };
        }

        // 2. Target is a special Genus or Higher Taxon, and guessed species belongs to that group!
        if (targetGenusInfo && doesGuessBelongToTargetGenus(guess, targetGenusInfo)) {
            const rankLabel = targetGenusInfo.rank || "Genus";
            return {
                time: 0.0,
                rank: rankLabel,
                lca_name: targetGenusInfo.genus,
                major_name: targetGenusInfo.genus,
                major_rank: rankLabel,
                major_time: 0.0
            };
        }
        if (phylogenyTree && phylogenyTree.species && phylogenyTree.nodes) {
            const linG = phylogenyTree.species[guessKey];
            const linT = phylogenyTree.species[targetKey];
            if (linG && linT) {
                let lca = linG[0];
                const common = [];
                const maxLen = Math.min(linG.length, linT.length);
                for (let i = 0; i < maxLen; i++) {
                    if (linG[i] === linT[i]) {
                        lca = linG[i];
                        common.push(lca);
                    } else {
                        break;
                    }
                }
                const node = phylogenyTree.nodes[lca] || { time: 50.0, rank: "Class", name: "Chordata", major_name: "Chordata" };

                let majorNode = null;
                if (node.major_name && node.major_name !== node.name) {
                    for (let i = common.length - 1; i >= 0; i--) {
                        const anc = phylogenyTree.nodes[common[i]];
                        if (anc && (anc.name === node.major_name || (anc.name === 'Metazoa' && node.major_name === 'Animalia'))) {
                            majorNode = {
                                name: node.major_name,
                                rank: anc.rank,
                                time: anc.time
                            };
                            break;
                        }
                    }
                }

                return {
                    time: node.time,
                    rank: node.rank,
                    lca_name: node.name,
                    major_name: node.major_name || node.name,
                    major_rank: majorNode ? majorNode.rank : node.rank,
                    major_time: majorNode ? majorNode.time : (node.time * 1.5)
                };
            }
        }
        if (targetData && targetData[guessKey]) {
            const td = targetData[guessKey];
            return {
                time: td.time,
                rank: td.rank,
                lca_name: td.lca_name,
                major_name: td.major_name || td.lca_name || td.rank,
                major_rank: td.rank,
                major_time: td.time * 1.5
            };
        }
        return null;
    }

    // Guess Handling
    async function handleGuess() {
        if (isGameOver) return;
        const guess = animalInput.value.trim();
        if (!guess) return;

        let guessedAlias = animalInput.dataset.matchedAlias || null;
        delete animalInput.dataset.matchedAlias;

        let validGuess = allSpecies.find(s => s.toLowerCase() === guess.toLowerCase());
        if (!validGuess) {
            // Check exact common name or scientific name before aliases so primary names are never shadowed
            const g = guess.toLowerCase();
            validGuess = allSpecies.find(s => {
                const common = s.split(' (')[0].toLowerCase();
                const sci = extractScientificName(s).toLowerCase();
                return common === g || sci === g;
            });
        }
        if (!validGuess && speciesAliases) {
            const aliasMatch = speciesAliases[guess.toLowerCase()];
            if (aliasMatch) {
                validGuess = allSpecies.find(s => s.toLowerCase() === aliasMatch.toLowerCase());
                if (validGuess && !guessedAlias) {
                    guessedAlias = guess;
                }
            }
        }
        if (!validGuess && speciesAliases) {
            // Check prefix in aliases
            const g = guess.toLowerCase();
            for (const [alias, canonical] of Object.entries(speciesAliases)) {
                if (alias.startsWith(g)) {
                    validGuess = allSpecies.find(s => s.toLowerCase() === canonical.toLowerCase());
                    if (validGuess) {
                        if (!guessedAlias) guessedAlias = alias;
                        break;
                    }
                }
            }
        }
        if (!validGuess) {
            // Fallback: first species that starts with typed text
            const g = guess.toLowerCase();
            validGuess = allSpecies.find(s => s.toLowerCase().startsWith(g) || s.split(' (')[0].toLowerCase().startsWith(g));
        }
        if (!validGuess) {
            alert("Please select a recognized organism from the list.");
            return;
        }

        // Clean & format guessedAlias
        if (guessedAlias) {
            const canonicalCommon = validGuess.split(' (')[0].toLowerCase();
            if (guessedAlias.toLowerCase() === canonicalCommon || guessedAlias.toLowerCase() === validGuess.toLowerCase()) {
                guessedAlias = null;
            } else {
                guessedAlias = guessedAlias.split(' ')
                    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                    .join(' ');
            }
        }

        const guessKey = validGuess.toLowerCase();
        if (guessedSet.has(guessKey)) {
            alert("You already guessed that organism!");
            return;
        }

        guessedSet.add(guessKey);

        const data = getEvolutionaryComparison(validGuess, targetSpecies);
        if (!data) {
            alert("Evolutionary comparison data not available for this pair.");
            return;
        }
        const targetGenusInfo = getGenusFromEntry(targetSpecies);
        const isMatch = (guessKey === targetSpecies.toLowerCase()) || 
                        (targetGenusInfo && doesGuessBelongToTargetGenus(validGuess, targetGenusInfo));

        const latinNameMatch = validGuess.match(/\((.*?)\)/);
        const wikiTitle = latinNameMatch ? latinNameMatch[1] : validGuess;

        const guessObj = {
            name: validGuess,
            wikiTitle: wikiTitle,
            guessedAlias: guessedAlias || null,
            lca_rank: data.rank,
            lca_name: data.lca_name || data.rank,
            major_name: data.major_name || data.lca_name || data.rank,
            major_rank: data.major_rank || data.rank,
            major_time: data.major_time !== undefined ? data.major_time : data.time,
            tmrca: data.time,
            isMatch: isMatch,
            timestamp: Date.now()
        };

        guesses.push(guessObj);
        if (targetAlertContainer) targetAlertContainer.innerHTML = '';
        addGuessToBoard(validGuess, wikiTitle, data, isMatch, guessedAlias);
        updateTree();

        // Save active progress if daily
        if (!isUnlimited) {
            saveActiveGuesses(currentDateStr, guesses, targetSpecies);
        }

        animalInput.value = '';
        closeDropdown();

        if (isMatch) {
            if (targetAlertContainer && guessedAlias) {
                const canonicalCommon = targetSpecies.split(' (')[0];
                const latinMatch = targetSpecies.match(/\((.*?)\)/);
                const canonicalLatin = latinMatch ? latinMatch[1] : '';
                targetAlertContainer.innerHTML = `
                    <div class="alias-success-banner" style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.4); border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; font-size: 0.95rem; color: #86efac; animation: fadeIn 0.3s ease;">
                        <span style="font-size: 1.3rem;">🌟</span>
                        <div>
                            <strong>Correct!</strong> You guessed <strong>${escapeHtml(guessedAlias)}</strong>, which is an accepted alias of <strong>${escapeHtml(canonicalCommon)}</strong> <em>(${escapeHtml(canonicalLatin)})</em>.
                        </div>
                    </div>
                `;
            }
            finishGame(true);
        }
    }

    // ==========================================================================
    // Feature 4: Taxonomic Rank Hint System
    // ==========================================================================
    const MAIN_RANKS_ORDER = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus'];
    const RANK_EMOJIS = {
        'Kingdom': '🟫',
        'Phylum': '🟦',
        'Class': '🟪',
        'Order': '🟥',
        'Family': '🟧',
        'Genus': '🟨',
        'Species': '🟩'
    };

    function getTargetTaxonomyRanks() {
        const targetKey = targetSpecies.toLowerCase();
        const targetLin = (phylogenyTree && phylogenyTree.species) ? phylogenyTree.species[targetKey] : null;
        const result = {};
        if (!targetLin || !phylogenyTree.nodes) return result;

        for (const nid of targetLin) {
            const node = phylogenyTree.nodes[nid];
            if (!node) continue;
            const r = node.rank;
            if (MAIN_RANKS_ORDER.includes(r) && !result[r]) {
                result[r] = {
                    rank: r,
                    name: node.major_name || node.name,
                    wikiTitle: node.name,
                    time: node.time
                };
            }
        }
        return result;
    }

    function getNextTaxonomicRankHint() {
        const targetRanks = getTargetTaxonomyRanks();
        
        // 1. Identify which ranks are already matched by player's guesses
        const matchedRanks = new Set();
        guesses.forEach(g => {
            const r = g.lca_rank;
            const idx = MAIN_RANKS_ORDER.indexOf(r);
            if (idx !== -1) {
                for (let i = 0; i <= idx; i++) {
                    matchedRanks.add(MAIN_RANKS_ORDER[i]);
                }
            }
            if (g.isMatch) {
                MAIN_RANKS_ORDER.forEach(rk => matchedRanks.add(rk));
            }
        });

        // 2. Identify which ranks have already been given by prior hints
        const hintedRanks = new Set(revealedHints.map(h => h.rank));

        // 3. Find the first rank in MAIN_RANKS_ORDER that is NOT yet matched or hinted
        for (const r of MAIN_RANKS_ORDER) {
            if (!matchedRanks.has(r) && !hintedRanks.has(r) && targetRanks[r]) {
                return {
                    type: 'rank',
                    rank: r,
                    name: targetRanks[r].name,
                    wikiTitle: targetRanks[r].wikiTitle || targetRanks[r].name,
                    time: targetRanks[r].time
                };
            }
        }

        // 4. If all 6 ranks are matched or hinted, provide a species clue
        if (!hintedRanks.has('Species')) {
            const common = (targetPresentationName || targetSpecies.split(' (')[0]).trim();
            const latinMatch = targetSpecies.match(/\((.*?)\)/);
            const latin = latinMatch ? latinMatch[1] : common;
            return {
                type: 'species',
                rank: 'Species',
                name: `Starts with "${common[0]}" (Latin: "${latin[0]}...")`,
                wikiTitle: latin,
                time: 0.0
            };
        }

        return null;
    }

    function getOrdinal(n) {
        const s = ["th", "st", "nd", "rd"];
        const v = n % 100;
        return n + (s[(v - 20) % 10] || s[v] || s[0]);
    }

    function addHintToBoard(hint, hintNumber) {
        if (!guessesContainer) return;
        const rank = hint.rank || 'Taxa';
        const rankLower = rank.toLowerCase();
        const emoji = RANK_EMOJIS[rank] || '💡';
        const cssClass = `closeness-${rankLower}`;
        const ordinalStr = getOrdinal(hintNumber || 1);
        const wikiTitle = hint.wikiTitle || hint.name;
        const timeStr = (hint.time === 0 || rank === 'Species') ? "0.0 MYA (Exact)" : (hint.time ? `${hint.time.toFixed(1)} MYA` : "Unknown MYA");

        const row = document.createElement('div');
        row.className = `guess-row guess-row-hint ${cssClass}`;
        row.innerHTML = `
            <div class="guess-header guess-hint-header">
                <span class="guess-hint-title">
                    <span class="hint-lightbulb">💡</span> Revealed Clue
                </span>
                <span class="hint-used-flag">${ordinalStr} Clue Used</span>
            </div>
            <div class="guess-hint-name taxa-link" data-taxa="${wikiTitle}">
                ${rank}: <strong>${hint.name}</strong>
            </div>
            <div class="guess-subrow">
                <span class="closeness-pill ${cssClass}" title="Revealed ${rank}">
                    ${emoji} ${rank}
                </span>
                <span class="feedback-badge feedback-rank taxa-link" data-taxa="${wikiTitle}">
                    ${rank}: ${hint.name}
                </span>
                <span class="feedback-badge feedback-time" title="Ancestral divergence time for this rank">
                    Diverged: ${timeStr}
                </span>
            </div>
        `;

        const taxaLinks = row.querySelectorAll('.taxa-link');
        taxaLinks.forEach(el => {
            el.addEventListener('mouseenter', (e) => showWikiTooltip(e, wikiTitle));
            el.addEventListener('mouseleave', hideWikiTooltip);
            el.addEventListener('click', () => {
                window.open(`https://en.wikipedia.org/wiki/${encodeURIComponent(wikiTitle)}`, '_blank');
            });
        });

        guessesContainer.prepend(row);
    }

    function handleHintRequest() {
        if (isGameOver) return;
        const hint = getNextTaxonomicRankHint();
        if (!hint) {
            alert("All main taxonomic rank clues have already been revealed or deduced by your guesses!");
            return;
        }

        hint.timestamp = Date.now();
        revealedHints.push(hint);
        if (!isUnlimited) {
            saveActiveHints(currentDateStr, revealedHints, { targetSpecies, puzzleNum });
        }

        addHintToBoard(hint, revealedHints.length);
        updateTree();
    }

    function renderHintsCard() {
        // Obsolete: Hints now render directly in the guesses column as full clue cards
        if (hintsCard) hintsCard.classList.add('hidden');
    }

    hintBtn?.addEventListener('click', handleHintRequest);

    function getGuessRankEmoji(g) {
        if (g.isMatch) {
            if (g.lca_rank === 'Genus') return '🟨';
            return '🟩';
        }
        if (g.lca_rank === 'Species') return '🟩';
        const r = g.lca_rank;
        if (r === 'Genus') return '🟨'; // yellow - genus match
        if (r === 'Family') return '🟧'; // orange - family
        if (r === 'Order') return '🟥'; // red - order
        if (r === 'Class') return '🟪'; // purple - class
        if (r === 'Phylum') return '🟦'; // blue - phylum
        if (r === 'Kingdom') return '🟫'; // brown - kingdom
        return '⬛'; // black - nothing match
    }

    function getGameTimelineEmojis(guessList = guesses, hintList = revealedHints) {
        const timeline = [];
        if (guessList && guessList.length > 0) {
            guessList.forEach((g, idx) => {
                timeline.push({
                    type: 'guess',
                    emoji: getGuessRankEmoji(g),
                    time: g.timestamp || (idx * 2)
                });
            });
        }
        if (hintList && hintList.length > 0) {
            hintList.forEach((h, idx) => {
                timeline.push({
                    type: 'hint',
                    emoji: '💡',
                    time: h.timestamp || (idx * 2 + 1)
                });
            });
        }
        timeline.sort((a, b) => a.time - b.time);
        return timeline.map(item => item.emoji).join('');
    }

    function getClosenessInfo(data, isMatch) {
        if (isMatch) {
            if (data.rank === 'Genus') {
                return {
                    rank: 'Genus',
                    emoji: '🟨',
                    label: 'Genus (Match) (0 MYA)',
                    shortLabel: 'Genus (Match)',
                    cssClass: 'closeness-genus',
                    squareClass: 'square-genus'
                };
            }
            return {
                rank: 'Species',
                emoji: '🟩',
                label: 'Species (Match) (0 MYA)',
                shortLabel: 'Species (Match)',
                cssClass: 'closeness-species',
                squareClass: 'square-species'
            };
        }
        if (data.rank === 'Species') {
            return {
                rank: 'Species',
                emoji: '🟩',
                label: 'Species (Match) (0 MYA)',
                shortLabel: 'Species (Match)',
                cssClass: 'closeness-species',
                squareClass: 'square-species'
            };
        }
        const r = data.rank;
        if (r === 'Genus') {
            return {
                rank: 'Genus',
                emoji: '🟨',
                label: 'Same Genus (Sister species)',
                shortLabel: 'Genus',
                cssClass: 'closeness-genus',
                squareClass: 'square-genus'
            };
        }
        if (r === 'Family') {
            return {
                rank: 'Family',
                emoji: '🟧',
                label: 'Same Family',
                shortLabel: 'Family',
                cssClass: 'closeness-family',
                squareClass: 'square-family'
            };
        }
        if (r === 'Order') {
            return {
                rank: 'Order',
                emoji: '🟥',
                label: 'Same Order',
                shortLabel: 'Order',
                cssClass: 'closeness-order',
                squareClass: 'square-order'
            };
        }
        if (r === 'Class') {
            return {
                rank: 'Class',
                emoji: '🟪',
                label: 'Same Class',
                shortLabel: 'Class',
                cssClass: 'closeness-class',
                squareClass: 'square-class'
            };
        }
        if (r === 'Phylum') {
            return {
                rank: 'Phylum',
                emoji: '🟦',
                label: 'Same Phylum',
                shortLabel: 'Phylum',
                cssClass: 'closeness-phylum',
                squareClass: 'square-phylum'
            };
        }
        if (r === 'Kingdom') {
            return {
                rank: 'Kingdom',
                emoji: '🟫',
                label: 'Same Kingdom',
                shortLabel: 'Kingdom',
                cssClass: 'closeness-kingdom',
                squareClass: 'square-kingdom'
            };
        }
        return {
            rank: 'Domain',
            emoji: '⬛',
            label: 'Same Domain (Eukaryota)',
            shortLabel: 'Domain',
            cssClass: 'closeness-domain',
            squareClass: 'square-domain'
        };
    }

    function addGuessToBoard(guessName, wikiTitle, data, isMatch, guessedAlias = null) {
        const closeness = getClosenessInfo(data, isMatch);
        const row = document.createElement('div');
        row.className = `guess-row ${closeness.cssClass}`;
        const matchClass = isMatch ? 'match-exact' : '';

        const timeStr = data.time === 0 ? "0.0 MYA (Match)" : (data.time === -1.0 ? "Unknown (>500 MYA)" : `${data.time.toFixed(1)} MYA`);
        const lcaName = data.lca_name || data.rank;
        const majorName = data.major_name || lcaName;

        let rankBadgeText = `${data.rank}: ${lcaName}`;
        if (isMatch || data.rank === 'Species') {
            rankBadgeText = `Species: ${lcaName}`;
        } else if (majorName && majorName !== lcaName && majorName !== 'Unknown' && lcaName !== 'Unknown') {
            rankBadgeText = `${data.rank}: ${majorName} (${lcaName})`;
        } else if (majorName && majorName !== 'Unknown') {
            rankBadgeText = `${data.rank}: ${majorName}`;
        }

        // Primary: Unicode square emoji; Fallback: CSS rank-square-icon
        const iconHtml = closeness.emoji || `<span class="rank-square-icon ${closeness.squareClass}"></span>`;

        let aliasBadgeHtml = '';
        if (guessedAlias) {
            aliasBadgeHtml = `<span class="guess-alias-badge" style="display: block; font-size: 0.8rem; opacity: 0.82; color: #a5b4fc; margin-top: 2px;">(guessed as "${escapeHtml(guessedAlias)}")</span>`;
        }

        row.innerHTML = `
            <div class="guess-header">
                <span class="guess-name ${matchClass} taxa-link">${guessName}</span>
                ${aliasBadgeHtml}
            </div>
            <div class="guess-subrow">
                <span class="closeness-pill ${closeness.cssClass}" title="${closeness.label}">
                    ${iconHtml} ${closeness.shortLabel}
                </span>
                <span class="feedback-badge feedback-rank ${matchClass} taxa-link" data-taxa="${lcaName}">${rankBadgeText}</span>
                <span class="feedback-badge feedback-time ${matchClass}" title="Estimated evolutionary divergence time">Diverged: ${timeStr}</span>
            </div>
        `;

        const nameSpan = row.querySelector('.guess-name');
        nameSpan.addEventListener('mouseenter', (e) => showWikiTooltip(e, wikiTitle));
        nameSpan.addEventListener('mouseleave', hideWikiTooltip);
        nameSpan.addEventListener('click', () => {
            window.open(`https://en.wikipedia.org/wiki/${encodeURIComponent(wikiTitle)}`, '_blank');
        });

        const taxaSpan = row.querySelector('.feedback-rank');
        taxaSpan.addEventListener('mouseenter', (e) => showWikiTooltip(e, lcaName));
        taxaSpan.addEventListener('mouseleave', hideWikiTooltip);
        taxaSpan.addEventListener('click', () => {
            window.open(`https://en.wikipedia.org/wiki/${encodeURIComponent(lcaName)}`, '_blank');
        });

        guessesContainer.prepend(row);
    }

    function addSurrenderRow(species) {
        const commonName = species.split(' (')[0];
        const latinMatch = species.match(/\((.*?)\)/);
        const wikiTitle = latinMatch ? latinMatch[1] : commonName;
        const row = document.createElement('div');
        row.className = 'guess-row closeness-surrender';

        let aliasBadgeHtml = '';
        if (targetPresentationName && targetPresentationName.toLowerCase() !== commonName.toLowerCase()) {
            aliasBadgeHtml = `<span class="guess-alias-badge" style="display: block; font-size: 0.8rem; opacity: 0.82; color: #a5b4fc; margin-top: 2px;">(Featured as "${escapeHtml(targetPresentationName)}")</span>`;
        }

        row.innerHTML = `
            <div class="guess-header">
                <span class="guess-name match-exact taxa-link">${species}</span>
                ${aliasBadgeHtml}
            </div>
            <div class="guess-subrow">
                <span class="closeness-pill closeness-surrender" title="Organism Revealed">
                    ⬜ Revealed
                </span>
                <span class="feedback-badge feedback-rank match-exact taxa-link" data-taxa="${commonName}">Target Organism</span>
                <span class="feedback-badge feedback-time match-exact">Gave Up</span>
            </div>
        `;
        const nameSpan = row.querySelector('.guess-name');
        nameSpan.addEventListener('mouseenter', (e) => showWikiTooltip(e, wikiTitle));
        nameSpan.addEventListener('mouseleave', hideWikiTooltip);
        nameSpan.addEventListener('click', () => {
            window.open(`https://en.wikipedia.org/wiki/${encodeURIComponent(wikiTitle)}`, '_blank');
        });
        guessesContainer.prepend(row);
    }

    // In-App Confirmation Modal (Replaces browser confirm() popups for clean mobile UX)
    function showInAppConfirm({ icon = '❓', title = 'Confirm Action', message = 'Are you sure?', proceedText = 'Confirm', proceedBg = '#ef4444', onProceed }) {
        const modal = document.getElementById('confirm-modal');
        if (!modal) {
            if (onProceed) onProceed();
            return;
        }
        const iconEl = document.getElementById('confirm-modal-icon');
        const titleEl = document.getElementById('confirm-modal-title');
        const msgEl = document.getElementById('confirm-modal-message');
        const cancelBtn = document.getElementById('confirm-modal-cancel');
        const proceedBtn = document.getElementById('confirm-modal-proceed');

        if (iconEl) iconEl.textContent = icon;
        if (titleEl) titleEl.textContent = title;
        if (msgEl) msgEl.textContent = message;
        if (proceedBtn) {
            proceedBtn.textContent = proceedText;
            proceedBtn.style.background = proceedBg;
        }

        const cleanup = () => {
            closeModal(modal);
            cancelBtn?.removeEventListener('click', handleCancel);
            proceedBtn?.removeEventListener('click', handleProceed);
        };

        const handleCancel = () => cleanup();
        const handleProceed = () => {
            cleanup();
            if (onProceed) onProceed();
        };

        cancelBtn?.addEventListener('click', handleCancel, { once: true });
        proceedBtn?.addEventListener('click', handleProceed, { once: true });

        openModal(modal);
    }

    function finishGame(win) {
        isGameOver = true;
        endTitle.textContent = win ? "You found it! 🏆" : "Organism Revealed 🏳️";
        endTitle.style.color = win ? "var(--success-color)" : "#f87171";
        const hintCount = revealedHints.length;
        const hintSuffix = hintCount > 0 ? ` (${hintCount} hint${hintCount === 1 ? '' : 's'})` : '';

        const canonicalCommon = targetSpecies.split(' (')[0];
        const allAliases = getAliasesForSpecies(targetSpecies, speciesAliases);
        const targetGenusInfo = getGenusFromEntry(targetSpecies);

        let genusNoticeHtml = '';
        if (targetGenusInfo) {
            const rankLabel = targetGenusInfo.rank || 'Genus';
            genusNoticeHtml = `
                <div class="genus-notice-box" style="background: rgba(234, 179, 8, 0.12); border: 1px solid rgba(234, 179, 8, 0.45); border-radius: 8px; padding: 10px 14px; margin: 10px 0 8px 0; color: #fef08a; font-size: 0.92rem; text-align: left; line-height: 1.45;">
                    <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #facc15; margin-bottom: 4px;">
                        <span style="font-size: 1.15rem;">🌿</span> Taxonomic Notice: Today's organism was a ${escapeHtml(rankLabel)}!
                    </div>
                    <div>Today's mystery target was actually the <strong>${escapeHtml(rankLabel)} ${escapeHtml(targetGenusInfo.genus)}</strong> (<em>${escapeHtml(canonicalCommon)}</em>), which encompasses multiple recognized biological species.</div>
                </div>
            `;
        }

        let aliasInfoHtml = '';
        if (targetPresentationName && targetPresentationName.toLowerCase() !== canonicalCommon.toLowerCase()) {
            aliasInfoHtml += `<div style="font-size: 0.85rem; color: #a5b4fc; margin-top: 4px;">Featured round presentation name: <strong>${escapeHtml(targetPresentationName)}</strong></div>`;
        }
        if (allAliases && allAliases.length > 0) {
            const otherAliases = allAliases.filter(a => a.toLowerCase() !== targetPresentationName.toLowerCase());
            if (otherAliases.length > 0) {
                aliasInfoHtml += `<div style="font-size: 0.8rem; opacity: 0.85; color: var(--text-secondary); margin-top: 2px;">Also known as: <em>${escapeHtml(otherAliases.join(', '))}</em></div>`;
            }
        }

        endMessage.innerHTML = `The organism was <strong>${targetSpecies}</strong>.<br>` +
            genusNoticeHtml +
            aliasInfoHtml +
            `<span style="font-size: 0.9rem; color: var(--text-secondary); display: inline-block; margin-top: 6px;">${win ? `Solved in ${guesses.length} guess${guesses.length === 1 ? '' : 'es'}${hintSuffix}!` : 'Surrendered & revealed.'}</span>`;

        if (!win) {
            addSurrenderRow(targetSpecies);
        }

        const endEmojisRow = document.getElementById('end-emojis-row');
        if (endEmojisRow) {
            let emojis = getGameTimelineEmojis(guesses, revealedHints);
            if (win) {
                emojis += ' ✅'; // Always append green checkbox after all game wins
            } else {
                emojis += ' ⬜'; // White square indicates surrendered / revealed
            }
            endEmojisRow.textContent = emojis;
        }

        if (inputSection) inputSection.style.display = 'none';
        if (animalInput && animalInput.parentElement) animalInput.parentElement.style.display = '';
        if (guessBtn) guessBtn.style.display = '';
        if (giveUpBtn) giveUpBtn.style.display = '';
        if (hintBtn) hintBtn.style.display = '';
        gameEndPanel.classList.remove('hidden');

        updateTree();

        if (!isUnlimited) {
            recordDailyCompletion(currentDateStr, puzzleNum, win, guesses.length, guesses, targetSpecies, revealedHints);
            clearActiveGuesses(currentDateStr);
            if (win) {
                setTimeout(() => openModal(statsModal), 1000);
            }
        } else {
            recordPracticeCompletion(win, guesses.length, guesses, targetSpecies, revealedHints);
        }
    }

    guessBtn.addEventListener('click', handleGuess);
    giveUpBtn.addEventListener('click', () => {
        if (isGameOver) return;
        showInAppConfirm({
            icon: '🏳️',
            title: 'Give Up & Reveal?',
            message: 'Are you sure you want to surrender and reveal the mystery organism?',
            proceedText: 'Reveal Organism',
            proceedBg: '#ef4444',
            onProceed: () => finishGame(false)
        });
    });

    function setGameMode(unlimited) {
        if (isUnlimited === unlimited) return;
        isUnlimited = unlimited;
        if (isUnlimited) {
            localStorage.setItem('phylogenle_game_mode', 'practice');
            const newUrl = window.location.pathname + '?mode=practice';
            window.history.replaceState(null, '', newUrl);
            initGame();
        } else {
            localStorage.setItem('phylogenle_game_mode', 'daily');
            currentDateStr = getTodayDateStr();
            puzzleNum = getPuzzleNumber(currentDateStr);
            window.history.replaceState(null, '', window.location.pathname);
            initGame();
        }
    }

    if (modeDailyBtn) {
        modeDailyBtn.addEventListener('click', () => setGameMode(false));
    }
    if (modePracticeBtn) {
        modePracticeBtn.addEventListener('click', () => setGameMode(true));
    }

    playAgainBtn.addEventListener('click', () => {
        if (isUnlimited) {
            initGame();
        } else {
            setGameMode(true);
        }
    });

    shareResultBtn.addEventListener('click', () => shareScore());

    const resetCurrentPuzzleBtn = document.getElementById('reset-current-puzzle-btn');
    if (resetCurrentPuzzleBtn) {
        resetCurrentPuzzleBtn.addEventListener('click', () => {
            if (isUnlimited) {
                initGame();
                return;
            }
            resetDateRecord(currentDateStr);
            initGame();
        });
    }

    // ==========================================================================
    // D3 Tree Rendering: Dynamic Scaling & Smart Vertical Staggering
    // ==========================================================================
    function getNodeDisplayEmoji(d) {
        if (d.data.emoji) return d.data.emoji;
        if (d.data.isMystery) {
            if (d.data.isMatch) {
                const targetGenusInfo = getGenusFromEntry(targetSpecies);
                return (targetGenusInfo && targetGenusInfo.genus) ? '🟨' : '🟩';
            }
            if (isGameOver) return '⬜';
            return '⬜';
        }
        if (d.data.isGuess) {
            return d.data.emoji || '🟨';
        }
        const t = (d.data.name || '').toLowerCase();
        if (t === 'root' || t === 'root (luca)' || t === 'luca' || t === 'cellular organisms' || t === 'life' || t === 'eukaryota' || t === 'bacteria' || t === 'archaea') {
            return '⬛';
        }
        // Clade ranks
        const rank = d.data.rank;
        if (rank) {
            if (rank === 'Species') return '🟩';
            if (rank === 'Genus') return '🟨';
            if (rank === 'Family') return '🟧';
            if (rank === 'Order') return '🟥';
            if (rank === 'Class') return '🟪';
            if (rank === 'Phylum') return '🟦';
            if (rank === 'Kingdom') return '🟫';
            if (rank === 'Domain') return '⬛';
        }
        // Clade names
        const taxonMap = {
            'animalia': '🟫', 'metazoa': '🟫', 'plantae': '🟫', 'viridiplantae': '🟫', 'fungi': '🟫',
            'eukaryota': '⬛', 'bacteria': '⬛', 'archaea': '⬛', 'cellular organisms': '⬛', 'life': '⬛', 'root': '⬛', 'root (luca)': '⬛', 'luca': '⬛',
            'chordata': '🟦', 'arthropoda': '🟦', 'mollusca': '🟦', 'annelida': '🟦', 'cnidaria': '🟦', 'echinodermata': '🟦',
            'streptophyta': '🟦', 'tracheophyta': '🟦', 'ascomycota': '🟦', 'basidiomycota': '🟦', 'pseudomonadota': '🟦',
            'mammalia': '🟪', 'aves': '🟪', 'reptilia': '🟪', 'amphibia': '🟪', 'insecta': '🟪', 'arachnida': '🟪', 'actinopterygii': '🟪',
            'magnoliopsida': '🟪', 'liliopsida': '🟪', 'gammaproteobacteria': '🟪', 'agaricomycetes': '🟪',
            'carnivora': '🟥', 'primates': '🟥', 'rodentia': '🟥', 'artiodactyla': '🟥', 'cetacea': '🟥', 'chiroptera': '🟥', 'lagomorpha': '🟥',
            'lepidoptera': '🟥', 'coleoptera': '🟥', 'hymenoptera': '🟥', 'diptera': '🟥', 'passeriformes': '🟥',
            'rosales': '🟥', 'poales': '🟥', 'fabales': '🟥', 'asterales': '🟥', 'solanales': '🟥', 'brassicales': '🟥',
            'felidae': '🟧', 'canidae': '🟧', 'ursidae': '🟧', 'hominidae': '🟧', 'cercopithecidae': '🟧', 'mustelidae': '🟧',
            'papilionidae': '🟧', 'nymphalidae': '🟧', 'apidae': '🟧', 'elephantidae': '🟧', 'equidae': '🟧', 'bovidae': '🟧',
            'rosaceae': '🟧', 'poaceae': '🟧', 'fabaceae': '🟧', 'asteraceae': '🟧', 'solanaceae': '🟧', 'brassicaceae': '🟧'
        };
        if (taxonMap[t]) return taxonMap[t];
        return '🟫';
    }

    function updateTree() {
        const sortedGuesses = [...guesses].sort((a, b) => {
            const timeA = a.tmrca === -1 ? Infinity : a.tmrca;
            const timeB = b.tmrca === -1 ? Infinity : b.tmrca;
            return timeB - timeA;
        });

        const hasMatch = sortedGuesses.some(g => g.isMatch);
        const isRevealed = hasMatch || isGameOver;
        const mysteryName = isRevealed ? targetSpecies.split(' (')[0] : "?";
        const latinMatch = targetSpecies.match(/\((.*?)\)/);
        const mysteryWiki = latinMatch ? latinMatch[1] : mysteryName;
        const targetGenusInfo = getGenusFromEntry(targetSpecies);
        const matchRankEmoji = (targetGenusInfo && targetGenusInfo.genus) ? '🟨' : '🟩';
        const mysteryEmoji = hasMatch ? matchRankEmoji : (isGameOver ? '⬜' : '⬜');
        const mysteryNode = {
            name: mysteryName,
            wikiTitle: mysteryWiki,
            isMystery: true,
            isMatch: hasMatch,
            isRevealed: isRevealed,
            emoji: mysteryEmoji
        };

        function getTargetRootInfo() {
            let defaultRootName = "Root (LUCA)";
            let defaultRank = "Domain";
            let defaultWiki = "Last_universal_common_ancestor";
            const targetLin = (phylogenyTree && phylogenyTree.species) ? phylogenyTree.species[targetSpecies.toLowerCase()] : null;
            if (targetLin && phylogenyTree.nodes) {
                for (let tid of targetLin) {
                    const n = phylogenyTree.nodes[tid];
                    if (n && (n.rank === "Domain" || n.rank === "Kingdom")) {
                        const nName = (n.name || '').toLowerCase();
                        if (nName === 'root' || nName === 'cellular organisms' || nName === 'luca') {
                            defaultRootName = "Root (LUCA)";
                            defaultWiki = "Last_universal_common_ancestor";
                            defaultRank = "Domain";
                            break;
                        } else {
                            defaultRootName = n.major_name || n.name;
                            defaultRank = n.rank;
                            defaultWiki = defaultRootName;
                            break;
                        }
                    }
                }
            }
            return { name: defaultRootName, wikiTitle: defaultWiki, rank: defaultRank, emoji: defaultRank === 'Domain' ? '⬛' : '🟫' };
        }

        const rankHints = revealedHints.filter(h => h.type === 'rank');
        if (sortedGuesses.length === 0 && rankHints.length === 0) {
            if (isGameOver) {
                const tr = getTargetRootInfo();
                drawTree({
                    name: tr.name,
                    wikiTitle: tr.wikiTitle,
                    rank: tr.rank,
                    emoji: tr.emoji,
                    isTrunk: true,
                    children: [mysteryNode]
                });
            } else {
                drawTree({ name: "?", emoji: '⬜', isMystery: true, children: [] });
            }
            return;
        }

        const trunkMap = new Map();

        // 1. Add revealed rank hints to the trunk
        rankHints.forEach(h => {
            if (h.name && !trunkMap.has(h.name)) {
                trunkMap.set(h.name, {
                    name: h.name,
                    wikiTitle: h.wikiTitle || h.name,
                    rank: h.rank,
                    time: h.time !== undefined ? h.time : 100,
                    isTrunk: true,
                    isHint: true,
                    guessChildren: []
                });
            }
        });

        sortedGuesses.forEach(g => {
            if (g.isMatch) return;
            // 2. Major Linnaean rank node (e.g. Mammalia, Carnivora, Chordata)
            if (g.major_name && g.major_name !== g.lca_name && g.major_name !== 'Unknown' && g.major_name !== 'root') {
                if (!trunkMap.has(g.major_name)) {
                    trunkMap.set(g.major_name, {
                        name: g.major_name,
                        wikiTitle: g.major_name,
                        rank: g.major_rank || g.lca_rank,
                        time: g.major_time !== undefined ? g.major_time : (g.tmrca * 1.5),
                        isTrunk: true,
                        guessChildren: []
                    });
                }
            }

            // 3. Specific LCA subclade node (e.g. Boreoeutheria, Caniformia)
            if (!trunkMap.has(g.lca_name)) {
                trunkMap.set(g.lca_name, {
                    name: g.lca_name,
                    wikiTitle: g.lca_name,
                    rank: g.lca_rank,
                    time: g.tmrca,
                    isTrunk: true,
                    guessChildren: []
                });
            }

            const commonName = g.name.split(' (')[0];
            const guessEmoji = getGuessRankEmoji(g);
            const guessNode = {
                name: commonName,
                wikiTitle: g.wikiTitle,
                isGuess: true,
                rank: 'Species',
                emoji: guessEmoji
            };
            trunkMap.get(g.lca_name).guessChildren.push(guessNode);
        });

        // Build target lineage depth lookup to guarantee mathematically correct evolutionary order
        const targetLin = (phylogenyTree && phylogenyTree.species) ? phylogenyTree.species[targetSpecies.toLowerCase()] : null;
        const targetLinIdxMap = new Map();
        if (targetLin && phylogenyTree.nodes) {
            targetLin.forEach((tid, idx) => {
                const n = phylogenyTree.nodes[tid];
                if (n) {
                    if (n.name) targetLinIdxMap.set(n.name.toLowerCase(), idx);
                    if (n.major_name && !targetLinIdxMap.has(n.major_name.toLowerCase())) {
                        targetLinIdxMap.set(n.major_name.toLowerCase(), idx);
                    }
                }
            });
        }

        // Automatically reveal any skipped intermediate standard Linnaean ranks
        // (e.g. if Family or Genus is hit, automatically write out the Order on the tree trunk)
        const RANK_DEPTH_MAP = {
            'Domain': 1,
            'Kingdom': 2,
            'Phylum': 3,
            'Class': 4,
            'Order': 5,
            'Family': 6,
            'Genus': 7,
            'Species': 8
        };

        let maxReachedDepth = 0;
        sortedGuesses.forEach(g => {
            const d1 = RANK_DEPTH_MAP[g.lca_rank] || 0;
            const d2 = RANK_DEPTH_MAP[g.major_rank] || 0;
            const d = Math.max(d1, d2);
            if (d > maxReachedDepth) maxReachedDepth = d;
        });
        rankHints.forEach(h => {
            const d = RANK_DEPTH_MAP[h.rank] || 0;
            if (d > maxReachedDepth) maxReachedDepth = d;
        });

        // Automatically reveal any skipped intermediate standard Linnaean ranks
        // (e.g. if Family is hit after Class, automatically write out the Order node on the tree trunk)
        if (targetLin && phylogenyTree.nodes && maxReachedDepth >= 3) {
            const standardRanks = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus'];
            standardRanks.forEach(targetRank => {
                const targetDepth = RANK_DEPTH_MAP[targetRank];
                if (maxReachedDepth >= targetDepth) {
                    for (let tid of targetLin) {
                        const n = phylogenyTree.nodes[tid];
                        if (n && n.rank === targetRank) {
                            const nodeName = n.major_name || n.name;
                            if (!trunkMap.has(nodeName) && !trunkMap.has(n.name)) {
                                trunkMap.set(nodeName, {
                                    name: nodeName,
                                    wikiTitle: n.name,
                                    rank: targetRank,
                                    time: n.time !== undefined ? n.time : 50,
                                    isTrunk: true,
                                    guessChildren: []
                                });
                            }
                            break;
                        }
                    }
                }
            });
        }

        function getLinIdx(node) {
            const raw = (node.name || '').toLowerCase();
            if (raw === 'root' || raw === 'root (luca)' || raw === 'luca' || raw === 'cellular organisms' || raw === 'life') {
                return 0;
            }
            if (targetLinIdxMap.has(raw)) {
                return targetLinIdxMap.get(raw);
            }
            const wiki = (node.wikiTitle || '').toLowerCase();
            if (targetLinIdxMap.has(wiki)) {
                return targetLinIdxMap.get(wiki);
            }
            for (let [name, idx] of targetLinIdxMap.entries()) {
                if (raw.includes(name) || name.includes(raw)) {
                    return idx;
                }
            }
            return -1;
        }

        const trunkList = Array.from(trunkMap.values()).sort((a, b) => {
            const idxA = getLinIdx(a);
            const idxB = getLinIdx(b);
            if (idxA !== -1 && idxB !== -1) {
                if (idxA !== idxB) {
                    return idxA - idxB; // Biological order: root (0) down to species!
                }
            } else if (idxA !== -1) {
                return -1;
            } else if (idxB !== -1) {
                return 1;
            }
            // Tie-break or fallback by divergence time
            const tA = a.time === -1 ? Infinity : a.time;
            const tB = b.time === -1 ? Infinity : b.time;
            return tB - tA;
        });

        // Normalize root/LUCA node names & emojis
        trunkList.forEach(node => {
            const low = (node.name || '').toLowerCase();
            if (low === 'root' || low === 'cellular organisms' || low === 'luca') {
                node.name = 'Root (LUCA)';
                node.wikiTitle = 'Last_universal_common_ancestor';
                node.rank = 'Domain';
                node.emoji = '⬛';
            }
        });

        // Enforce time monotonicity along trunk (parent time >= child time)
        for (let i = trunkList.length - 2; i >= 0; i--) {
            if (trunkList[i].time < trunkList[i + 1].time) {
                trunkList[i].time = trunkList[i + 1].time;
            }
        }

        if (trunkList.length === 0) {
            const tr = getTargetRootInfo();
            drawTree({
                name: tr.name,
                wikiTitle: tr.wikiTitle,
                rank: tr.rank,
                emoji: tr.emoji,
                isTrunk: true,
                children: [mysteryNode]
            });
            return;
        }

        for (let i = 0; i < trunkList.length; i++) {
            const cur = trunkList[i];
            cur.children = [...cur.guessChildren];
            if (i + 1 < trunkList.length) {
                cur.children.push(trunkList[i + 1]);
            } else {
                cur.children.push(mysteryNode);
            }
        }

        let root = trunkList[0];
        const topRanks = new Set(["Domain", "Kingdom"]);
        const topNames = new Set(["Life", "Cellular organisms", "cellular organisms", "root", "Root (LUCA)", "LUCA", "Eukaryota", "Bacteria", "Archaea", "Animalia", "Metazoa", "Plantae", "Viridiplantae", "Fungi"]);
        if (!topRanks.has(root.rank) && !topNames.has(root.name)) {
            const tr = getTargetRootInfo();
            root = { name: tr.name, wikiTitle: tr.wikiTitle, rank: tr.rank, emoji: tr.emoji, isTrunk: true, children: [root] };
        }

        drawTree(root);
    }

    let lastRenderedTreeData = null;

    function drawTree(treeData) {
        if (!treeContainer) return;
        lastRenderedTreeData = treeData;
        treeContainer.innerHTML = '';

        // Add Zoom & Pan Navigation Controls
        const controlsDiv = document.createElement('div');
        controlsDiv.className = 'tree-controls';
        controlsDiv.innerHTML = `
            <button id="tree-zoom-in" title="Zoom in" aria-label="Zoom in">+</button>
            <button id="tree-zoom-out" title="Zoom out" aria-label="Zoom out">−</button>
            <button id="tree-zoom-reset" title="Reset view and center tree" aria-label="Reset view">⟲</button>
        `;
        treeContainer.appendChild(controlsDiv);

        // Add interactive touch/mouse pan hint
        const hintDiv = document.createElement('div');
        hintDiv.className = 'tree-hint';
        hintDiv.textContent = '✋ Drag to pan • Scroll / pinch to zoom';
        treeContainer.appendChild(hintDiv);

        const containerWidth = treeContainer.clientWidth || 550;
        const containerHeight = treeContainer.clientHeight || 520;

        // Count leaf nodes for dynamic allocation
        const hierarchyData = d3.hierarchy(treeData, d => d.children);
        const leafNodes = hierarchyData.leaves();
        const leafCount = Math.max(leafNodes.length, 1);
        const maxDepth = Math.max(hierarchyData.height || 1, 1);

        // Dynamically adjust leaf spacing so large trees stay compact
        const leafSpacing = leafCount > 8 ? 115 : (leafCount > 4 ? 130 : 145);
        const computedWidth = Math.max(leafCount * leafSpacing, 440);

        // Fixed taxonomic rank level height: ~72px per level
        const levelHeight = 72;
        const computedHeight = Math.max(180, maxDepth * levelHeight);

        // Responsive SVG that fills container
        const svg = d3.select("#tree-container").append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("class", "tree-svg");

        // Master zoomable group
        const g = svg.append("g").attr("class", "tree-zoom-group");

        // D3 Zoom & Dragging Hand Behavior
        const zoom = d3.zoom()
            .scaleExtent([0.25, 2.5])
            .on("start", () => {
                treeContainer.classList.add("is-dragging");
            })
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            })
            .on("end", () => {
                treeContainer.classList.remove("is-dragging");
            });

        svg.call(zoom);

        const treeMap = d3.tree().size([computedWidth, computedHeight]);
        const treeNodes = treeMap(hierarchyData);
        const allDescendants = treeNodes.descendants();

        const dynamicFontSize = 11;

        // Draw Links inside zoom group
        g.selectAll(".link")
            .data(treeNodes.descendants().slice(1))
            .enter().append("path")
            .attr("class", "link")
            .attr("d", d => {
                return "M" + d.x + "," + d.y
                     + "C" + d.x + "," + (d.y + d.parent.y) / 2
                     + " " + d.parent.x + "," + (d.y + d.parent.y) / 2
                     + " " + d.parent.x + "," + d.parent.y;
            });

        // Smart Collision-Aware Vertical Staggering for leaf/guess nodes
        const childNodes = allDescendants.filter(d => !d.data.isTrunk).sort((a, b) => a.x - b.x);
        let currentChildTier = 0;
        let lastChildX = -999;
        let lastChildWidth = 0;
        childNodes.forEach((node) => {
            const labelText = `${getNodeDisplayEmoji(node)} ${node.data.name}`;
            const approxWidth = labelText.length * 7.5 + 24;
            const dist = node.x - lastChildX;
            const minSafeDist = (approxWidth + lastChildWidth) / 2 + 16;
            if (dist < minSafeDist) {
                currentChildTier = (currentChildTier + 1) % 3;
            } else {
                currentChildTier = 0;
            }
            node.staggerTier = currentChildTier;
            lastChildX = node.x;
            lastChildWidth = approxWidth;
        });

        // Smart Vertical Staggering for trunk nodes
        const trunkNodes = allDescendants.filter(d => d.data.isTrunk).sort((a, b) => a.x - b.x);
        let currentTrunkTier = 0;
        let lastTrunkX = -999;
        trunkNodes.forEach(node => {
            if (node.x - lastTrunkX < 80) {
                currentTrunkTier = (currentTrunkTier + 1) % 2;
            } else {
                currentTrunkTier = 0;
            }
            node.trunkTier = currentTrunkTier;
            lastTrunkX = node.x;
        });

        // Nodes Group inside zoom group
        const node = g.selectAll(".node")
            .data(allDescendants)
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${d.x}, ${d.y})`);

        // Vertical Dashed Stagger Leader Lines for offset child nodes
        node.each(function(d) {
            if (!d.data.isTrunk && d.staggerTier > 0) {
                const targetY = d.staggerTier === 1 ? 46 : 74;
                d3.select(this).append("line")
                    .attr("class", "node-stagger-line")
                    .attr("x1", 0)
                    .attr("y1", 9)
                    .attr("x2", 0)
                    .attr("y2", targetY - 10);
            }
        });

        // Node Circles
        node.append("circle")
            .attr("r", d => d.data.isMystery ? 10 : 7)
            .style("fill", d => {
                if (d.data.isMystery) {
                    if (d.data.isMatch) return "var(--success-color)";
                    if (isGameOver) return "#ffffff";
                    return "#60a5fa";
                }
                if (d.data.isGuess) return "var(--warning-color)";
                return "var(--bg-primary)";
            })
            .style("stroke", d => {
                if (d.data.isMystery) {
                    return "#ffffff";
                }
                if (d.data.isGuess) return "#f59e0b";
                return "var(--accent-color)";
            });

        // Calculate Y Offset per node
        function getNodeYOffset(d) {
            if (d.data.isTrunk) {
                return d.trunkTier === 1 ? -32 : -18;
            }
            if (d.staggerTier === 1) return 46;
            if (d.staggerTier === 2) return 74;
            return 22;
        }

        // Background Pill/Backdrop for maximum contrast and legibility
        node.append("rect")
            .attr("class", "node-label-bg")
            .attr("rx", 6)
            .attr("ry", 6)
            .attr("height", dynamicFontSize + 10)
            .attr("y", d => getNodeYOffset(d) - dynamicFontSize / 2 - 5);

        // Text Labels
        const textLabels = node.append("text")
            .attr("dy", ".35em")
            .attr("y", d => getNodeYOffset(d))
            .style("text-anchor", "middle")
            .style("font-size", `${dynamicFontSize}px`)
            .attr("class", "taxa-link node-label-text")
            .text(d => `${getNodeDisplayEmoji(d)} ${d.data.name}`)
            .on("mouseenter", function(e, d) {
                if (!d.data.isMystery || (d.data.isMystery && d.data.name !== "?")) {
                    const query = d.data.wikiTitle || d.data.name;
                    showWikiTooltip(e, query);
                }
            })
            .on("mouseleave", hideWikiTooltip)
            .on("click", function(e, d) {
                if (!d.data.isMystery || (d.data.isMystery && d.data.name !== "?")) {
                    const query = getNormalizedWikiTitle(d.data.wikiTitle || d.data.name);
                    window.open(`https://en.wikipedia.org/wiki/${encodeURIComponent(query)}`, '_blank');
                }
            });

        // Size background rects dynamically according to measured text width
        node.each(function() {
            const textEl = d3.select(this).select("text").node();
            const rectEl = d3.select(this).select("rect");
            if (textEl && rectEl.node()) {
                const bbox = textEl.getBBox();
                rectEl.attr("x", bbox.x - 10)
                      .attr("width", bbox.width + 20);
            }
        });

        // Make entire node group (circle, pill background, text) interactive with Wikipedia tooltips and links
        node.each(function(d) {
            const isInteractable = !d.data.isMystery || (d.data.isMystery && d.data.name !== "?");
            if (!isInteractable) return;
            const rawQuery = d.data.wikiTitle || d.data.name;
            if (!rawQuery || rawQuery === "Unknown" || rawQuery === "?") return;
            const query = getNormalizedWikiTitle(rawQuery);

            const gEl = d3.select(this);
            gEl.classed("taxa-clickable", true);

            gEl.on("mouseenter", function(e) {
                showWikiTooltip(e, rawQuery);
            })
            .on("mouseleave", hideWikiTooltip)
            .on("click", function(e) {
                if (treeContainer.classList.contains("is-dragging")) return;
                window.open(`https://en.wikipedia.org/wiki/${encodeURIComponent(query)}`, '_blank');
            });
        });

        // Initial Smart View Fitting: center and scale the tree to container
        const padX = 45;
        const padY = 50;
        const fitScaleX = (containerWidth - padX * 2) / computedWidth;
        const fitScaleY = (containerHeight - padY * 2) / computedHeight;
        const initialScale = Math.min(1.0, Math.max(0.40, Math.min(fitScaleX, fitScaleY)));
        const initialX = Math.max(padX, (containerWidth - computedWidth * initialScale) / 2);
        const initialY = 36;
        const initialTransform = d3.zoomIdentity.translate(initialX, initialY).scale(initialScale);

        svg.call(zoom.transform, initialTransform);

        // Zoom button event bindings
        d3.select("#tree-zoom-in").on("click", (e) => {
            e.stopPropagation();
            svg.transition().duration(250).call(zoom.scaleBy, 1.3);
        });
        d3.select("#tree-zoom-out").on("click", (e) => {
            e.stopPropagation();
            svg.transition().duration(250).call(zoom.scaleBy, 0.77);
        });
        d3.select("#tree-zoom-reset").on("click", (e) => {
            e.stopPropagation();
            svg.transition().duration(350).call(zoom.transform, initialTransform);
        });
    }

    // Debounced window resize handler to maintain tree centering
    let resizeTimer = null;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (lastRenderedTreeData) {
                drawTree(lastRenderedTreeData);
            }
        }, 200);
    });

    // ==========================================================================
    // Feature 3: Universal Species Catalog In-App Viewer
    // ==========================================================================
    let savedCatalogScrollTop = 0;

    async function openCatalogModal() {
        if (!catalogModal) return;
        catalogModal.classList.add('active');
        if (!catalogLoaded) {
            await loadSpeciesCatalog();
        } else {
            // Restore scroll position where user left off without re-rendering or collapsing details
            if (catalogContent && savedCatalogScrollTop > 0) {
                setTimeout(() => {
                    catalogContent.scrollTop = savedCatalogScrollTop;
                }, 10);
            }
        }
    }

    async function loadSpeciesCatalog() {
        if (!catalogContent) return;
        if (catalogLoaded && catalogMarkdownText) {
            renderCatalogView();
            return;
        }

        catalogContent.innerHTML = `
            <div class="catalog-loading">
                <span class="catalog-spinner">🧬</span>
                <p>Loading Universal Taxonomic Directory (29,564 species)...</p>
            </div>
        `;

        try {
            const [mdResp, taxResp] = await Promise.all([
                fetch(`species_catalog_taxonomic.md?v=tax_2_${Date.now()}`),
                fetch(`data/species_taxonomy_catalog.json?v=tax_2_${Date.now()}`)
            ]);

            if (!mdResp.ok) throw new Error(`HTTP ${mdResp.status} loading species_catalog_taxonomic.md`);
            catalogMarkdownText = await mdResp.text();

            if (taxResp.ok) {
                catalogTaxonomyData = await taxResp.json();
                buildCatalogCladeIndex();
            }

            catalogLoaded = true;
            renderCatalogView();
        } catch (err) {
            console.error("Failed to load species catalog:", err);
            catalogContent.innerHTML = `
                <div class="catalog-empty-notice" style="color: #ef4444;">
                    Failed to load taxonomic directory. Please check local server connection.
                </div>
            `;
        }
    }

    function renderMarkdown(md) {
        if (window.marked && typeof window.marked.parse === 'function') {
            return window.marked.parse(md);
        }
        return parseMarkdownFallback(md);
    }

    function parseMarkdownFallback(md) {
        let html = '';
        const lines = md.split('\n');
        let inTable = false;

        for (let line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
                if (/^\|(\s*:?-+:?\s*\|)+$/.test(trimmed)) {
                    continue;
                }
                const cells = trimmed.slice(1, -1).split('|').map(c => c.trim());
                if (!inTable) {
                    html += '<table class="catalog-table"><thead><tr>';
                    cells.forEach(c => html += `<th>${formatInlineMarkdown(c)}</th>`);
                    html += '</tr></thead><tbody>';
                    inTable = true;
                } else {
                    html += '<tr>';
                    cells.forEach(c => html += `<td>${formatInlineMarkdown(c)}</td>`);
                    html += '</tr>';
                }
                continue;
            }

            if (inTable) {
                html += '</tbody></table>';
                inTable = false;
            }

            if (trimmed.startsWith('### ')) {
                html += `<h3>${formatInlineMarkdown(trimmed.substring(4))}</h3>`;
            } else if (trimmed.startsWith('## ')) {
                html += `<h2>${formatInlineMarkdown(trimmed.substring(3))}</h2>`;
            } else if (trimmed.startsWith('# ')) {
                html += `<h1>${formatInlineMarkdown(trimmed.substring(2))}</h1>`;
            } else if (trimmed === '---') {
                html += '<hr>';
            } else if (trimmed.startsWith('<details') || trimmed.startsWith('</details') || trimmed.startsWith('<summary') || trimmed.startsWith('</summary>')) {
                html += trimmed + '\n';
            } else if (trimmed) {
                html += `<p>${formatInlineMarkdown(trimmed)}</p>`;
            }
        }

        if (inTable) {
            html += '</tbody></table>';
        }
        return html;
    }

    function formatInlineMarkdown(str) {
        return str
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>');
    }

    function enhanceCatalogTableHtml(rawHtml) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = rawHtml;

        const tables = tempDiv.querySelectorAll('table');
        tables.forEach((table, tIdx) => {
            // Skip the first overview table
            if (tIdx === 0 && table.querySelector('th') && table.querySelector('th').textContent.includes('Domain')) {
                return;
            }

            const headerRow = table.querySelector('thead tr') || table.querySelector('tr');
            if (headerRow) {
                const th = document.createElement('th');
                th.textContent = 'Action';
                th.style.width = '100px';
                headerRow.appendChild(th);
            }

            const bodyRows = table.querySelectorAll('tbody tr') || table.querySelectorAll('tr:not(:first-child)');
            bodyRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length >= 2) {
                    const commonName = cells[0].textContent.trim();
                    const sciName = cells[1].textContent.trim();
                    const fullSpecies = `${commonName} (${sciName})`;

                    const actionTd = document.createElement('td');
                    actionTd.innerHTML = `<button class="catalog-guess-btn" data-species="${encodeURIComponent(fullSpecies)}">🎯 Guess</button>`;
                    row.appendChild(actionTd);
                }
            });
        });

        return tempDiv.innerHTML;
    }

    let catalogSearchMatches = [];
    let catalogSearchRenderedCount = 0;
    const CATALOG_SEARCH_CHUNK_SIZE = 150;
    let catalogSearchScrollAttached = false;

    let catalogCladeIndex = null;
    let catalogSpeciesLookup = null;
    let catalogNodeNameToNode = null;

    function buildCatalogCladeIndex() {
        if (!phylogenyTree || !catalogTaxonomyData || catalogCladeIndex) return;

        const cladeToSpecies = new Map();
        const nodeNames = new Map();
        catalogNodeNameToNode = new Map();

        // 1. Map node ID -> lowercase clean name and catalogNodeNameToNode
        if (phylogenyTree.nodes) {
            for (const [nid, node] of Object.entries(phylogenyTree.nodes)) {
                if (node.name) {
                    const cleanName = node.name.toLowerCase().trim();
                    nodeNames.set(Number(nid), cleanName);
                    if (!catalogNodeNameToNode.has(cleanName)) {
                        catalogNodeNameToNode.set(cleanName, node);
                    }
                }
            }
        }

        // 2. Map species keys to catalogTaxonomyData items for fast lookup
        catalogSpeciesLookup = new Map();
        for (let i = 0; i < catalogTaxonomyData.length; i++) {
            const item = catalogTaxonomyData[i];
            const disp = (item.display || `${item.common} (${item.scientific})`).toLowerCase().trim();
            catalogSpeciesLookup.set(disp, item);
            if (item.scientific) {
                catalogSpeciesLookup.set(item.scientific.toLowerCase().trim(), item);
            }
            if (item.common) {
                catalogSpeciesLookup.set(item.common.toLowerCase().trim(), item);
            }
        }

        // 3. Map every clade name to a Set of matching catalog items
        if (phylogenyTree.species) {
            for (const [spKey, nids] of Object.entries(phylogenyTree.species)) {
                const catItem = catalogSpeciesLookup.get(spKey) || 
                                (spKey.includes('(') ? catalogSpeciesLookup.get(extractScientificName(spKey).toLowerCase()) : null);
                if (!catItem || !Array.isArray(nids)) continue;

                for (let i = 0; i < nids.length; i++) {
                    const cname = nodeNames.get(nids[i]);
                    if (cname) {
                        let itemSet = cladeToSpecies.get(cname);
                        if (!itemSet) {
                            itemSet = new Set();
                            cladeToSpecies.set(cname, itemSet);
                        }
                        itemSet.add(catItem);
                    }
                }
            }
        }

        catalogCladeIndex = cladeToSpecies;
    }

    function getTaxonVariants(query) {
        const q = (query || '').toLowerCase().trim();
        const variants = new Set([q]);
        if (q.endsWith('s') && q.length > 3) variants.add(q.slice(0, -1));
        if (q.endsWith('ids') && q.length > 4) {
            variants.add(q.slice(0, -3) + 'idae');
            variants.add(q.slice(0, -3) + 'ida');
        }
        if (q.endsWith('id') && q.length > 3) {
            variants.add(q.slice(0, -2) + 'idae');
            variants.add(q.slice(0, -2) + 'ida');
        }
        if (q.endsWith('e') && q.length > 3) {
            variants.add(q.slice(0, -1) + 'a');
        }
        if (q.endsWith('an') && q.length > 4) {
            variants.add(q.slice(0, -2) + 'a');
        }
        return Array.from(variants);
    }

    function renderCatalogView() {
        if (!catalogContent) return;

        if (catalogSearchScrollAttached) {
            catalogContent.removeEventListener('scroll', handleCatalogSearchScroll);
            catalogSearchScrollAttached = false;
        }

        const searchQuery = catalogSearchInput ? catalogSearchInput.value.toLowerCase().trim() : '';

        if (searchQuery) {
            renderCatalogSearchResults(searchQuery);
            return;
        }

        const actionControls = `
            <div class="catalog-tree-actions">
                <button type="button" id="catalog-expand-all-btn" class="tree-action-btn">➕ Expand All</button>
                <button type="button" id="catalog-collapse-all-btn" class="tree-action-btn">➖ Collapse All</button>
                <span style="font-size: 0.8rem; color: var(--text-secondary); margin-left: auto;">
                    All 8 ranks collapsed by default — click any level (Domain ➔ Kingdom ➔ Phylum ➔ Class ➔ Order ➔ Family ➔ Genus) to expand
                </span>
            </div>
        `;

        const rawHtml = renderMarkdown(catalogMarkdownText);
        catalogContent.innerHTML = actionControls + enhanceCatalogTableHtml(rawHtml);

        // Bind expand and collapse all buttons
        const expandBtn = document.getElementById('catalog-expand-all-btn');
        const collapseBtn = document.getElementById('catalog-collapse-all-btn');

        if (expandBtn) {
            expandBtn.addEventListener('click', () => {
                catalogContent.querySelectorAll('details').forEach(d => d.open = true);
            });
        }
        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => {
                catalogContent.querySelectorAll('details').forEach(d => d.open = false);
            });
        }

        // Handle jumping to specific kingdom if tab selected
        if (currentCatalogClade && currentCatalogClade !== 'tree') {
            jumpToCatalogClade(currentCatalogClade);
        } else {
            catalogContent.scrollTop = 0;
        }
    }

    function jumpToCatalogClade(cladeName) {
        if (!catalogContent) return;
        const allDetails = catalogContent.querySelectorAll('details');
        allDetails.forEach(d => {
            const summary = d.querySelector('summary');
            if (summary && summary.textContent.toLowerCase().includes(cladeName.toLowerCase())) {
                d.open = true;
                let parent = d.parentElement.closest('details');
                while (parent) {
                    parent.open = true;
                    parent = parent.parentElement.closest('details');
                }
                setTimeout(() => {
                    d.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 50);
            }
        });
    }

    async function openCatalogAtTaxon(taxonName) {
        if (!catalogModal) return;
        await openCatalogModal();
        if (!catalogLoaded) {
            await loadSpeciesCatalog();
        }

        const raw = (taxonName || '').trim();
        const clean = raw.toLowerCase();
        if (!clean) return;

        buildCatalogCladeIndex();

        // Clear search input initially
        if (catalogSearchInput && catalogSearchInput.value) {
            catalogSearchInput.value = '';
        }
        if (catalogSearchClear) {
            catalogSearchClear.classList.add('hidden');
        }

        setTimeout(() => {
            if (!catalogContent) return;

            const cleanNoParen = clean.replace(/\(.*?\)/g, '').trim();
            const sciMatch = raw.match(/\((.*?)\)/);
            const sciName = sciMatch ? sciMatch[1].trim().toLowerCase() : '';

            const summaries = Array.from(catalogContent.querySelectorAll('summary'));
            let matchedSummary = null;

            // 1. Look for matching rank summary header (Order, Family, Class, Phylum, Kingdom, Domain)
            for (const s of summaries) {
                const txt = s.textContent.toLowerCase();
                if (txt.includes(`: ${clean}`) || 
                    (cleanNoParen && txt.includes(`: ${cleanNoParen}`)) || 
                    (sciName && txt.includes(`: ${sciName}`))) {
                    matchedSummary = s;
                    break;
                }
            }

            // 2. Substring match in summary
            if (!matchedSummary) {
                for (const s of summaries) {
                    const txt = s.textContent.toLowerCase();
                    if (txt.includes(clean) || (cleanNoParen && txt.includes(cleanNoParen))) {
                        matchedSummary = s;
                        break;
                    }
                }
            }

            if (matchedSummary) {
                const parentDetails = matchedSummary.closest('details');
                if (parentDetails) parentDetails.open = true;

                let ancestor = parentDetails ? parentDetails.parentElement.closest('details') : null;
                while (ancestor) {
                    ancestor.open = true;
                    ancestor = ancestor.parentElement.closest('details');
                }

                setTimeout(() => {
                    matchedSummary.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    matchedSummary.classList.remove('catalog-highlight-target');
                    void matchedSummary.offsetWidth;
                    matchedSummary.classList.add('catalog-highlight-target');
                }, 80);
                return;
            }

            // 3. Search in species table rows
            const rows = Array.from(catalogContent.querySelectorAll('tbody tr'));
            let matchedRow = null;
            for (const tr of rows) {
                const txt = tr.textContent.toLowerCase();
                if (txt.includes(clean) || (cleanNoParen && txt.includes(cleanNoParen)) || (sciName && txt.includes(sciName))) {
                    matchedRow = tr;
                    break;
                }
            }

            if (matchedRow) {
                let ancestor = matchedRow.closest('details');
                while (ancestor) {
                    ancestor.open = true;
                    ancestor = ancestor.parentElement.closest('details');
                }

                setTimeout(() => {
                    matchedRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    matchedRow.classList.remove('catalog-highlight-target');
                    void matchedRow.offsetWidth;
                    matchedRow.classList.add('catalog-highlight-target');
                }, 80);
                return;
            }

            // 4. Clade / Taxon search (for intermediate clades, superfamilies, orders like Muroidea, Tetrapoda, Glires)
            if (catalogSearchInput) {
                catalogSearchInput.value = raw;
                if (catalogSearchClear) catalogSearchClear.classList.remove('hidden');
                renderCatalogView();
            }
        }, 120);
    }
    window.openCatalogAtTaxon = openCatalogAtTaxon;
    window.showWikiTooltip = showWikiTooltip;

    function renderCatalogSearchResults(query) {
        if (!catalogContent) return;

        if (catalogSearchScrollAttached) {
            catalogContent.removeEventListener('scroll', handleCatalogSearchScroll);
            catalogSearchScrollAttached = false;
        }

        buildCatalogCladeIndex();

        const cleanQ = query.toLowerCase().trim();
        const queryVariants = getTaxonVariants(cleanQ);

        let matches = [];
        const seen = new Set();

        // 1. Direct taxonomic fields matching
        if (catalogTaxonomyData && Array.isArray(catalogTaxonomyData)) {
            for (let i = 0; i < catalogTaxonomyData.length; i++) {
                const item = catalogTaxonomyData[i];
                if ((item.common && item.common.toLowerCase().includes(cleanQ)) ||
                    (item.scientific && item.scientific.toLowerCase().includes(cleanQ)) ||
                    (item.genus && item.genus.toLowerCase().includes(cleanQ)) ||
                    (item.family && item.family.toLowerCase().includes(cleanQ)) ||
                    (item.order && item.order.toLowerCase().includes(cleanQ)) ||
                    (item.class && item.class.toLowerCase().includes(cleanQ)) ||
                    (item.phylum && item.phylum.toLowerCase().includes(cleanQ)) ||
                    (item.kingdom && item.kingdom.toLowerCase().includes(cleanQ)) ||
                    (item.domain && item.domain.toLowerCase().includes(cleanQ))) {
                    seen.add(item);
                    matches.push(item);
                }
            }
        } else {
            for (let i = 0; i < allSpecies.length; i++) {
                const sp = allSpecies[i];
                if (sp.toLowerCase().includes(cleanQ)) {
                    const common = sp.split(' (')[0];
                    const sciMatch = sp.match(/\((.*?)\)/);
                    const item = {
                        display: sp,
                        common: common,
                        scientific: sciMatch ? sciMatch[1] : '',
                        clade: '',
                        subclade: ''
                    };
                    seen.add(sp);
                    matches.push(item);
                }
            }
        }

        // 2. Comprehensive Clade & Phylogenetic Lineage Indexing
        if (catalogCladeIndex) {
            // First: exact matches on any variant (e.g. muroidea, amniota, glires)
            for (const v of queryVariants) {
                const exactSet = catalogCladeIndex.get(v);
                if (exactSet) {
                    for (const item of exactSet) {
                        if (!seen.has(item)) {
                            seen.add(item);
                            matches.push(item);
                        }
                    }
                }
            }

            // Second: substring matches on clades if query length >= 4
            if (cleanQ.length >= 4) {
                for (const [cname, itemSet] of catalogCladeIndex.entries()) {
                    for (const v of queryVariants) {
                        if (cname.includes(v)) {
                            for (const item of itemSet) {
                                if (!seen.has(item)) {
                                    seen.add(item);
                                    matches.push(item);
                                }
                            }
                            break;
                        }
                    }
                }
            }
        }

        catalogSearchMatches = matches;
        catalogSearchRenderedCount = 0;

        if (matches.length === 0) {
            catalogContent.innerHTML = `
                <div class="catalog-empty-notice">
                    No organisms found matching "<strong>${escapeHtml(query)}</strong>".<br>
                    <span style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 6px; display: inline-block;">
                        Try searching by genus (*Amphiprion*, *Panthera*), family (Felidae, Percidae), order (Rodentia, Carnivora), or clade (Muroidea, Tetrapoda).
                    </span>
                </div>
            `;
            return;
        }

        // Check if there is known clade metadata to present
        let cladeBannerHtml = '';
        if (catalogNodeNameToNode) {
            for (const v of queryVariants) {
                const nodeInfo = catalogNodeNameToNode.get(v);
                if (nodeInfo) {
                    cladeBannerHtml = `
                        <div class="catalog-clade-banner" style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 8px; padding: 0.5rem 0.85rem; margin: 0.5rem 0 0.85rem 0; font-size: 0.85rem; color: #c7d2fe;">
                            🧬 Taxonomic Clade: <strong>${escapeHtml(nodeInfo.name)}</strong>
                            ${nodeInfo.rank ? ` &bull; Rank: <span style="color: #fbbf24;">${escapeHtml(nodeInfo.rank)}</span>` : ''}
                            ${nodeInfo.major_name && nodeInfo.major_name.toLowerCase() !== nodeInfo.name.toLowerCase() ? ` &bull; Major Linnaean Group: <strong>${escapeHtml(nodeInfo.major_name)}</strong>` : ''}
                            ${nodeInfo.time ? ` &bull; Divergence Age: ~${nodeInfo.time} Mya` : ''}
                        </div>
                    `;
                    break;
                }
            }
        }

        const initialBatch = matches.slice(0, CATALOG_SEARCH_CHUNK_SIZE);
        catalogSearchRenderedCount = initialBatch.length;

        const subtitleText = matches.length <= CATALOG_SEARCH_CHUNK_SIZE
            ? `Showing all ${matches.length.toLocaleString()} matching organisms (click "🎯 Guess" to select):`
            : `Found <strong>${matches.length.toLocaleString()}</strong> matching organisms. Showing <span id="catalog-search-count">${catalogSearchRenderedCount.toLocaleString()}</span> (scroll down to browse all):`;

        let html = `
            <h2>🔍 Search Results for "${escapeHtml(query)}"</h2>
            ${cladeBannerHtml}
            <p id="catalog-search-subtitle" style="color: var(--text-secondary); font-size: 0.85rem;">${subtitleText}</p>
            <table class="catalog-table">
                <thead>
                    <tr>
                        <th>Common Name</th>
                        <th>Scientific Name</th>
                        <th>🟨 Genus</th>
                        <th>Taxonomic Lineage</th>
                        <th style="width: 100px;">Action</th>
                    </tr>
                </thead>
                <tbody id="catalog-search-tbody">
                    ${renderCatalogSearchRowsHtml(initialBatch)}
                </tbody>
            </table>
            <div id="catalog-search-scroll-status" style="text-align: center; padding: 12px; font-size: 0.82rem; color: var(--text-secondary);">
                ${matches.length > catalogSearchRenderedCount 
                    ? `Showing ${catalogSearchRenderedCount.toLocaleString()} of ${matches.length.toLocaleString()} organisms — scroll down to load more`
                    : `✓ All ${matches.length.toLocaleString()} matching organisms loaded`}
            </div>
        `;

        catalogContent.innerHTML = html;
        catalogContent.scrollTop = 0;

        if (catalogSearchRenderedCount < matches.length) {
            catalogContent.addEventListener('scroll', handleCatalogSearchScroll);
            catalogSearchScrollAttached = true;
        }
    }

    function renderCatalogSearchRowsHtml(items) {
        let rowsHtml = '';
        for (const m of items) {
            const fullSpecies = m.display || `${m.common} (${m.scientific})`;
            const lineageParts = [];
            if (m.kingdom) lineageParts.push(m.kingdom);
            if (m.class && !m.class.includes('Incertae')) lineageParts.push(m.class);
            if (m.order && !m.order.includes('Incertae')) lineageParts.push(m.order);
            if (m.family && !m.family.includes('Incertae')) lineageParts.push(m.family);
            const lineageStr = lineageParts.join(' ➔ ') || (m.clade ? `${m.clade} • ${m.subclade}` : '');

            rowsHtml += `
                <tr>
                    <td><strong>${escapeHtml(m.common || '')}</strong></td>
                    <td><em>${escapeHtml(m.scientific || '')}</em></td>
                    <td><span style="color: #fbbf24;">*${escapeHtml(m.genus || (m.scientific ? m.scientific.split(' ')[0] : ''))}*</span></td>
                    <td><span style="font-size: 0.78rem; color: #94a3b8;">${escapeHtml(lineageStr)}</span></td>
                    <td><button class="catalog-guess-btn" data-species="${encodeURIComponent(fullSpecies)}">🎯 Guess</button></td>
                </tr>
            `;
        }
        return rowsHtml;
    }

    function handleCatalogSearchScroll() {
        if (!catalogContent || catalogSearchRenderedCount >= catalogSearchMatches.length) return;
        const { scrollTop, scrollHeight, clientHeight } = catalogContent;
        if (scrollTop + clientHeight >= scrollHeight - 350) {
            const nextBatch = catalogSearchMatches.slice(catalogSearchRenderedCount, catalogSearchRenderedCount + CATALOG_SEARCH_CHUNK_SIZE);
            if (nextBatch.length > 0) {
                const tbody = document.getElementById('catalog-search-tbody');
                if (tbody) {
                    tbody.insertAdjacentHTML('beforeend', renderCatalogSearchRowsHtml(nextBatch));
                }
                catalogSearchRenderedCount += nextBatch.length;

                const countSpan = document.getElementById('catalog-search-count');
                if (countSpan) {
                    countSpan.textContent = catalogSearchRenderedCount.toLocaleString();
                }

                const statusDiv = document.getElementById('catalog-search-scroll-status');
                if (statusDiv) {
                    if (catalogSearchRenderedCount >= catalogSearchMatches.length) {
                        statusDiv.textContent = `✓ All ${catalogSearchMatches.length.toLocaleString()} matching organisms loaded`;
                    } else {
                        statusDiv.textContent = `Showing ${catalogSearchRenderedCount.toLocaleString()} of ${catalogSearchMatches.length.toLocaleString()} organisms — scroll down to load more`;
                    }
                }

                if (catalogSearchRenderedCount >= catalogSearchMatches.length) {
                    catalogContent.removeEventListener('scroll', handleCatalogSearchScroll);
                    catalogSearchScrollAttached = false;
                }
            }
        }
    }

    // Catalog event bindings
    catalogContent?.addEventListener('click', (e) => {
        const btn = e.target.closest('.catalog-guess-btn');
        if (btn) {
            const rawSp = btn.getAttribute('data-species');
            if (rawSp) {
                const sp = decodeURIComponent(rawSp);
                closeModal(catalogModal);
                animalInput.value = sp;
                handleGuess();
            }
        }
    });

    catalogCladeTabs?.addEventListener('click', (e) => {
        const btn = e.target.closest('.catalog-tab-btn');
        if (btn) {
            catalogCladeTabs.querySelectorAll('.catalog-tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCatalogClade = btn.getAttribute('data-clade') || 'tree';
            if (catalogSearchInput) catalogSearchInput.value = '';
            if (catalogSearchClear) catalogSearchClear.classList.add('hidden');
            renderCatalogView();
        }
    });

    catalogSearchInput?.addEventListener('input', () => {
        const val = catalogSearchInput.value.trim();
        if (catalogSearchClear) {
            if (val) catalogSearchClear.classList.remove('hidden');
            else catalogSearchClear.classList.add('hidden');
        }
        clearTimeout(catalogSearchDebounce);
        catalogSearchDebounce = setTimeout(() => {
            renderCatalogView();
        }, 150);
    });

    catalogSearchClear?.addEventListener('click', () => {
        if (catalogSearchInput) catalogSearchInput.value = '';
        catalogSearchClear.classList.add('hidden');
        renderCatalogView();
    });

    // ==========================================================================
    // Modals & Navigation Handling
    // ==========================================================================
    function openModal(modal) {
        if (!modal) return;
        modal.classList.add('active');
        if (modal === archiveModal) renderArchiveModal();
        if (modal === statsModal) renderStatsModal();
        if (modal === catalogModal) openCatalogModal();
    }

    function closeModal(modal) {
        if (!modal) return;
        if (modal === catalogModal && catalogContent) {
            savedCatalogScrollTop = catalogContent.scrollTop;
        }
        modal.classList.remove('active');
    }

    // Persist catalog scroll position continuously
    catalogContent?.addEventListener('scroll', () => {
        if (catalogContent) {
            savedCatalogScrollTop = catalogContent.scrollTop;
        }
    }, { passive: true });

    // Close modals on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal-backdrop.active');
            if (activeModal) closeModal(activeModal);
        }
    });

    document.querySelectorAll('[data-close]').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-close');
            closeModal(document.getElementById(id));
        });
    });

    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) closeModal(backdrop);
        });
    });

    document.getElementById('archive-modal-btn')?.addEventListener('click', () => openModal(archiveModal));
    document.getElementById('stats-modal-btn')?.addEventListener('click', () => openModal(statsModal));
    document.getElementById('help-modal-btn')?.addEventListener('click', () => openModal(helpModal));
    catalogNavBtn?.addEventListener('click', openCatalogModal);
    catalogBottomBtn?.addEventListener('click', openCatalogModal);

    // Archive Reset Toolbar
    const archiveResetCurrentBtn = document.getElementById('archive-reset-current-btn');
    if (archiveResetCurrentBtn) {
        archiveResetCurrentBtn.addEventListener('click', () => {
            showInAppConfirm({
                icon: '🔄',
                title: 'Reset Puzzle Record?',
                message: `Reset puzzle record for ${currentDateStr}? This allows you to replay with the updated species target.`,
                proceedText: 'Reset Puzzle',
                proceedBg: '#f59e0b',
                onProceed: () => {
                    resetDateRecord(currentDateStr);
                    renderArchiveModal();
                    initGame();
                }
            });
        });
    }

    const archiveResetAllBtn = document.getElementById('archive-reset-all-btn');
    if (archiveResetAllBtn) {
        archiveResetAllBtn.addEventListener('click', () => {
            showInAppConfirm({
                icon: '⚠️',
                title: 'Reset All History?',
                message: 'Are you sure you want to reset all past puzzle records and statistics? This will clear your archive history so all dates can be replayed freshly.',
                proceedText: 'Reset Everything',
                proceedBg: '#dc2626',
                onProceed: () => {
                    resetAllHistory();
                    renderArchiveModal();
                    initGame();
                }
            });
        });
    }

    // Archive Tabs (Calendar vs List)
    const calTab = document.getElementById('archive-tab-calendar');
    const listTab = document.getElementById('archive-tab-list');
    const calView = document.getElementById('archive-calendar-view');
    const listView = document.getElementById('archive-list-view');

    if (calTab && listTab && calView && listView) {
        calTab.addEventListener('click', () => {
            calTab.classList.add('active');
            listTab.classList.remove('active');
            calView.style.display = 'block';
            listView.style.display = 'none';
            renderCalendarView();
        });

        listTab.addEventListener('click', () => {
            listTab.classList.add('active');
            calTab.classList.remove('active');
            listView.style.display = 'block';
            calView.style.display = 'none';
            renderArchiveList();
        });
    }

    // Year and Month navigation
    const yearSelect = document.getElementById('cal-year-select');
    if (yearSelect) {
        const curY = parseDate(getTodayDateStr()).getFullYear();
        yearSelect.innerHTML = '';
        for (let y = curY; y >= 2024; y--) {
            const opt = document.createElement('option');
            opt.value = String(y);
            opt.textContent = String(y);
            yearSelect.appendChild(opt);
        }
        yearSelect.value = String(calYear);
        yearSelect.addEventListener('change', (e) => {
            calYear = Number(e.target.value);
            renderCalendarView();
        });
    }

    const monthSelect = document.getElementById('cal-month-select');
    if (monthSelect) {
        monthSelect.value = String(calMonth);
        monthSelect.addEventListener('change', (e) => {
            calMonth = Number(e.target.value);
            renderCalendarView();
        });
    }

    document.getElementById('cal-prev-month-btn')?.addEventListener('click', () => {
        calMonth--;
        if (calMonth < 0) {
            calMonth = 11;
            calYear--;
        }
        renderCalendarView();
    });

    document.getElementById('cal-next-month-btn')?.addEventListener('click', () => {
        calMonth++;
        if (calMonth > 11) {
            calMonth = 0;
            calYear++;
        }
        renderCalendarView();
    });

    document.getElementById('cal-today-btn')?.addEventListener('click', () => {
        const t = parseDate(getTodayDateStr());
        calYear = t.getFullYear();
        calMonth = t.getMonth();
        renderCalendarView();
    });

    // Archive Search & Filter
    const searchInput = document.getElementById('archive-search');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            renderArchiveList(searchInput.value);
        });
    }

    document.querySelectorAll('.archive-filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.archive-filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderArchiveList(searchInput ? searchInput.value : '');
        });
    });

    function renderArchiveModal() {
        renderCalendarView();
        renderArchiveList();
    }

    // Render 42-cell Calendar Grid
    function renderCalendarView() {
        const container = document.getElementById('calendar-days-container');
        if (!container) return;

        const todayStr = getTodayDateStr();
        const todayDate = parseDate(todayStr);

        if (monthSelect) monthSelect.value = String(calMonth);
        if (yearSelect) yearSelect.value = String(calYear);

        const nextBtn = document.getElementById('cal-next-month-btn');
        if (nextBtn) {
            const isFutureMonth = calYear > todayDate.getFullYear() ||
                (calYear === todayDate.getFullYear() && calMonth >= todayDate.getMonth());
            nextBtn.disabled = isFutureMonth;
        }

        const firstDayIndex = new Date(calYear, calMonth, 1).getDay();
        const totalDaysInMonth = new Date(calYear, calMonth + 1, 0).getDate();
        const history = getHistory();
        const cellsHtml = [];

        // Empty slots before month start
        for (let i = 0; i < firstDayIndex; i++) {
            cellsHtml.push('<div class="calendar-day-cell is-empty"></div>');
        }

        // Month days
        for (let day = 1; day <= totalDaysInMonth; day++) {
            const dateStr = `${calYear}-${String(calMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const isFuture = dateStr > todayStr;
            const isToday = dateStr === todayStr;

            if (isFuture) {
                cellsHtml.push(`
                    <div class="calendar-day-cell is-future">
                        <div class="cal-day-num">${day}</div>
                    </div>
                `);
                continue;
            }

            const pNum = getPuzzleNumber(dateStr);
            const record = history[dateStr];

            let statusClass = 'status-pending';
            let statusTag = isToday ? '🧬 Today' : '⚪ Play';

            if (record && record.completed) {
                if (record.solved) {
                    statusClass = 'status-solved';
                    statusTag = `🏆 ${record.guessCount}g`;
                } else {
                    statusClass = 'status-revealed';
                    statusTag = '❌ Revealed';
                }
            } else if (isToday) {
                statusClass = 'status-today';
            }

            cellsHtml.push(`
                <div class="calendar-day-cell ${statusClass} ${isToday ? 'is-today' : ''}" data-date="${dateStr}">
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <span class="cal-day-num">${day}</span>
                        <span class="cal-puzzle-num">#${pNum}</span>
                    </div>
                    <div class="cal-status-tag">${statusTag}</div>
                </div>
            `);
        }

        // Fill remaining slots to reach 42
        while (cellsHtml.length < 42) {
            cellsHtml.push('<div class="calendar-day-cell is-empty"></div>');
        }

        container.innerHTML = cellsHtml.join('');

        container.querySelectorAll('.calendar-day-cell[data-date]').forEach(cell => {
            cell.addEventListener('click', () => {
                const targetDate = cell.getAttribute('data-date');
                closeModal(archiveModal);
                loadDatePuzzle(targetDate);
            });
        });
    }

    // Render List View
    function renderArchiveList(query = '') {
        const listContainer = document.getElementById('archive-list-container');
        if (!listContainer) return;

        const activeFilter = document.querySelector('.archive-filter-btn.active')?.getAttribute('data-filter') || 'all';
        const todayStr = getTodayDateStr();
        const history = getHistory();
        const items = [];

        const curDate = parseDate(todayStr);
        const q = query.trim().toLowerCase();

        // Show all days from today back to epoch (no artificial truncation)
        const epochDate = parseDate(EPOCH_DATE_STR);
        const dayDiff = Math.max(0, Math.round((curDate - epochDate) / (1000 * 60 * 60 * 24)));
        for (let i = 0; i <= dayDiff; i++) {
            const d = new Date(curDate);
            d.setDate(d.getDate() - i);
            const dateStr = formatDate(d);
            const pNum = getPuzzleNumber(dateStr);
            const record = history[dateStr];

            // Apply filter
            if (activeFilter === 'solved' && (!record || !record.solved)) continue;
            if (activeFilter === 'unplayed' && record && record.completed) continue;

            // Apply search
            if (q) {
                const matchDate = dateStr.includes(q);
                const matchNum = String(pNum).includes(q);
                if (!matchDate && !matchNum) continue;
            }

            let badgeHtml = '';
            if (record && record.completed) {
                if (record.solved) {
                    badgeHtml = `<span style="color: #10b981; font-weight: 700; font-size: 0.8rem;">🏆 Solved (${record.guessCount} guesses)</span>`;
                } else {
                    badgeHtml = `<span style="color: #ef4444; font-weight: 700; font-size: 0.8rem;">❌ Revealed</span>`;
                }
            } else if (dateStr === todayStr) {
                badgeHtml = `<span style="color: #60a5fa; font-weight: 700; font-size: 0.8rem;">🧬 Today's Puzzle</span>`;
            } else {
                badgeHtml = `<span style="color: var(--text-secondary); font-size: 0.8rem;">Unplayed</span>`;
            }

            let actionsHtml = `<button class="archive-play-btn" data-date="${dateStr}">Play</button>`;
            if (record && record.completed) {
                actionsHtml = `
                    <div class="archive-item-actions">
                        <button class="archive-play-btn" data-date="${dateStr}">View</button>
                        <button class="archive-row-reset-btn" data-date="${dateStr}" title="Reset this puzzle to replay fresh">🔄 Reset</button>
                    </div>
                `;
            }

            items.push(`
                <div class="archive-item-card">
                    <div class="archive-card-info">
                        <span class="archive-card-date">Phylogenle #${pNum} • ${dateStr}</span>
                        <div class="archive-card-sub">${badgeHtml}</div>
                    </div>
                    ${actionsHtml}
                </div>
            `);
        }

        if (items.length === 0) {
            listContainer.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 2rem;">No puzzles match your filter.</div>';
        } else {
            listContainer.innerHTML = items.join('');
            listContainer.querySelectorAll('.archive-play-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const d = btn.getAttribute('data-date');
                    closeModal(archiveModal);
                    loadDatePuzzle(d);
                });
            });

            listContainer.querySelectorAll('.archive-row-reset-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const d = btn.getAttribute('data-date');
                    showInAppConfirm({
                        icon: '🔄',
                        title: 'Reset Puzzle?',
                        message: `Reset puzzle record for ${d}?`,
                        proceedText: 'Reset',
                        proceedBg: '#f59e0b',
                        onProceed: () => {
                            resetDateRecord(d);
                            renderArchiveModal();
                            if (d === currentDateStr) initGame();
                        }
                    });
                });
            });
        }
    }

    function loadDatePuzzle(dateStr) {
        isUnlimited = false;
        currentDateStr = dateStr;
        puzzleNum = getPuzzleNumber(dateStr);
        const url = new URL(window.location);
        url.searchParams.set('date', dateStr);
        url.searchParams.delete('mode');
        window.history.pushState({}, '', url);
        initGame();
    }

    // ==========================================================================
    // Statistics & Past Games History Modal Rendering
    // ==========================================================================
    let selectedStatsGameId = null;

    const RANK_ACCURACY_PCT = {
        'Species': 100.0,
        'Genus': 85.7,
        'Family': 71.4,
        'Order': 57.1,
        'Class': 42.9,
        'Phylum': 28.6,
        'Kingdom': 14.3,
        'Domain': 5.0
    };

    function computeGameAccuracy(rec) {
        if (rec.completed && rec.solved) return 100.0;
        const gList = Array.isArray(rec.guesses) ? rec.guesses : [];
        if (gList.length === 0) return 0.0;
        let best = 5.0;
        for (const g of gList) {
            if (g.isMatch) return 100.0;
            const r = g.lca_rank || g.rank || 'Domain';
            const score = RANK_ACCURACY_PCT[r] || 5.0;
            if (score > best) best = score;
        }
        return best;
    }

    function getGameVisualCategory(rec) {
        if (!rec.completed) return 'unfinished';
        if (!rec.solved) return 'gaveup';
        const hintCount = Array.isArray(rec.hints) ? rec.hints.length : 0;
        if (hintCount > 0) return 'hint';
        const gCount = rec.guessCount || (Array.isArray(rec.guesses) ? rec.guesses.length : 0);
        if (gCount > 0 && gCount <= 3) return 'snipe';
        return 'solved';
    }

    function getCategorySwatchColor(cat) {
        if (cat === 'snipe') return '#eab308';
        if (cat === 'hint') return '#ec4899';
        if (cat === 'solved') return '#8b5cf6';
        if (cat === 'unfinished') return '#38bdf8';
        return 'transparent';
    }

    function formatDisplayDateMMDDYYYY(dateStr, timestamp) {
        if (dateStr && /^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
            const [y, m, d] = dateStr.split('-');
            return `${Number(m)}/${Number(d)}/${y}`;
        }
        if (timestamp) {
            const dt = new Date(timestamp);
            if (!isNaN(dt.getTime())) {
                return `${dt.getMonth() + 1}/${dt.getDate()}/${dt.getFullYear()}`;
            }
        }
        return dateStr || '—';
    }

    function resolveOrganismTitleForRecord(rec) {
        if (!rec.completed) {
            return 'Mystery Organism (In Progress)';
        }
        if (rec.targetSpecies) {
            return rec.targetSpecies;
        }
        // Fallback for legacy completed records missing targetSpecies:
        // Check if last winning guess has name, or deterministically compute from dateStr
        if (Array.isArray(rec.guesses) && rec.guesses.length > 0) {
            const matchGuess = rec.guesses.find(g => g.isMatch);
            if (matchGuess && matchGuess.name) return matchGuess.name;
        }
        if (rec.dateStr && allAnimals && allAnimals.length > 0) {
            try {
                const resolved = getDailyTargetSpecies(
                    rec.dateStr,
                    allAnimals,
                    phylogenyTree ? phylogenyTree.species : null,
                    phylogenyTree ? phylogenyTree.nodes : null,
                    speciesPopularity
                );
                if (resolved) return resolved;
            } catch (e) {
                // ignore
            }
        }
        return `Daily Puzzle #${rec.puzzleNum || ''}`.trim();
    }

    function renderStatsHeatmap(ledger, includeUnfinished) {
        const monthsEl = document.getElementById('stats-heatmap-months');
        const gridEl = document.getElementById('stats-heatmap-grid');
        const unfinLegend = document.getElementById('heatmap-legend-unfinished');
        if (!monthsEl || !gridEl) return;

        if (unfinLegend) {
            unfinLegend.classList.toggle('hidden', !includeUnfinished);
        }

        // Index daily records by YYYY-MM-DD (prefer completed daily over unfinished)
        const byDate = {};
        for (const rec of ledger) {
            const dStr = rec.dateStr;
            if (!dStr) continue;
            if (!byDate[dStr] || (rec.completed && !byDate[dStr].completed) || (rec.mode === 'daily' && byDate[dStr].mode !== 'daily')) {
                byDate[dStr] = rec;
            }
        }

        // Build 53 weeks (371 days) ending on Saturday of the current week
        const today = parseDate(getTodayDateStr());
        const endSaturday = new Date(today);
        endSaturday.setDate(today.getDate() + (6 - today.getDay()));

        const totalWeeks = 53;
        const startSunday = new Date(endSaturday);
        startSunday.setDate(endSaturday.getDate() - (totalWeeks * 7 - 1));

        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const monthCellsHtml = [];
        const dayCellsHtml = [];
        let lastMonth = -1;

        for (let w = 0; w < totalWeeks; w++) {
            const weekStart = new Date(startSunday);
            weekStart.setDate(startSunday.getDate() + w * 7);
            // Determine if a new month starts in this week
            let label = '';
            for (let d = 0; d < 7; d++) {
                const cur = new Date(weekStart);
                cur.setDate(weekStart.getDate() + d);
                if (cur.getDate() === 1 || (w === 0 && d === 0)) {
                    const m = cur.getMonth();
                    if (m !== lastMonth) {
                        label = monthNames[m];
                        lastMonth = m;
                    }
                    break;
                }
            }
            monthCellsHtml.push(`<div class="heatmap-month-label">${label}</div>`);

            for (let d = 0; d < 7; d++) {
                const cur = new Date(weekStart);
                cur.setDate(weekStart.getDate() + d);
                const dStr = formatDate(cur);
                const isFuture = dStr > getTodayDateStr();
                const rec = !isFuture ? byDate[dStr] : null;

                if (rec) {
                    const cat = getGameVisualCategory(rec);
                    const orgTitle = resolveOrganismTitleForRecord(rec);
                    const gCount = rec.guessCount || (Array.isArray(rec.guesses) ? rec.guesses.length : 0);
                    const statusLabel = !rec.completed
                        ? `Unfinished (${gCount} guesses)`
                        : (rec.solved ? `Solved in ${gCount} guess${gCount === 1 ? '' : 'es'}` : `Gave up (${gCount} guesses)`);
                    const tooltip = `${formatDisplayDateMMDDYYYY(dStr)} • ${rec.mode === 'practice' ? 'Practice' : `Daily #${rec.puzzleNum}`} — ${orgTitle} (${statusLabel})`;
                    dayCellsHtml.push(
                        `<div class="heatmap-cell has-game cell-${cat}" data-game-id="${escapeHtml(rec.id)}" data-date="${dStr}" title="${escapeHtml(tooltip)}"></div>`
                    );
                } else {
                    dayCellsHtml.push(
                        `<div class="heatmap-cell" data-date="${dStr}" title="${formatDisplayDateMMDDYYYY(dStr)}"></div>`
                    );
                }
            }
        }

        monthsEl.innerHTML = monthCellsHtml.join('');
        gridEl.innerHTML = dayCellsHtml.join('');

        gridEl.querySelectorAll('.heatmap-cell.has-game').forEach(cell => {
            cell.addEventListener('click', () => {
                const gId = cell.getAttribute('data-game-id');
                if (gId) openStatsGameDetail(gId, ledger);
            });
        });
    }

    function openStatsGameDetail(gameId, ledger) {
        const drawer = document.getElementById('stats-game-detail-drawer');
        if (!drawer) return;

        const rec = ledger.find(r => r.id === gameId);
        if (!rec) {
            drawer.classList.add('hidden');
            return;
        }

        // If the game is unfinished, resume it directly on the board so we never spoil it
        if (!rec.completed && rec.dateStr) {
            closeModal(statsModal);
            loadPuzzleForDate(rec.dateStr);
            return;
        }

        selectedStatsGameId = gameId;
        document.querySelectorAll('#stats-history-tbody tr').forEach(tr => {
            tr.classList.toggle('is-selected', tr.getAttribute('data-game-id') === gameId);
        });

        const orgTitle = resolveOrganismTitleForRecord(rec);
        const commonName = orgTitle.split(' (')[0];
        const gList = Array.isArray(rec.guesses) ? rec.guesses : [];
        const hList = Array.isArray(rec.hints) ? rec.hints : [];
        const gCount = rec.guessCount || gList.length;
        const acc = computeGameAccuracy(rec).toFixed(1);
        const modeBadge = rec.mode === 'practice' ? '∞ Practice' : `Daily #${rec.puzzleNum || getPuzzleNumber(rec.dateStr)}`;
        const dateDisp = formatDisplayDateMMDDYYYY(rec.dateStr, rec.timestamp);
        const outcomeLabel = rec.solved
            ? (gCount <= 3 && hList.length === 0 ? `🎯 Sniped in ${gCount} guess${gCount === 1 ? '' : 'es'}` : `✅ Solved in ${gCount} guess${gCount === 1 ? '' : 'es'}`)
            : `🏳️ Gave Up (${gCount} guess${gCount === 1 ? '' : 'es'})`;

        const guessesHtml = gList.length > 0
            ? gList.map((g, idx) => {
                const emoji = getGuessRankEmoji(g);
                const gName = (g.name || 'Unknown').split(' (')[0];
                const lca = g.lca_name || g.lca_rank || 'Domain';
                const tmrcaStr = g.tmrca === 0 ? '0 MYA' : (typeof g.tmrca === 'number' && g.tmrca > 0 ? `${g.tmrca.toFixed(1)} MYA` : '');
                return `
                    <div class="detail-guess-chip" title="${escapeHtml(g.name || '')} • Shared Clade: ${escapeHtml(lca)}">
                        <div class="detail-guess-left">
                            <span class="detail-guess-idx">#${idx + 1}</span>
                            <span>${emoji}</span>
                            <span class="detail-guess-name">${escapeHtml(gName)}</span>
                        </div>
                        <span class="detail-guess-right">${escapeHtml(lca)}${tmrcaStr ? ` • ${tmrcaStr}` : ''}</span>
                    </div>
                `;
            }).join('')
            : `<div style="font-size: 0.78rem; color: #64748b;">No individual guess log recorded for this game.</div>`;

        const hintsSummaryHtml = hList.length > 0
            ? `<div style="font-size: 0.75rem; color: #f472b6;">💡 Hints used (${hList.length}): ${hList.map(h => `${escapeHtml(h.rank)}: ${escapeHtml(h.name)}`).join(' • ')}</div>`
            : '';

        drawer.innerHTML = `
            <div class="detail-drawer-header">
                <div>
                    <div class="detail-drawer-title">
                        <span>${escapeHtml(orgTitle)}</span>
                        <span style="font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 999px; background: rgba(139, 92, 246, 0.2); color: #c4b5fd;">${escapeHtml(outcomeLabel)}</span>
                    </div>
                    <div class="detail-drawer-subtitle">
                        ${escapeHtml(modeBadge)} • ${escapeHtml(dateDisp)} • Accuracy: ${acc}% • Hints: ${hList.length}
                    </div>
                </div>
                <div class="detail-drawer-actions">
                    <button type="button" id="detail-open-catalog-btn" class="detail-action-btn" title="View organism in Universal Species Catalog">📖 Open in Catalog</button>
                    ${rec.mode !== 'practice' && rec.dateStr ? `<button type="button" id="detail-load-board-btn" class="detail-action-btn" title="Load this date's puzzle on the game board">🗺️ View on Board</button>` : ''}
                    <button type="button" id="detail-close-drawer-btn" class="detail-close-btn" title="Close breakdown">✕</button>
                </div>
            </div>
            ${hintsSummaryHtml}
            <div class="detail-guesses-list">
                ${guessesHtml}
            </div>
        `;
        drawer.classList.remove('hidden');

        document.getElementById('detail-close-drawer-btn')?.addEventListener('click', () => {
            selectedStatsGameId = null;
            drawer.classList.add('hidden');
            document.querySelectorAll('#stats-history-tbody tr').forEach(tr => tr.classList.remove('is-selected'));
        });

        document.getElementById('detail-open-catalog-btn')?.addEventListener('click', () => {
            closeModal(statsModal);
            openCatalogAtTaxon(commonName);
        });

        document.getElementById('detail-load-board-btn')?.addEventListener('click', () => {
            if (rec.dateStr) {
                closeModal(statsModal);
                loadPuzzleForDate(rec.dateStr);
            }
        });
    }

    function renderStatsHistoryTable(ledger) {
        const tbody = document.getElementById('stats-history-tbody');
        const totalEl = document.getElementById('stats-total-count');
        const searchInput = document.getElementById('stats-history-search');
        if (!tbody) return;

        const query = (searchInput ? searchInput.value : '').trim().toLowerCase();
        const filtered = ledger.filter(rec => {
            if (!query) return true;
            const orgTitle = resolveOrganismTitleForRecord(rec).toLowerCase();
            const puzStr = rec.mode === 'practice' ? 'practice' : `#${rec.puzzleNum || ''}`;
            const dateDisp = formatDisplayDateMMDDYYYY(rec.dateStr, rec.timestamp).toLowerCase();
            const rawDate = (rec.dateStr || '').toLowerCase();
            return orgTitle.includes(query) || puzStr.includes(query) || dateDisp.includes(query) || rawDate.includes(query);
        });

        if (totalEl) {
            totalEl.textContent = String(filtered.length);
        }

        if (filtered.length === 0) {
            tbody.innerHTML = `
                <tr class="stats-empty-row">
                    <td colspan="6">No games recorded yet. Play a Daily or Practice puzzle and your history will automatically be saved here!</td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = filtered.map(rec => {
            const cat = getGameVisualCategory(rec);
            const dotColor = getCategorySwatchColor(cat);
            const dotStyle = cat === 'gaveup'
                ? 'background: transparent; border: 1.5px solid #94a3b8;'
                : (cat === 'unfinished' ? 'background: rgba(56,189,248,0.3); border: 1.5px dashed #38bdf8;' : `background: ${dotColor};`);
            const orgTitle = resolveOrganismTitleForRecord(rec);
            const hintCount = Array.isArray(rec.hints) ? rec.hints.length : 0;
            const hintsCell = hintCount > 0 ? `${hintCount}` : '—';
            const gCount = rec.guessCount || (Array.isArray(rec.guesses) ? rec.guesses.length : 0);
            const acc = computeGameAccuracy(rec).toFixed(1);
            const dailyCell = rec.mode === 'practice' ? '∞ Practice' : `#${rec.puzzleNum || getPuzzleNumber(rec.dateStr)}`;
            const dateCell = formatDisplayDateMMDDYYYY(rec.dateStr, rec.timestamp);
            const isSelected = selectedStatsGameId && selectedStatsGameId === rec.id;

            const orgCellHtml = rec.completed
                ? `<span class="history-status-dot" style="${dotStyle}"></span><span class="history-organism-link">${escapeHtml(orgTitle)}</span>`
                : `<span class="history-status-dot" style="${dotStyle}"></span><span class="history-organism-unfinished">${escapeHtml(orgTitle)} — Click to Resume</span>`;

            return `
                <tr data-game-id="${escapeHtml(rec.id)}" class="${isSelected ? 'is-selected' : ''}" title="${rec.completed ? 'Click to inspect guesses & details' : 'Click to resume this unfinished game'}">
                    <td class="col-organism">${orgCellHtml}</td>
                    <td class="col-hints">${hintsCell}</td>
                    <td class="col-guesses">${gCount}</td>
                    <td class="col-accuracy">${acc}%</td>
                    <td class="col-daily">${escapeHtml(dailyCell)}</td>
                    <td class="col-date">${escapeHtml(dateCell)}</td>
                </tr>
            `;
        }).join('');

        tbody.querySelectorAll('tr[data-game-id]').forEach(tr => {
            tr.addEventListener('click', () => {
                const gId = tr.getAttribute('data-game-id');
                if (gId) openStatsGameDetail(gId, ledger);
            });
        });
    }

    function renderStatsModal() {
        const stats = getStats();
        const unfinishedToggle = document.getElementById('stats-unfinished-toggle');
        const includeUnfinished = Boolean(unfinishedToggle && unfinishedToggle.checked);
        const ledger = getAllGamesLedger({ includeUnfinished });

        // Update Account Sync Badge
        const syncBadge = document.getElementById('stats-account-sync-badge');
        if (syncBadge) {
            const user = getCurrentUser ? getCurrentUser() : null;
            if (user) {
                syncBadge.textContent = `☁️ Synced (${user.email || user.displayName || 'Account'})`;
                syncBadge.classList.add('is-synced');
            } else {
                syncBadge.textContent = '💾 Saved Locally (Sign in to sync across devices)';
                syncBadge.classList.remove('is-synced');
            }
        }

        // Top Summary Cards
        const playedEl = document.getElementById('stat-played');
        const streakEl = document.getElementById('stat-streak');
        const maxStreakEl = document.getElementById('stat-max-streak');
        const meanGuessesEl = document.getElementById('stat-mean-guesses');
        const winPctEl = document.getElementById('stat-win-pct');

        if (playedEl) playedEl.textContent = stats.played;
        if (streakEl) streakEl.textContent = stats.currentStreak;
        if (maxStreakEl) maxStreakEl.textContent = stats.maxStreak;
        if (meanGuessesEl) meanGuessesEl.textContent = (stats.meanGuesses || 0).toFixed(1);
        const winPct = stats.played > 0 ? Math.round((stats.won / stats.played) * 100) : 0;
        if (winPctEl) winPctEl.textContent = `${winPct}%`;

        // Render 52-Week Activity Heatmap & Past Games Table
        renderStatsHeatmap(ledger, includeUnfinished);
        renderStatsHistoryTable(ledger);

        // Render Guess Distribution Bars
        const distContainer = document.getElementById('score-distribution-bars');
        if (distContainer) {
            const buckets = ['1-3', '4-6', '7-9', '10-12', '13-15', '16+'];
            const dist = stats.distribution || {};
            const maxVal = Math.max(1, ...buckets.map(b => dist[b] || 0));

            distContainer.innerHTML = buckets.map(bucket => {
                const count = dist[bucket] || 0;
                const pct = Math.max(8, Math.round((count / maxVal) * 100));
                return `
                    <div class="dist-row">
                        <span class="dist-label">${bucket}</span>
                        <div class="dist-bar-wrapper">
                            <div class="dist-bar" style="width: ${count > 0 ? pct : 8}%;">
                                <span>${count}</span>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
    }

    document.getElementById('stats-unfinished-toggle')?.addEventListener('change', () => {
        renderStatsModal();
    });

    document.getElementById('stats-history-search')?.addEventListener('input', () => {
        const unfinishedToggle = document.getElementById('stats-unfinished-toggle');
        const includeUnfinished = Boolean(unfinishedToggle && unfinishedToggle.checked);
        const ledger = getAllGamesLedger({ includeUnfinished });
        renderStatsHistoryTable(ledger);
    });

    onStorageChange(() => {
        if (statsModal && statsModal.classList.contains('active')) {
            renderStatsModal();
        }
        if (archiveModal && archiveModal.classList.contains('active')) {
            renderArchiveModal();
        }
    });

    onAuthChange(() => {
        if (statsModal && statsModal.classList.contains('active')) {
            renderStatsModal();
        }
    });

    // Share Score Functionality
    function shareScore() {
        const shareToast = document.getElementById('share-toast');
        const history = getHistory();
        const record = history[currentDateStr];
        const isSolved = record ? record.solved : (isGameOver && guesses.some(g => g.isMatch));
        const activeGuesses = (record && record.guesses && record.guesses.length > 0) ? record.guesses : guesses;
        const activeHints = (record && record.hints) ? record.hints : revealedHints;
        const count = activeGuesses.length;
        const hintCount = activeHints.length;

        // Emoji feedback row with chronological hints (💡)
        let emojis = getGameTimelineEmojis(activeGuesses, activeHints);
        if (isSolved) {
            emojis += ' ✅'; // Always append green checkbox after all game wins
        } else {
            emojis += ' ⬜'; // Surrender / revealed indicator
        }

        const modeLabel = isUnlimited ? "Practice" : `#${puzzleNum}`;
        const hintText = hintCount > 0 ? ` (${hintCount} hint${hintCount === 1 ? '' : 's'})` : '';
        const statusText = isSolved
            ? `Solved in ${count} guess${count === 1 ? '' : 'es'}${hintText}!`
            : `Revealed${hintText}`;

        const shareText = `Phylogenle ${modeLabel} 🧬\n` +
            `${statusText}\n` +
            `${emojis}\n` +
            `https://amitjoshi2724.github.io/phylogenle/`;

        if (navigator.clipboard) {
            navigator.clipboard.writeText(shareText).then(() => {
                if (shareToast) {
                    shareToast.classList.remove('hidden');
                    setTimeout(() => shareToast.classList.add('hidden'), 2500);
                }
            }).catch(() => alert(shareText));
        } else {
            alert(shareText);
        }
    }

    document.getElementById('share-score-btn')?.addEventListener('click', shareScore);

    window.addEventListener('popstate', () => {
        checkURLParams();
        initGame();
    });

    // Initial load
    checkURLParams();
    initGame();
}

if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", bootPhylogenle);
} else {
    bootPhylogenle();
}
