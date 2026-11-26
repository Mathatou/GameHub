import {
  getGame,
  getRandomGame,
  getLibrary,
  removeGameFromLib,
  addGameToLib
} from "./api.js";

import {
  lNotifications,
  dismissNotification,
  notify
} from "./notifications.js";

const { createApp, ref, computed } = Vue;
function describeGame(g) {
  return `${g.name} (${g.min_players}-${g.max_players} players, ` +
         `${g.playing_time} min, complexity ${g.complexity.toFixed(1)})`;
}


// Component: one game card with its button
const GameCard = {
  props: ["game", "inLibrary", "pending", "libraryReady"],
  emits: ["add", "remove"],
  computed: {
    label() {
      return describeGame(this.game);
    },
  },
  methods: {
    onClick() {
      if (this.pending || !this.libraryReady) return;
      if (this.inLibrary) {
        this.$emit("remove", this.game.id);
      } else {
        this.$emit("add", this.game.id);
      }
    },
  },
  template: `
    <li>
      <span>{{ label }}</span>
      <button :disabled="pending || !libraryReady" @click="onClick">
        {{ pending
          ? (inLibrary ? "Removing..." : "Adding...")
          : (!libraryReady ? "Loading library..." : (inLibrary ? "Remove" : "Add to library")) }}
      </button>
    </li>`,
};

createApp({
  components: { GameCard },
  setup() {
    // Interface state: when these change, the page updates by itself
    const players = ref("");
    const maxTime = ref("");
    const maxComplexity = ref("");
    const source = ref("catalog");

    const games = ref([]);
    const count = ref(null);
    const listSource = ref("catalog");   // source used for the displayed list
    const randomGame = ref(null);
    const noRandom = ref(false);
    const libraryIds = ref(new Set());
    const pendingIds = ref(new Set());
    const libraryReady = ref(false);

    const message = computed(() => {
      if (count.value === null) return "";
      const shown = games.value.length;
      return `${count.value} games found` +
             (count.value > shown ? ` (showing ${shown})` : "");
    });

    function operationErrorMessage(receipt, operation) {
      if (receipt.status === null) {
        return "Can't reach the server. Check that it is running and try again.";
      }

      const messages = {
        add: "The game could not be added. Please try again.",
        remove: "The game could not be removed. Please try again.",
        search: "The search failed. Please try again.",
        random: "Could not pick a random game. Please try again.",
      };
      return messages[operation] ?? "Something went wrong. Please try again.";
    }

    function setLibraryMembership(id, isInLibrary) {
      const updatedIds = new Set(libraryIds.value);
      if (isInLibrary) {
        updatedIds.add(id);
      } else {
        updatedIds.delete(id);
      }
      libraryIds.value = updatedIds;
    }

    function setPending(id, isPending) {
      const updatedIds = new Set(pendingIds.value);
      if (isPending) {
        updatedIds.add(id);
      } else {
        updatedIds.delete(id);
      }
      pendingIds.value = updatedIds;
    }

    function removeFromLibraryResults(id) {
      if (listSource.value !== "library") return;
      games.value = games.value.filter((game) => game.id !== id);
      if (count.value !== null) {
        count.value = Math.max(0, count.value - 1);
      }
    }

    async function loadLibrary() {
      const receipt = await getLibrary();
      if (!receipt.ok) {
        notify("Your library could not be loaded.", "error", true, {
          label: "Retry",
          action: loadLibrary,
        });
        return;
      }

      libraryIds.value = new Set(receipt.data.map((game) => game.id));
      libraryReady.value = true;
    }

    async function runNotificationAction(notification) {
      const action = notification.action;
      dismissNotification(notification.id);
      if (action) await action();
    }

    // Blank fields are simply not sent, so the backend ignores them
    function buildParams(usedSource) {
      const params = new URLSearchParams({ source: usedSource });
      const filled = (v) => v !== "" && v !== null;
      if (filled(players.value)) params.append("players", players.value);
      if (filled(maxTime.value)) params.append("max_time", maxTime.value);
      if (filled(maxComplexity.value)) params.append("max_complexity", maxComplexity.value);
      return params;
    }

    async function search() {
      const usedSource = source.value;
      randomGame.value = null;
      noRandom.value = false;
      const receipt = await getGame(buildParams(usedSource));
      if (!receipt.ok) {
        notify(operationErrorMessage(receipt, "search"), "error");
        return;
      }
      games.value = receipt.data.games;
      count.value = receipt.data.count;
      listSource.value = usedSource;
    }

    async function pickRandom() {
      randomGame.value = null;
      noRandom.value = false;
      const receipt = await getRandomGame(buildParams(source.value));
      if (!receipt.ok) {
        if (receipt.status === 404) {
          noRandom.value = true;
          return;
        }
        notify(operationErrorMessage(receipt, "random"), "error");
        return;
      }
      randomGame.value = receipt.data;
    }

    async function addGame(id) {
      if (pendingIds.value.has(id)) return;
      setPending(id, true);
      try {
        const receipt = await addGameToLib(id);
        if (receipt.ok || receipt.status === 409) {
          setLibraryMembership(id, true);
          return;
        }
        if (receipt.status === 404) {
          notify("This game could not be found in the catalog.", "error");
          return;
        }
        notify(operationErrorMessage(receipt, "add"), "error");
      } finally {
        setPending(id, false);
      }
    }

    async function removeGame(id) {
      if (pendingIds.value.has(id)) return;
      const gameName = games.value.find((game) => game.id === id)?.name ?? "Game";
      setPending(id, true);
      try {
        const receipt = await removeGameFromLib(id);
        if (receipt.ok || receipt.status === 404) {
          setLibraryMembership(id, false);
          removeFromLibraryResults(id);
          if (receipt.ok) {
            notify(`${gameName} removed from your library.`, "success");
          }
          return;
        }
        notify(operationErrorMessage(receipt, "remove"), "error");
      } finally {
        setPending(id, false);
      }
    }

    void loadLibrary();

    return {
      players, maxTime, maxComplexity, source,
      games, listSource, randomGame, noRandom, message,
      libraryIds, pendingIds, libraryReady,
      search, pickRandom, addGame, removeGame, describeGame,
      lNotifications, dismissNotification, runNotificationAction,
    };
  },
}).mount("#app");