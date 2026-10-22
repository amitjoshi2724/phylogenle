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
            if (allSpecies.length === 0) {
                const response = await fetch('data/species_list.json');
                allSpecies = await response.json();
            }

            if (isUnlimited) {
                targetSpecies = allSpecies[Math.floor(Math.random() * allSpecies.length)];
            } else {
                targetSpecies = getDailyTargetSpecies(allSpecies, currentDateStr);
            }

            const targetFilename = targetSpecies.toLowerCase().replace(/ /g, "_") + ".json";
            const targetResponse = await fetch(`data/${targetFilename}`);
            targetData = await targetResponse.json();

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
                        addGuessToBoard(g.name, g.wikiTitle, { rank: g.lca_rank, lca_name: g.lca_name, time: g.tmrca }, g.isMatch);
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
                addGuessToBoard(g.name, g.wikiTitle, { rank: g.lca_rank, lca_name: g.lca_name, time: g.tmrca }, g.isMatch);
            });
            updateTree();
        } else {
            const latinMatch = (record.targetSpecies || targetSpecies).match(/\((.*?)\)/);
            const name = (record.targetSpecies || targetSpecies).split(' (')[0];
            const wiki = latinMatch ? latinMatch[1] : name;
            drawTree({
                name: "Animalia",
                isTrunk: true,
                children: [{
                    name: name,
                    wikiTitle: wiki,
                    isMystery: true,
                    isMatch: true
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
        
        for (const species of allSpecies) {
            if (!val || species.toLowerCase().includes(val)) {
                let displayHtml = species;
                if (val) {
                    const idx = species.toLowerCase().indexOf(val);
                    displayHtml = species.substring(0, idx) + "<strong>" + species.substring(idx, idx + val.length) + "</strong>" + species.substring(idx + val.length);
                }
                
                if (guessedSet.has(species.toLowerCase())) {
                    listHTML += `<li class="autocomplete-item guessed-item" style="opacity: 0.45; pointer-events: none; cursor: default;" data-value="${species}">${displayHtml} (Already Guessed)</li>`;
                } else {
                    listHTML += `<li class="autocomplete-item" data-value="${species}">${displayHtml}</li>`;
                }
                matchCount++;
                if (matchCount >= 40) break; // Keep list snappy
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

        if (!targetData[guessKey]) {
            alert("Evolutionary comparison data not available for this pair.");
            return;
        }

        const data = targetData[guessKey];
        const isMatch = guessKey === targetSpecies.toLowerCase();

        const latinNameMatch = validGuess.match(/\((.*?)\)/);
        const wikiTitle = latinNameMatch ? latinNameMatch[1] : validGuess;

        const guessObj = {
            name: validGuess,
            wikiTitle: wikiTitle,
            lca_rank: data.rank,
            lca_name: data.lca_name || data.rank,
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
                label: 'Exact Match (0 MYA)',
                shortLabel: 'Exact Match',
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
            rank: 'Nothing',
            emoji: '⬛',
            label: 'No Match',
            shortLabel: 'No Match',
            cssClass: 'closeness-nothing',
            squareClass: 'square-nothing'
        };
    }

    function addGuessToBoard(guessName, wikiTitle, data, isMatch) {
        const closeness = getClosenessInfo(data, isMatch);
        const row = document.createElement('div');
        row.className = `guess-row ${closeness.cssClass}`;
        const matchClass = isMatch ? 'match-exact' : '';

        const timeStr = data.time === 0 ? "Exact Match" : (data.time === -1.0 ? "Unknown (>500 MYA)" : `${data.time.toFixed(1)} MYA`);
        const lcaName = data.lca_name || data.rank;

        row.innerHTML = `
            <div class="guess-main-info">
                <span class="closeness-pill ${closeness.cssClass}" title="${closeness.label}">
                    <span class="rank-square-icon ${closeness.squareClass}"></span> ${closeness.shortLabel}
                </span>
                <span class="guess-name ${matchClass} taxa-link">${guessName}</span>
            </div>
            <div class="guess-feedback">
                <span class="feedback-badge feedback-time ${matchClass}" title="Estimated evolutionary divergence time">Diverged: ${timeStr}</span>
                <span class="feedback-badge feedback-rank ${matchClass} taxa-link" data-taxa="${lcaName}">${data.rank}: ${lcaName}</span>
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

    function finishGame(win) {
        isGameOver = true;
        endTitle.textContent = win ? "You found it! 🏆" : "Organism Revealed";
        endTitle.style.color = win ? "var(--success-color)" : "var(--danger-color)";
        endMessage.innerHTML = `The organism was <strong>${targetSpecies}</strong>.<br>` +
            `<span style="font-size: 0.9rem; color: var(--text-secondary);">${win ? `Solved in ${guesses.length} guess${guesses.length === 1 ? '' : 'es'}!` : 'Better luck next time!'}</span>`;

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
        if (confirm("Are you sure you want to give up and reveal the mystery organism?")) {
            finishGame(false);
        }
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
    function updateTree() {
        const sortedGuesses = [...guesses].sort((a, b) => {
            const timeA = a.tmrca === -1 ? Infinity : a.tmrca;
            const timeB = b.tmrca === -1 ? Infinity : b.tmrca;
            return timeB - timeA;
        });

        if (sortedGuesses.length === 0) {
            drawTree({ name: "?", children: [] });
            return;
        }

        let root = null;
        let prevLCA = null;

        sortedGuesses.forEach(g => {
            if (g.isMatch) return;
            const commonName = g.name.split(' (')[0];
            const guessNode = { name: commonName, wikiTitle: g.wikiTitle, isGuess: true };

            if (!prevLCA || prevLCA.name !== g.lca_name) {
                const newLCA = { name: g.lca_name, isTrunk: true, children: [guessNode] };
                if (prevLCA) {
                    prevLCA.children.push(newLCA);
                } else {
                    root = newLCA;
                }
                prevLCA = newLCA;
            } else {
                prevLCA.children.push(guessNode);
            }
        });

        const hasMatch = sortedGuesses.some(g => g.isMatch);
        const mysteryName = hasMatch ? targetSpecies.split(' (')[0] : "?";
        const latinMatch = targetSpecies.match(/\((.*?)\)/);
        const mysteryWiki = latinMatch ? latinMatch[1] : mysteryName;
        const mysteryNode = { name: mysteryName, wikiTitle: mysteryWiki, isMystery: true, isMatch: hasMatch };

        if (!root) {
            root = { name: sortedGuesses[0].lca_name || "LCA", isTrunk: true, children: [mysteryNode] };
        } else {
            prevLCA.children.push(mysteryNode);
        }

        if (root.name !== "Metazoa" && root.name !== "Animalia") {
            root = { name: "Animalia", isTrunk: true, children: [root] };
        }

        drawTree(root);
    }

    function drawTree(treeData) {
        if (!treeContainer) return;
        treeContainer.innerHTML = '';

        const margin = { top: 60, right: 40, bottom: 80, left: 40 };
        const containerWidth = treeContainer.clientWidth || 600;
        const containerHeight = Math.max(500, treeContainer.clientHeight || 500);

        // Count leaf nodes for dynamic minimum width
        const hierarchyData = d3.hierarchy(treeData, d => d.children);
        const leafNodes = hierarchyData.leaves();
        const leafCount = leafNodes.length;

        // Dynamic width: allocates at least 85px per leaf so text never squeezes
        const computedWidth = Math.max(containerWidth - margin.left - margin.right, leafCount * 85, 450);
        const computedHeight = Math.max(containerHeight - margin.top - margin.bottom, (guesses.length + 2) * 55, 380);

        const svg = d3.select("#tree-container").append("svg")
            .attr("width", computedWidth + margin.left + margin.right)
            .attr("height", computedHeight + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left}, ${margin.top})`);

        const treeMap = d3.tree().size([computedWidth, computedHeight]);
        const treeNodes = treeMap(hierarchyData);
        const allDescendants = treeNodes.descendants();

        // Calculate dynamic font size based on node horizontal density
        const minSpacing = computedWidth / Math.max(leafCount, 1);
        const dynamicFontSize = Math.max(9, Math.min(13, Math.floor(minSpacing / 7) + 2));

        // Draw Links
        svg.selectAll(".link")
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
        childNodes.forEach((node, idx) => {
            const approxWidth = (node.data.name || "").length * (dynamicFontSize * 0.65) + 16;
            const dist = node.x - lastChildX;
            // Overlap check based on actual text bounding width
            const minSafeDist = Math.max(110, (approxWidth + lastChildWidth) / 2 + 18);
            if (dist < minSafeDist) {
                currentChildTier = (currentChildTier + 1) % 3;
            } else {
                currentChildTier = 0;
            }
            node.staggerTier = currentChildTier;
            lastChildX = node.x;
            lastChildWidth = approxWidth;
        });

        // Smart Vertical Staggering for trunk nodes (d.data.isTrunk is true)
        const trunkNodes = allDescendants.filter(d => d.data.isTrunk).sort((a, b) => a.x - b.x);
        let currentTrunkTier = 0;
        let lastTrunkX = -999;
        trunkNodes.forEach(node => {
            if (node.x - lastTrunkX < 75) {
                currentTrunkTier = (currentTrunkTier + 1) % 2;
            } else {
                currentTrunkTier = 0;
            }
            node.trunkTier = currentTrunkTier;
            lastTrunkX = node.x;
        });

        // Nodes Group
        const node = svg.selectAll(".node")
            .data(allDescendants)
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${d.x}, ${d.y})`);

        // Vertical Dashed Stagger Leader Lines for offset child nodes
        node.each(function(d) {
            if (!d.data.isTrunk && d.staggerTier > 0) {
                const targetY = d.staggerTier === 1 ? 38 : 58;
                d3.select(this).append("line")
                    .attr("class", "node-stagger-line")
                    .attr("x1", 0)
                    .attr("y1", 8)
                    .attr("x2", 0)
                    .attr("y2", targetY - 10);
            }
        });

        // Node Circles
        node.append("circle")
            .attr("r", d => d.data.isMystery ? 10 : 7)
            .style("fill", d => {
                if (d.data.isMystery) return d.data.isMatch ? "var(--success-color)" : "#60a5fa";
                if (d.data.isGuess) return "var(--warning-color)";
                return "var(--bg-primary)";
            })
            .style("stroke", d => {
                if (d.data.isMystery) return "#ffffff";
                if (d.data.isGuess) return "#f59e0b";
                return "var(--accent-color)";
            });

        // Calculate Y Offset per node
        function getNodeYOffset(d) {
            if (d.data.isTrunk) {
                return d.trunkTier === 1 ? -32 : -18;
            }
            if (d.staggerTier === 1) return 38;
            if (d.staggerTier === 2) return 58;
            return 20;
        }

        // Background Pill/Backdrop for maximum contrast and legibility
        node.append("rect")
            .attr("class", "node-label-bg")
            .attr("height", dynamicFontSize + 8)
            .attr("y", d => getNodeYOffset(d) - dynamicFontSize / 2 - 4)
            .attr("opacity", 0.9);

        // Text Labels
        const textLabels = node.append("text")
            .attr("dy", ".35em")
            .attr("y", d => getNodeYOffset(d))
            .style("text-anchor", "middle")
            .style("font-size", `${dynamicFontSize}px`)
            .attr("class", "taxa-link node-label-text")
            .text(d => d.data.name)
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
                rectEl.attr("x", bbox.x - 6)
                      .attr("width", bbox.width + 12);
            }
        });
    }

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
            if (confirm("Reset puzzle record for " + currentDateStr + "? This allows you to replay with the updated species target.")) {
                resetDateRecord(currentDateStr);
                renderArchiveModal();
                initGame();
            }
        });
    }

    const archiveResetAllBtn = document.getElementById('archive-reset-all-btn');
    if (archiveResetAllBtn) {
        archiveResetAllBtn.addEventListener('click', () => {
            if (confirm("Are you sure you want to reset all past puzzle records and statistics? This will clear your archive history so all dates can be replayed freshly with the updated species dataset.")) {
                resetAllHistory();
                renderArchiveModal();
                initGame();
            }
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
                    resetDateRecord(d);
                    renderArchiveModal();
                    if (d === currentDateStr) initGame();
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
