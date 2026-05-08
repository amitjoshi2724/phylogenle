document.addEventListener('DOMContentLoaded', () => {
    const animalInput = document.getElementById('animal-input');
    const autocompleteList = document.getElementById('autocomplete-list');
    const guessBtn = document.getElementById('guess-btn');
    const guessesContainer = document.getElementById('guesses-container');
    const gameOverModal = document.getElementById('game-over-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const playAgainBtn = document.getElementById('play-again-btn');

    let allSpecies = [];
    let targetSpecies = "";
    let targetData = {};
    let selectedSpecies = "";
    let currentFocus = -1;
    let guesses = [];

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
                listHTML += `<li class="autocomplete-item" data-value="${species}">${displayHtml}</li>`;
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
        
        // Check if data exists for this guess
        if (!targetData[guessKey]) {
            alert("Error: No evolutionary data found for this comparison.");
            return;
        }

        const data = targetData[guessKey];
        const isMatch = guessKey === targetSpecies.toLowerCase();
        
        guesses.push({
            name: validGuess,
            lca_rank: data.rank,
            lca_name: data.lca_name || data.rank,
            tmrca: data.time,
            isMatch: isMatch
        });
        
        addGuessToBoard(validGuess, data, isMatch);
        updateTree();
        
        // Clear input
        animalInput.value = '';
        selectedSpecies = '';
        closeDropdown();

        if (isMatch) {
            showGameOver(true);
        }
    }

    function addGuessToBoard(guessName, data, isMatch) {
        const row = document.createElement('div');
        row.className = 'guess-row';
        
        let matchClass = isMatch ? 'match-exact' : '';
        
        // Format time (e.g. 50.5 Million Years Ago)
        const timeStr = data.time === 0 ? "Exact Match" : (data.time === -1.0 ? "Unknown (>500 MYA)" : `${data.time.toFixed(1)} MYA`);
        const lcaName = data.lca_name || data.rank;
        
        row.innerHTML = `
            <div class="guess-name ${matchClass}">${guessName}</div>
            <div class="guess-feedback">
                <span class="feedback-badge feedback-time ${matchClass}" title="TMRCA = Time to Most Recent Common Ancestor">TMRCA: ${timeStr}</span>
                <span class="feedback-badge feedback-rank ${matchClass}">${data.rank}: ${lcaName}</span>
            </div>
        `;
        
        // Prepend to show newest at top
        guessesContainer.prepend(row);
    }

    function showGameOver(win) {
        modalTitle.textContent = win ? "You found it!" : "Game Over";
        modalTitle.style.color = win ? "var(--success-color)" : "var(--danger-color)";
        modalMessage.textContent = `The organism was ${targetSpecies}.`;
        gameOverModal.classList.remove('hidden');
    }

    // Event Listeners
    guessBtn.addEventListener('click', handleGuess);
    
    playAgainBtn.addEventListener('click', () => {
        gameOverModal.classList.add('hidden');
        guessesContainer.innerHTML = '';
        animalInput.value = '';
        guesses = [];
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
            
            const guessNode = { name: g.name, isGuess: true };
            
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
        const mysteryNode = { name: hasMatch ? targetSpecies : "?", isMystery: true };
        
        if (!root) {
            root = { name: sortedGuesses[0].lca_name || "LCA", isTrunk: true, children: [mysteryNode] };
        } else {
            prevLCA.children.push(mysteryNode);
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
            .text(d => d.data.name);
    }
});
