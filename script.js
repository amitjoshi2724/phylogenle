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
    formatDate 
} from './prng.js';
import { 
    recordDailyCompletion, 
    getStats, 
    getHistory, 
    getRecordForDate, 
    saveActiveGuesses, 
    loadActiveGuesses, 
    clearActiveGuesses,
    resetDateRecord,
    resetAllHistory
} from './storage.js';
import './auth.js'; // Initializes Google Auth singleton & UI

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
    const modeToggleBtn = document.getElementById('mode-toggle-btn');
    const treeContainer = document.getElementById('tree-container');

    // Modals
    const archiveModal = document.getElementById('archive-modal');
    const statsModal = document.getElementById('stats-modal');
    const helpModal = document.getElementById('help-modal');

    // Game State
    let isUnlimited = false;
    let currentDateStr = getTodayDateStr();
    let puzzleNum = getPuzzleNumber(currentDateStr);
    let allSpecies = [];
    let targetSpecies = "";
    let targetData = {};
    let phylogenyTree = null;
    let currentFocus = -1;
    let guesses = [];
    let guessedSet = new Set();
    let isGameOver = false;

    // Calendar state
    const todayObj = parseDate(currentDateStr);
    let calYear = todayObj.getFullYear();
    let calMonth = todayObj.getMonth();

    // Wikipedia Tooltip Setup
    const wikiTooltip = document.getElementById('wiki-tooltip');
    const wikiTitle = wikiTooltip.querySelector('.wiki-title');
    const wikiSnippet = wikiTooltip.querySelector('.wiki-snippet');
    let tooltipTimeout;

    async function showWikiTooltip(e, rankName) {
        clearTimeout(tooltipTimeout);
        wikiTooltip.classList.remove('hidden');
        
        let left = e.pageX + 15;
        let top = e.pageY + 15;
        
        if (left + 300 > window.innerWidth) {
            left = window.innerWidth - 320;
        }
        
        wikiTooltip.style.left = left + 'px';
        wikiTooltip.style.top = top + 'px';
        wikiTooltip.style.pointerEvents = 'auto';
        
        wikiTitle.innerHTML = `<a href="https://en.wikipedia.org/wiki/${encodeURIComponent(rankName)}" target="_blank">${rankName} &#8594;</a>`;
        wikiSnippet.textContent = "Loading summary...";

        try {
            const resp = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(rankName)}`);
            const data = await resp.json();
            if (data.extract) {
                wikiSnippet.textContent = data.extract.substring(0, 180) + "...";
            } else {
                wikiSnippet.textContent = "No Wikipedia summary available.";
            }
        } catch (err) {
            wikiSnippet.textContent = "Error loading summary.";
        }
    }

    function hideWikiTooltip() {
        tooltipTimeout = setTimeout(() => {
            wikiTooltip.classList.add('hidden');
            wikiTooltip.style.pointerEvents = 'none';
        }, 150);
    }

    wikiTooltip.addEventListener('mouseenter', () => clearTimeout(tooltipTimeout));
    wikiTooltip.addEventListener('mouseleave', hideWikiTooltip);

    // Check URL parameters on load
    function checkURLParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const modeParam = urlParams.get('mode');
        const dateParam = urlParams.get('date');

        if (modeParam === 'unlimited' || modeParam === 'practice') {
            isUnlimited = true;
        } else if (dateParam && /^\d{4}-\d{2}-\d{2}$/.test(dateParam)) {
            currentDateStr = dateParam;
            puzzleNum = getPuzzleNumber(dateParam);
            isUnlimited = false;
        }
        updateModeUI();
    }

    function updateModeUI() {
        if (!modeToggleBtn) return;
        if (isUnlimited) {
            modeToggleBtn.textContent = 'DAILY';
            modeToggleBtn.classList.add('unlimited-active');
            modeToggleBtn.title = 'Switch to Daily Puzzle Mode';
            if (puzzleBadge) puzzleBadge.textContent = 'PRACTICE MODE 🧬';
        } else {
            modeToggleBtn.textContent = 'PRACTICE';
            modeToggleBtn.classList.remove('unlimited-active');
            modeToggleBtn.title = 'Switch to Unlimited Practice Mode';
            const isToday = currentDateStr === getTodayDateStr();
            if (puzzleBadge) {
                puzzleBadge.textContent = `DAILY #${puzzleNum} • ${currentDateStr}${isToday ? ' (TODAY)' : ''}`;
            }
        }
    }

    // Initialize Game
    async function initGame() {
        try {
            if (allSpecies.length === 0 || !phylogenyTree) {
                if (guessesContainer && guessesContainer.children.length === 0) {
                    guessesContainer.innerHTML = `<div class="loading-state" style="text-align: center; padding: 2rem; color: var(--text-secondary);"><span style="display:inline-block; font-size: 1.5rem; animation: spin 1.2s linear infinite; margin-bottom: 0.5rem;">🧬</span><br>Loading evolutionary tree of life...</div>`;
                }

                const [speciesResp, treeResp] = await Promise.all([
                    allSpecies.length === 0 ? fetch('data/species_list.json?v=tree_8') : Promise.resolve(null),
                    !phylogenyTree ? fetch('data/phylogeny_tree.json?v=tree_8') : Promise.resolve(null)
                ]);

                if (speciesResp) {
                    if (!speciesResp.ok) throw new Error(`HTTP ${speciesResp.status} loading species list`);
                    allSpecies = await speciesResp.json();
                }

                if (treeResp) {
                    if (!treeResp.ok) throw new Error(`HTTP ${treeResp.status} loading phylogeny tree`);
                    phylogenyTree = await treeResp.json();
                }
            }

            if (isUnlimited) {
                targetSpecies = allSpecies[Math.floor(Math.random() * allSpecies.length)];
            } else {
                targetSpecies = getDailyTargetSpecies(allSpecies, currentDateStr);
            }

            // Reset round variables
            guesses = [];
            guessedSet = new Set();
            isGameOver = false;
            guessesContainer.innerHTML = '';
            gameEndPanel.classList.add('hidden');
            if (inputSection) inputSection.style.display = 'flex';
            animalInput.value = '';

            updateModeUI();

            // If daily, check if already completed
            if (!isUnlimited) {
                const existing = getRecordForDate(currentDateStr);
                if (existing && existing.completed) {
                    restoreCompletedGame(existing);
                    return;
                }

                // Check for in-progress saved guesses
                const active = loadActiveGuesses(currentDateStr);
                if (active && Array.isArray(active) && active.length > 0) {
                    active.forEach(g => {
                        const guessKey = g.name.toLowerCase();
                        guessedSet.add(guessKey);
                        guesses.push(g);
                        addGuessToBoard(g.name, g.wikiTitle, {
                    rank: g.lca_rank,
                    lca_name: g.lca_name,
                    major_name: g.major_name || g.lca_name,
                    time: g.tmrca
                }, g.isMatch);
                    });
                    updateTree();
                    return;
                }
            }

            drawTree({ name: "?", children: [] });
        } catch (error) {
            console.error("Failed to initialize game:", error);
            guessesContainer.innerHTML = `<div class="error" style="color: #ef4444; padding: 1rem;">Failed to load game data. Please run via a local web server (http://).</div>`;
        }
    }

    function restoreCompletedGame(record) {
        isGameOver = true;
        if (inputSection) inputSection.style.display = 'none';

        endTitle.textContent = record.solved ? "You found it! ⭐" : "Organism Revealed";
        endTitle.style.color = record.solved ? "var(--success-color)" : "var(--danger-color)";
        endMessage.innerHTML = `The organism was <strong>${record.targetSpecies || targetSpecies}</strong>.<br>` +
            `<span style="font-size: 0.9rem; color: var(--text-secondary);">${record.solved ? `Solved in ${record.guessCount} guesses!` : 'Gave up.'}</span>`;

        const endEmojisRow = document.getElementById('end-emojis-row');
        if (endEmojisRow && record.guesses && record.guesses.length > 0) {
            let emojis = record.guesses.map(g => getGuessRankEmoji(g)).join('');
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
            record.guesses.forEach(g => {
                const guessKey = g.name.toLowerCase();
                guessedSet.add(guessKey);
                guesses.push(g);
                addGuessToBoard(g.name, g.wikiTitle, {
                    rank: g.lca_rank,
                    lca_name: g.lca_name,
                    major_name: g.major_name || g.lca_name,
                    time: g.tmrca
                }, g.isMatch);
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
                    emoji: record.solved ? '🟩' : '⬜'
                }]
            });
        }
    }

    // Toggle Dropdown
    function showDropdown() {
        if (isGameOver) return;
        const val = animalInput.value.toLowerCase().trim();
        let listHTML = '';
        let matchCount = 0;
        
        if (!val) {
            for (const species of allSpecies) {
                listHTML += `<li class="autocomplete-item" data-value="${species}">${species}</li>`;
                if (++matchCount >= 60) break;
            }
        } else {
            const startsWith = [];
            const wordMatch = [];
            const subMatch = [];

            for (const species of allSpecies) {
                const sLower = species.toLowerCase();
                const idx = sLower.indexOf(val);
                if (idx === -1) continue;

                if (idx === 0) {
                    startsWith.push(species);
                } else if (sLower[idx - 1] === ' ' || sLower[idx - 1] === '(' || sLower[idx - 1] === '-') {
                    wordMatch.push(species);
                } else {
                    subMatch.push(species);
                }
            }

            const candidates = [...startsWith, ...wordMatch, ...subMatch];
            for (const species of candidates) {
                const idx = species.toLowerCase().indexOf(val);
                const displayHtml = species.substring(0, idx) + "<strong>" + species.substring(idx, idx + val.length) + "</strong>" + species.substring(idx + val.length);
                
                if (guessedSet.has(species.toLowerCase())) {
                    listHTML += `<li class="autocomplete-item guessed-item" style="opacity: 0.45; pointer-events: none; cursor: default;" data-value="${species}">${displayHtml} (Already Guessed)</li>`;
                } else {
                    listHTML += `<li class="autocomplete-item" data-value="${species}">${displayHtml}</li>`;
                }
                if (++matchCount >= 80) break;
            }
        }
        
        if (listHTML) {
            autocompleteList.innerHTML = listHTML;
            autocompleteList.classList.add('active');
            
            const items = autocompleteList.getElementsByClassName('autocomplete-item');
            for (let i = 0; i < items.length; i++) {
                const selectItem = (e) => {
                    e.preventDefault();
                    animalInput.value = items[i].getAttribute('data-value');
                    closeDropdown();
                    handleGuess();
                };
                items[i].addEventListener('mousedown', selectItem);
                items[i].addEventListener('click', selectItem);
            }
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

    animalInput.addEventListener('click', showDropdown);
    animalInput.addEventListener('input', showDropdown);
    animalInput.addEventListener('keyup', showDropdown);
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
            addActive(x);
        } else if (e.keyCode === 38) { // Up
            currentFocus--;
            addActive(x);
        } else if (e.keyCode === 13) { // Enter
            e.preventDefault();
            if (currentFocus > -1 && x && x[currentFocus]) {
                x[currentFocus].click();
            } else if (animalInput.value) {
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

    function getEvolutionaryComparison(guess, target) {
        const guessKey = guess.toLowerCase();
        const targetKey = target.toLowerCase();
        if (guessKey === targetKey) {
            const latinMatch = guess.match(/\((.*?)\)/);
            const sci = latinMatch ? latinMatch[1] : guess;
            return { time: 0.0, rank: "Species", lca_name: sci, major_name: sci, major_rank: "Species", major_time: 0.0 };
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

        let validGuess = allSpecies.find(s => s.toLowerCase() === guess.toLowerCase());
        if (!validGuess) {
            // Also match common name, scientific name inside parentheses, or prefix
            const g = guess.toLowerCase();
            validGuess = allSpecies.find(s => {
                const common = s.split(' (')[0].toLowerCase();
                const sciMatch = s.match(/\((.*?)\)/);
                const sci = sciMatch ? sciMatch[1].toLowerCase() : '';
                return common === g || sci === g;
            });
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
        const isMatch = guessKey === targetSpecies.toLowerCase();

        const latinNameMatch = validGuess.match(/\((.*?)\)/);
        const wikiTitle = latinNameMatch ? latinNameMatch[1] : validGuess;

        const guessObj = {
            name: validGuess,
            wikiTitle: wikiTitle,
            lca_rank: data.rank,
            lca_name: data.lca_name || data.rank,
            major_name: data.major_name || data.lca_name || data.rank,
            major_rank: data.major_rank || data.rank,
            major_time: data.major_time !== undefined ? data.major_time : data.time,
            tmrca: data.time,
            isMatch: isMatch
        };

        guesses.push(guessObj);
        addGuessToBoard(validGuess, wikiTitle, data, isMatch);
        updateTree();

        // Save active progress if daily
        if (!isUnlimited) {
            saveActiveGuesses(currentDateStr, guesses);
        }

        animalInput.value = '';
        closeDropdown();

        if (isMatch) {
            finishGame(true);
        }
    }

    function getGuessRankEmoji(g) {
        if (g.isMatch || g.lca_rank === 'Species') return '🟩';
        const r = g.lca_rank;
        if (r === 'Genus') return '🟨'; // yellow - genus match
        if (r === 'Family') return '🟧'; // orange - family
        if (r === 'Order') return '🟥'; // red - order
        if (r === 'Class') return '🟪'; // purple - class
        if (r === 'Phylum') return '🟦'; // blue - phylum
        if (r === 'Kingdom') return '🟫'; // brown - kingdom
        return '⬛'; // black - nothing match
    }

    function getClosenessInfo(data, isMatch) {
        if (isMatch || data.rank === 'Species') {
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

    function addGuessToBoard(guessName, wikiTitle, data, isMatch) {
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

        row.innerHTML = `
            <div class="guess-header">
                <span class="guess-name ${matchClass} taxa-link">${guessName}</span>
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
        row.innerHTML = `
            <div class="guess-header">
                <span class="guess-name match-exact taxa-link">${species}</span>
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
        endMessage.innerHTML = `The organism was <strong>${targetSpecies}</strong>.<br>` +
            `<span style="font-size: 0.9rem; color: var(--text-secondary);">${win ? `Solved in ${guesses.length} guess${guesses.length === 1 ? '' : 'es'}!` : 'Surrendered & revealed.'}</span>`;

        if (!win) {
            addSurrenderRow(targetSpecies);
        }

        const endEmojisRow = document.getElementById('end-emojis-row');
        if (endEmojisRow) {
            let emojis = guesses.map(g => getGuessRankEmoji(g)).join('');
            if (!win) {
                emojis += ' ⬜'; // White square indicates surrendered / revealed
            }
            endEmojisRow.textContent = emojis;
        }

        animalInput.parentElement.style.display = 'none';
        guessBtn.style.display = 'none';
        giveUpBtn.style.display = 'none';
        gameEndPanel.classList.remove('hidden');

        updateTree();

        if (!isUnlimited) {
            recordDailyCompletion(currentDateStr, puzzleNum, win, guesses.length, guesses, targetSpecies);
            clearActiveGuesses(currentDateStr);
            if (win) {
                setTimeout(() => openModal(statsModal), 1000);
            }
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

    playAgainBtn.addEventListener('click', () => {
        if (isUnlimited) {
            initGame();
        } else {
            // Switch to practice or load today
            isUnlimited = true;
            initGame();
        }
    });

    modeToggleBtn.addEventListener('click', () => {
        isUnlimited = !isUnlimited;
        if (isUnlimited) {
            initGame();
        } else {
            currentDateStr = getTodayDateStr();
            puzzleNum = getPuzzleNumber(currentDateStr);
            initGame();
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
            if (d.data.isMatch) return '🟩';
            if (isGameOver) return '⬜';
            return '⬜';
        }
        if (d.data.isGuess) {
            return d.data.emoji || '🟨';
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
        const t = (d.data.name || '').toLowerCase();
        const taxonMap = {
            'animalia': '🟫', 'metazoa': '🟫', 'plantae': '🟫', 'viridiplantae': '🟫', 'fungi': '🟫',
            'eukaryota': '⬛', 'bacteria': '⬛', 'archaea': '⬛', 'cellular organisms': '⬛', 'life': '⬛', 'root': '⬛',
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
        const mysteryEmoji = hasMatch ? '🟩' : (isGameOver ? '⬜' : '⬜');
        const mysteryNode = {
            name: mysteryName,
            wikiTitle: mysteryWiki,
            isMystery: true,
            isMatch: hasMatch,
            isRevealed: isRevealed,
            emoji: mysteryEmoji
        };

        function getTargetRootInfo() {
            let defaultRootName = "Animalia";
            let defaultRank = "Kingdom";
            const targetLin = (phylogenyTree && phylogenyTree.species) ? phylogenyTree.species[targetSpecies.toLowerCase()] : null;
            if (targetLin && phylogenyTree.nodes) {
                for (let tid of targetLin) {
                    const n = phylogenyTree.nodes[tid];
                    if (n && (n.rank === "Kingdom" || n.rank === "Domain")) {
                        defaultRootName = n.major_name || n.name;
                        defaultRank = n.rank;
                        break;
                    }
                }
            }
            return { name: defaultRootName, rank: defaultRank };
        }

        if (sortedGuesses.length === 0) {
            if (isGameOver) {
                const tr = getTargetRootInfo();
                drawTree({
                    name: tr.name,
                    rank: tr.rank,
                    isTrunk: true,
                    children: [mysteryNode]
                });
            } else {
                drawTree({ name: "?", emoji: '⬜', isMystery: true, children: [] });
            }
            return;
        }

        const trunkMap = new Map();

        sortedGuesses.forEach(g => {
            if (g.isMatch) return;
            // 1. Major Linnaean rank node (e.g. Mammalia, Carnivora, Chordata)
            if (g.major_name && g.major_name !== g.lca_name && g.major_name !== 'Unknown' && g.major_name !== 'root') {
                if (!trunkMap.has(g.major_name)) {
                    trunkMap.set(g.major_name, {
                        name: g.major_name,
                        rank: g.major_rank || g.lca_rank,
                        time: g.major_time !== undefined ? g.major_time : (g.tmrca * 1.5),
                        isTrunk: true,
                        guessChildren: []
                    });
                }
            }

            // 2. Specific LCA subclade node (e.g. Boreoeutheria, Caniformia)
            if (!trunkMap.has(g.lca_name)) {
                trunkMap.set(g.lca_name, {
                    name: g.lca_name,
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

        const trunkList = Array.from(trunkMap.values()).sort((a, b) => {
            const tA = a.time === -1 ? Infinity : a.time;
            const tB = b.time === -1 ? Infinity : b.time;
            return tB - tA;
        });

        if (trunkList.length === 0) {
            const tr = getTargetRootInfo();
            drawTree({
                name: tr.name,
                rank: tr.rank,
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
        const topNames = new Set(["Life", "Cellular organisms", "cellular organisms", "root", "Eukaryota", "Bacteria", "Archaea", "Animalia", "Metazoa", "Plantae", "Viridiplantae", "Fungi"]);
        if (!topRanks.has(root.rank) && !topNames.has(root.name)) {
            const tr = getTargetRootInfo();
            root = { name: tr.name, rank: tr.rank, isTrunk: true, children: [root] };
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
                    const query = d.data.wikiTitle || d.data.name;
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
    // Modals & Navigation Handling
    // ==========================================================================
    function openModal(modal) {
        if (!modal) return;
        modal.classList.add('active');
        if (modal === archiveModal) renderArchiveModal();
        if (modal === statsModal) renderStatsModal();
    }

    function closeModal(modal) {
        if (!modal) return;
        modal.classList.remove('active');
    }

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

        // Show last 60 days in list
        for (let i = 0; i < 60; i++) {
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
    // Statistics Modal Rendering
    // ==========================================================================
    function renderStatsModal() {
        const stats = getStats();

        document.getElementById('stat-played').textContent = stats.played;
        const winPct = stats.played > 0 ? Math.round((stats.won / stats.played) * 100) : 0;
        document.getElementById('stat-win-pct').textContent = `${winPct}%`;
        document.getElementById('stat-streak').textContent = stats.currentStreak;
        document.getElementById('stat-max-streak').textContent = stats.maxStreak;

        const distContainer = document.getElementById('score-distribution-bars');
        if (!distContainer) return;

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

    // Share Score Functionality
    function shareScore() {
        const shareToast = document.getElementById('share-toast');
        const history = getHistory();
        const record = history[currentDateStr];
        const isSolved = record ? record.solved : (isGameOver && guesses.some(g => g.isMatch));
        const count = guesses.length;

        // Emoji feedback row
        let emojis = guesses.slice(0, 10).map(g => getGuessRankEmoji(g)).join('');
        if (!isSolved) {
            emojis += ' ⬜'; // Surrender / revealed indicator
        }

        const shareText = `Phylogenle #${puzzleNum} 🧬\n` +
            `${isSolved ? `Solved in ${count} guess${count === 1 ? '' : 'es'}!` : 'Revealed'}\n` +
            `${emojis}${guesses.length > 10 ? '...' : ''}\n` +
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

    // Initial load
    checkURLParams();
    initGame();
}

if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", bootPhylogenle);
} else {
    bootPhylogenle();
}
