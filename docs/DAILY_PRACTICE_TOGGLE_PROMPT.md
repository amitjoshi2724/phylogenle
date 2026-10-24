# Reusable Agent Prompt: Segmented Daily vs. Practice Mode Toggle & Persistence

Copy and paste the prompt below into the chat for your other games (e.g., Asteroidle, ElementSpeller, Spaceship-Flight):

---

```markdown
### Feature Request: Segmented Daily / Practice Mode Toggle with URL & LocalStorage Persistence

Please upgrade our game mode switching between "Daily" and "Practice" modes. The current single-button toggle is ambiguous (users can't tell whether the button represents the current mode or the action to switch to the other mode) and refreshing in practice mode unexpectedly resets back to daily.

Implement the following design and architecture:

---

### 1. Segmented Dual-Pill Toggle UI
Replace the single toggle button with a segmented control containing both modes side-by-side:

```html
<div class="mode-segmented-toggle" role="group" aria-label="Game Mode">
    <button type="button" id="mode-daily-btn" class="mode-toggle-btn active" data-mode="daily">
        <span class="mode-icon">📅</span> Daily
    </button>
    <button type="button" id="mode-practice-btn" class="mode-toggle-btn" data-mode="practice">
        <span class="mode-icon">🎯</span> Practice
    </button>
</div>
```

**CSS Styling Requirements**:
- Container: Rounded pill shape (`border-radius: 9999px` or `20px`), subtle glassmorphism/dark background (`rgba(255, 255, 255, 0.06)`), and a subtle border.
- Buttons: Seamless inline buttons inside the pill.
- **Active State (`.active`)**: Crisp, bright accent background (e.g., primary theme color, blue/green), high-contrast text, subtle glow/shadow (`box-shadow: 0 2px 8px rgba(0,0,0,0.3)`).
- **Inactive State**: Dimmed, transparent background, smooth hover transition.
- Responsive: Looks great on both desktop and mobile header navigation bars without causing layout shifts.

---

### 2. Dual Persistence Strategy (URL + LocalStorage)
Ensure that refreshing the page or sharing a link preserves the user's active mode:

1. **On App Boot / Initialization**:
   - Determine mode in priority order:
     1. URL query parameter: `new URLSearchParams(window.location.search).get('mode')` (if `'practice'`, set mode to practice; if `'daily'`, set mode to daily).
     2. `localStorage` key (e.g., `game_mode_preference`).
     3. Default to `'daily'`.
   - Update the UI toggle buttons so the correct button has `.active`.
   - Ensure the URL reflects the active mode (e.g., append `?mode=practice` when in practice mode via `window.history.replaceState` without triggering a reload).

2. **On Mode Switch**:
   - When the user clicks the other mode:
     - Update active class on the segmented toggle buttons.
     - Persist the selection to `localStorage.setItem('game_mode_preference', newMode)`.
     - Update the URL parameter using `window.history.replaceState({}, '', newUrl)`:
       - Practice: `?mode=practice`
       - Daily: clean URL without query or `?mode=daily`.
     - Switch the game session cleanly.

---

### 3. Session & State Isolation
- **Daily Mode**:
  - Bound to the deterministic target/puzzle for today's date.
  - Feeds into daily stats, streaks, win distribution, and daily completion modal.
  - In-progress guesses for today must be saved to a daily-specific storage key (e.g., `daily_state_YYYY-MM-DD`).
- **Practice Mode**:
  - Picks a random target from the pool.
  - Offers a "New Round" / "Play Again" button that generates a fresh random puzzle.
  - Stored in a separate practice storage key (e.g., `practice_state`) so it never pollutes or wipes out the user's daily puzzle streak.

---

### 4. Verification Checklist
Before completing, verify:
- [ ] Clicking "Practice" highlights Practice and dims Daily; URL updates to `?mode=practice`.
- [ ] Hard-refreshing the page while in Practice mode stays in Practice mode (does NOT revert to Daily).
- [ ] Switching back to Daily updates URL to clean root / `?mode=daily` and stays in Daily on refresh.
- [ ] Daily stats and streaks are isolated from unlimited Practice rounds.
- [ ] No layout squishing or visual glitches on mobile and desktop viewports.
```
