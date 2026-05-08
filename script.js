document.addEventListener('DOMContentLoaded', () => {
    const animalInput = document.getElementById('animal-input');
    const autocompleteList = document.getElementById('autocomplete-list');
    const guessBtn = document.getElementById('guess-btn');
    const giveUpBtn = document.getElementById('give-up-btn');
    const guessesContainer = document.getElementById('guesses-container');
    const gameEndPanel = document.getElementById('game-end-panel');
    const endTitle = document.getElementById('end-title');
    const endMessage = document.getElementById('end-message');
    const playAgainBtn = document.getElementById('play-again-btn');

    let allSpecies = [];
    let targetSpecies = "";
    let targetData = {};
    let selectedSpecies = "";
    let currentFocus = -1;
    let guesses = [];
    let guessedSet = new Set();
    
    // Wikipedia Tooltip setup
    const wikiTooltip = document.getElementById('wiki-tooltip');
    const wikiTitle = wikiTooltip.querySelector('.wiki-title');
    const wikiSnippet = wikiTooltip.querySelector('.wiki-snippet');
    let tooltipTimeout;

    async function showWikiTooltip(e, rankName) {
        clearTimeout(tooltipTimeout);
        wikiTooltip.classList.remove('hidden');
        
        let left = e.pageX + 15;
        let top = e.pageY + 15;
        
        // Prevent tooltip from going off-screen
        if (left + 300 > window.innerWidth) {
            left = window.innerWidth - 320;
        }
        
        wikiTooltip.style.left = left + 'px';
        wikiTooltip.style.top = top + 'px';
        wikiTooltip.style.pointerEvents = 'auto'; // Allow clicking inside
        
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

    // Taxonomy rank order for display (lower index = closer relative)
    const rankOrder = {
        "Species": 0,
        "Genus": 1,
        "Family": 2,
        "Order": 3,
        "Class": 4,
        "Phylum": 5,
        "Kingdom": 6,
        "Domain": 7
    };

    // Initialize game
    async function initGame() {
        try {
            // Load species list
            const response = await fetch('data/species_list.json');
            allSpecies = await response.json();
            
            // Pick a random target species
            targetSpecies = allSpecies[Math.floor(Math.random() * allSpecies.length)];
            
            // Fetch target species data
            const targetFilename = targetSpecies.toLowerCase().replace(/ /g, "_") + ".json";
            const targetResponse = await fetch(`data/${targetFilename}`);
            targetData = await targetResponse.json();
            
            console.log("Game initialized. Target:", targetSpecies); // For debugging
        } catch (error) {
            console.error("Failed to initialize game:", error);
            guessesContainer.innerHTML = `<div class="error">Failed to load game data. Are you running a local server?</div>`;
        }
        drawTree({ name: "?", children: [] });
    }

    // Toggle dropdown based on input focus/click
    function showDropdown() {
        const val = animalInput.value.toLowerCase();
        let listHTML = '';
        
        allSpecies.forEach(species => {
            if (!val || species.toLowerCase().includes(val)) {
                // Bold the matching part if there is a value
                let displayHtml = species;
                if (val) {
                    const idx = species.toLowerCase().indexOf(val);
                    displayHtml = species.substring(0, idx) + "<strong>" + species.substring(idx, idx + val.length) + "</strong>" + species.substring(idx + val.length);
                }
                
                if (guessedSet.has(species.toLowerCase())) {
                    listHTML += `<li class="autocomplete-item guessed-item" style="opacity: 0.5; pointer-events: none; cursor: default;" data-value="${species}">${displayHtml} (Already Guessed)</li>`;
                } else {
                    listHTML += `<li class="autocomplete-item" data-value="${species}">${displayHtml}</li>`;
                }
            }
        });
        
        if (listHTML) {
            autocompleteList.innerHTML = listHTML;
            autocompleteList.classList.add('active');
            
            // Add click events to items
            const items = autocompleteList.getElementsByClassName('autocomplete-item');
            for (let i = 0; i < items.length; i++) {
                items[i].addEventListener('click', function(e) {
                    animalInput.value = this.getAttribute('data-value');
                    selectedSpecies = animalInput.value;
                    closeDropdown();
                });
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

    // Input Events
    animalInput.addEventListener('click', showDropdown);
    animalInput.addEventListener('input', showDropdown);
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function (e) {
        if (e.target !== animalInput && e.target !== autocompleteList) {
            closeDropdown();
        }
    });

    // Keyboard navigation for dropdown
    animalInput.addEventListener('keydown', function(e) {
        let x = autocompleteList.getElementsByClassName('autocomplete-item');
        if (e.keyCode == 40) { // Down
            currentFocus++;
            addActive(x);
        } else if (e.keyCode == 38) { // Up
            currentFocus--;
            addActive(x);
        } else if (e.keyCode == 13) { // Enter
            e.preventDefault();
            if (currentFocus > -1) {
                if (x) x[currentFocus].click();
            } else if (animalInput.value) {
                 handleGuess(); // If they typed something and hit enter without selecting
            }
        }
    });

    function addActive(x) {
        if (!x) return false;
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        x[currentFocus].classList.add('selected');
        // Scroll into view
        x[currentFocus].scrollIntoView({ block: 'nearest' });
    }

    function removeActive(x) {
        for (let i = 0; i < x.length; i++) {
            x[i].classList.remove('selected');
        }
    }

    // Handle Guessing
    async function handleGuess() {
        const guess = animalInput.value.trim();
        
        // Validate guess
        if (!guess) return;
        
        // Ensure valid species from our list
        const validGuess = allSpecies.find(s => s.toLowerCase() === guess.toLowerCase());
        
        if (!validGuess) {
            alert("Please select an organism from the list.");
            return;
        }

        const guessKey = validGuess.toLowerCase();
        
        if (guessedSet.has(guessKey)) {
            // Failsafe in case they hit enter on a disabled item
            alert("You already guessed that organism!");
            return;
        }
        
        guessedSet.add(guessKey);
        
        // Check if data exists for this guess
        if (!targetData[guessKey]) {
            alert("Error: No evolutionary data found for this comparison.");
            return;
        }

        const data = targetData[guessKey];
        const isMatch = guessKey === targetSpecies.toLowerCase();

        const latinNameMatch = validGuess.match(/\((.*?)\)/);
        const wikiTitle = latinNameMatch ? latinNameMatch[1] : validGuess;
        
        guesses.push({
            name: validGuess,
            wikiTitle: wikiTitle,
            lca_rank: data.rank,
            lca_name: data.lca_name || data.rank,
            tmrca: data.time,
            isMatch: isMatch
        });
        
        addGuessToBoard(validGuess, wikiTitle, data, isMatch);
        updateTree();
        
        // Clear input
        animalInput.value = '';
        selectedSpecies = '';
        closeDropdown();

        if (isMatch) {
            showGameOver(true);
        }
    }

    function addGuessToBoard(guessName, wikiTitle, data, isMatch) {
        const row = document.createElement('div');
        row.className = 'guess-row';
        
        let matchClass = isMatch ? 'match-exact' : '';
        
        // Format time (e.g. 50.5 Million Years Ago)
        const timeStr = data.time === 0 ? "Exact Match" : (data.time === -1.0 ? "Unknown (>500 MYA)" : `${data.time.toFixed(1)} MYA`);
        const lcaName = data.lca_name || data.rank;
        
        row.innerHTML = `
            <div class="guess-name ${matchClass} taxa-link">${guessName}</div>
            <div class="guess-feedback">
                <span class="feedback-badge feedback-time ${matchClass}" title="TMRCA = Time to Most Recent Common Ancestor">TMRCA: ${timeStr}</span>
                <span class="feedback-badge feedback-rank ${matchClass} taxa-link" data-taxa="${lcaName}">${data.rank}: ${lcaName}</span>
            </div>
        `;
        
        // Animal name link
        const nameSpan = row.querySelector('.guess-name');
        nameSpan.addEventListener('mouseenter', (e) => showWikiTooltip(e, wikiTitle));
        nameSpan.addEventListener('mouseleave', hideWikiTooltip);
        nameSpan.addEventListener('click', () => {
            window.open(`https://en.wikipedia.org/wiki/${encodeURIComponent(wikiTitle)}`, '_blank');
        });

        // Taxa link
        const taxaSpan = row.querySelector('.feedback-rank');
        taxaSpan.addEventListener('mouseenter', (e) => showWikiTooltip(e, lcaName));
        taxaSpan.addEventListener('mouseleave', hideWikiTooltip);
        taxaSpan.addEventListener('click', () => {
            window.open(`https://en.wikipedia.org/wiki/${encodeURIComponent(lcaName)}`, '_blank');
        });
        
        // Prepend to show newest at top
        guessesContainer.prepend(row);
    }

    function showGameOver(win) {
        endTitle.textContent = win ? "You found it!" : "Game Over";
        endTitle.style.color = win ? "var(--success-color)" : "var(--danger-color)";
        endMessage.innerHTML = `The organism was <strong>${targetSpecies}</strong>.`;
        
        // Hide inputs and show inline end panel
        animalInput.parentElement.style.display = 'none';
        guessBtn.style.display = 'none';
        giveUpBtn.style.display = 'none';
        
        gameEndPanel.classList.remove('hidden');
    }

    // Event Listeners
    guessBtn.addEventListener('click', handleGuess);
    giveUpBtn.addEventListener('click', () => showGameOver(false));
    
    playAgainBtn.addEventListener('click', () => {
        gameEndPanel.classList.add('hidden');
        animalInput.parentElement.style.display = 'block';
        guessBtn.style.display = 'block';
        giveUpBtn.style.display = 'block';
        
        guessesContainer.innerHTML = '';
        animalInput.value = '';
        guesses = [];
        guessedSet.clear();
        initGame();
    });

    // Start game
    initGame();

    // D3 Tree Rendering
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
            if (g.isMatch) return; // handled at the end
            
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
        const mysteryNode = { name: mysteryName, wikiTitle: mysteryWiki, isMystery: true };
        
        if (!root) {
            root = { name: sortedGuesses[0].lca_name || "LCA", isTrunk: true, children: [mysteryNode] };
        } else {
            prevLCA.children.push(mysteryNode);
        }
        
        // Ensure Animalia/Metazoa is always the absolute root
        if (root.name !== "Metazoa" && root.name !== "Animalia") {
            root = { name: "Animalia", isTrunk: true, children: [root] };
        }
        
        drawTree(root);
    }

    function drawTree(treeData) {
        const container = document.getElementById('tree-container');
        container.innerHTML = ''; // Clear previous
        
        const margin = {top: 40, right: 30, bottom: 40, left: 30};
        const width = container.clientWidth - margin.left - margin.right;
        const height = Math.max(500, container.clientHeight || 500, guesses.length * 80) - margin.top - margin.bottom;

        const svg = d3.select("#tree-container").append("svg")
            .attr("width", "100%")
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        const treeMap = d3.tree().size([width, height]);
        const nodes = d3.hierarchy(treeData, d => d.children);
        const treeNodes = treeMap(nodes);

        svg.selectAll(".link")
            .data(treeNodes.descendants().slice(1))
            .enter().append("path")
            .attr("class", "link")
            .attr("d", d => {
                return "M" + d.x + "," + d.y
                     + "C" + d.x + "," + (d.y + d.parent.y) / 2
                     + " " + d.parent.x + "," +  (d.y + d.parent.y) / 2
                     + " " + d.parent.x + "," + d.parent.y;
            });

        const node = svg.selectAll(".node")
            .data(treeNodes.descendants())
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", d => "translate(" + d.x + "," + d.y + ")");

        node.append("circle")
            .attr("r", 8)
            .style("fill", d => d.data.isMystery ? "var(--success-color)" : (d.data.isGuess ? "var(--warning-color)" : "var(--bg-primary)"));

        node.append("text")
            .attr("dy", ".35em")
            .attr("y", d => d.data.isTrunk ? -20 : 20)
            .style("text-anchor", "middle")
            .attr("class", "taxa-link")
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
    }
});
